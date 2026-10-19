"""Persistent live work, legacy migration and approval integration regressions."""
import copy
import json
import sqlite3
from uuid import uuid4
from unittest.mock import patch
import pytest
from trajectory import create_app, storage, work_storage
from test_goals import app
from test_generation import ready_goal, generate, fake_result, CONTENT
from test_review import draft_for as initial_draft_for, post_review, current


def draft_for(client, app, goal_url=None, content=None):
    if goal_url is None:
        return initial_draft_for(client, app, content=content)
    with app.app_context():
        revision = storage.find_goal(goal_url.split("/")[2])["revision"]
    result = fake_result()
    if content is not None:
        result = (result[0].validate_response(json.dumps(content)), result[1])
    request_id = str(uuid4())
    with patch("trajectory.ai.OllamaAdapter.generate", return_value=result):
        assert generate(client, goal_url, request_id, revision=str(revision)).status_code == 303
    return goal_url, request_id


def work_post(client, url, **values):
    page = client.get(url)
    assert page.status_code == 200
    with client.session_transaction() as state:
        token = state["csrf_token"]
    goal_id = url.split("/")[2]
    with client.application.app_context():
        revision = work_storage.revision(goal_id)
    return client.post(url, data={"csrf_token": token, "revision": revision, **values})


def work_rows(app, url):
    with app.app_context():
        goal_id = url.split("/")[2]
        return work_storage.milestones(goal_id), work_storage.tasks(goal_id)


def add_milestone(client, url, **changes):
    return work_post(client, url + "/work/milestones/new",
                     title="Ship demo", completion_criterion="A runnable demo exists", **changes)


def add_task(client, url, **changes):
    return work_post(client, url + "/work/tasks/new",
                     **{"title": "Write demo", "description": "Build the entry point.",
                        "estimated_minutes": "", "milestone_id": "", **changes})


def test_manual_work_without_ai_survives_restart_and_relink(app):
    client = app.test_client()
    url = ready_goal(client)
    assert add_milestone(client, url).status_code == 303
    milestones, _ = work_rows(app, url)
    milestone = milestones[0]
    assert add_task(client, url, milestone_id=milestone["id"]).status_code == 303
    _, tasks = work_rows(app, url)
    task = tasks[0]
    assert work_post(client, f'{url}/work/tasks/{task["id"]}/edit',
                     title="Rename demo", description="Changed description.",
                     estimated_minutes="45", milestone_id="").status_code == 303
    milestones, tasks = work_rows(app, url)
    assert tasks[0]["id"] == task["id"]
    assert tasks[0]["milestone_id"] is None and tasks[0]["estimated_minutes"] == 45
    assert work_post(client, f'{url}/work/milestones/{milestone["id"]}/edit',
                     title="Publish demo", completion_criterion="A demo is published").status_code == 303
    with app.app_context():
        assert work_storage.milestones(url.split("/")[2])[0]["id"] == milestone["id"]
    restarted = create_app(dict(app.config)).test_client()
    page = restarted.get(url + "/work")
    assert b"Rename demo" in page.data and b"Publish demo" in page.data
    assert b"45 minutes" in page.data
    assert b"Saved work" in page.data
    assert current(app, url) is None


def test_approved_work_edits_keep_ids_and_immutable_snapshots(app):
    client = app.test_client()
    url, draft = draft_for(client, app)
    assert post_review(client, url, draft).status_code == 303
    before = current(app, url)
    milestones, tasks = work_rows(app, url)
    task, milestone = tasks[0], milestones[0]
    assert work_post(client, f'{url}/work/tasks/{task["id"]}/edit',
                     title="Inspect carefully", description="Review data quality.",
                     estimated_minutes="60", milestone_id=milestone["id"]).status_code == 303
    assert work_post(client, f'{url}/work/milestones/{milestone["id"]}/edit',
                     title="Reliable baseline", completion_criterion="A reproducible result").status_code == 303
    _, second = draft_for(client, app, url)
    goal_id = url.split("/")[2]
    with app.app_context():
        goal_revision = storage.find_goal(goal_id)["revision"]
    assert goal_revision == 3
    assert post_review(client, url, second, expected_plan_id=before["id"]).status_code == 303
    after_milestones, after_tasks = work_rows(app, url)
    assert len(after_tasks) == 1 and after_tasks[0]["id"] == task["id"]
    assert after_tasks[0]["title"] == "Inspect carefully"
    assert after_milestones[0]["id"] == milestone["id"]
    assert after_milestones[0]["title"] == "Reliable baseline"
    with sqlite3.connect(app.config["DATABASE"]) as db:
        old_content = db.execute("SELECT content FROM approved_plans WHERE id=?", (before["id"],)).fetchone()[0]
        assert json.loads(old_content) == before["proposal"]
        assert db.execute("SELECT count(*) FROM approved_plan_tasks WHERE task_id=?", (task["id"],)).fetchone()[0] == 2


def test_replacement_preserves_manual_work_but_archives_removed_plan_work(app):
    client = app.test_client()
    url, first = draft_for(client, app)
    post_review(client, url, first)
    previous = current(app, url)
    old_milestone = work_rows(app, url)[0][0]["id"]
    assert add_task(client, url).status_code == 303
    changed = copy.deepcopy(CONTENT)
    changed["milestones"][0]["title"] = "New milestone"
    changed["milestones"][0]["tasks"][0]["title"] = "Different task"
    _, second = draft_for(client, app, url, changed)
    assert post_review(client, url, second, expected_plan_id=previous["id"]).status_code == 303
    milestones, tasks = work_rows(app, url)
    assert {t["title"] for t in tasks} == {"Write demo", "Different task"}
    assert old_milestone not in {m["id"] for m in milestones}
    with sqlite3.connect(app.config["DATABASE"]) as db:
        assert db.execute("SELECT count(*) FROM approved_tasks WHERE archived=1").fetchone()[0] == 1


def test_invalid_cross_goal_and_stale_edits_are_preserved_without_writes(app):
    client = app.test_client()
    url, other = ready_goal(client), ready_goal(client)
    add_milestone(client, other)
    foreign = work_rows(app, other)[0][0]["id"]
    response = add_task(client, url, title="Keep this", milestone_id=foreign)
    assert response.status_code == 422 and b"Keep this" in response.data
    assert work_rows(app, url)[1] == []
    assert client.get(f"{url}/work/milestones/{foreign}/edit").status_code == 404
    assert add_task(client, url).status_code == 303
    task = work_rows(app, url)[1][0]
    edit_url = f'{url}/work/tasks/{task["id"]}/edit'
    with app.app_context():
        stale_revision = work_storage.revision(url.split("/")[2])
    assert add_milestone(client, url).status_code == 303
    response = work_post(client, edit_url, title="Unsaved rename", description="Keep notes.",
                         estimated_minutes="30", milestone_id="", revision=stale_revision)
    assert response.status_code == 409 and b"Unsaved rename" in response.data
    assert work_rows(app, url)[1][0]["title"] == "Write demo"


@pytest.mark.parametrize("minutes", ["0", "-1", "1.5", "nan", "10081"])
def test_invalid_task_estimates_and_csrf(app, minutes):
    client = app.test_client()
    url = ready_goal(client)
    response = add_task(client, url, estimated_minutes=minutes)
    assert response.status_code == 422
    assert work_rows(app, url)[1] == []
    assert client.post(url + "/work/tasks/new", data={"title": "No token"}).status_code == 400


def test_manual_change_invalidates_pending_and_inflight_proposals(app):
    client = app.test_client()
    url, draft = draft_for(client, app)
    add_task(client, url)
    assert post_review(client, url, draft).status_code == 409
    assert b"Outdated draft" in client.get(url).data
    def change_work(context):
        from trajectory import work_service
        goal_id = url.split("/")[2]
        work_service.save(goal_id, "milestones", None, work_storage.revision(goal_id),
                          {"title": "During generation", "completion_criterion": "Saved work"})
        return fake_result()
    with patch("trajectory.ai.OllamaAdapter.generate", side_effect=change_work):
        response = generate(client, url, revision="2")
    assert response.status_code == 409 and b"response was discarded" in response.data


def test_approval_invalidates_an_open_manual_form(app):
    client = app.test_client()
    url, draft = draft_for(client, app)
    assert post_review(client, url, draft).status_code == 303
    response = work_post(client, url + "/work/tasks/new", revision="0",
                         title="Stale addition", description="Unsaved.", milestone_id="", estimated_minutes="")
    assert response.status_code == 409
    assert len(work_rows(app, url)[1]) == 1


def test_save_failure_rolls_back_task_link_and_revisions(app):
    client = app.test_client()
    url = ready_goal(client)
    with patch("trajectory.work_storage.bump_revision", side_effect=sqlite3.OperationalError):
        response = add_task(client, url, title="Keep this text")
    assert response.status_code == 503 and b"Keep this text" in response.data
    assert work_rows(app, url)[1] == []
    with app.app_context():
        assert work_storage.revision(url.split("/")[2]) == 0
        assert storage.find_goal(url.split("/")[2])["revision"] == 1


def test_untrusted_text_is_escaped_and_extra_fields_rejected(app):
    client = app.test_client()
    url = ready_goal(client)
    assert add_task(client, url, title="<script>oops</script>").status_code == 303
    page = client.get(url + "/work")
    assert b"<script>oops</script>" not in page.data and b"&lt;script&gt;" in page.data
    assert add_task(client, url, accepted="true").status_code == 422


def legacy_database(tmp_path):
    from trajectory.draft_storage import SCHEMA as DRAFT_SCHEMA
    from trajectory.review_storage import SCHEMA as REVIEW_SCHEMA
    database = str(tmp_path / "legacy.sqlite")
    with sqlite3.connect(database) as db:
        db.executescript(storage.SCHEMA + DRAFT_SCHEMA + REVIEW_SCHEMA)
        db.execute("INSERT INTO goals(id,title,description) VALUES ('goal','Legacy goal','Keep this')")
        for plan, draft, status in [("p1", "d1", "superseded"), ("p2", "d2", "current")]:
            db.execute("INSERT INTO plan_drafts(id,goal_id,source_revision,content,provenance) VALUES (?,'goal',1,?,'{}')",
                       (draft, json.dumps(CONTENT)))
            db.execute("""INSERT INTO approved_plans
                       (id,goal_id,draft_id,draft_revision,source_revision,content,provenance,status)
                       VALUES (?,'goal',?,1,1,?,'{}',?)""", (plan, draft, json.dumps(CONTENT), status))
        task = CONTENT["milestones"][0]["tasks"][0]
        db.execute("INSERT INTO approved_tasks VALUES ('task','goal',?,?,?,0)",
                   (task["title"], task["description"], task["estimated_minutes"]))
        db.executemany("INSERT INTO approved_plan_tasks VALUES (?,'task',0,0)", [("p1",), ("p2",)])
    return database


def test_legacy_backfill_is_repeatable_preserves_ids_history_and_foreign_keys(tmp_path):
    database = legacy_database(tmp_path)
    config = {"TESTING": True, "DATABASE": database}
    migrated = create_app(config)
    with migrated.app_context():
        milestones = work_storage.milestones("goal")
        task = work_storage.tasks("goal")[0]
        assert task["id"] == "task" and task["milestone_id"] == milestones[0]["id"]
        assert storage.get_db().execute("PRAGMA foreign_keys").fetchone()[0] == 1
    create_app(config)
    with sqlite3.connect(database) as db:
        assert db.execute("SELECT count(*) FROM work_milestones").fetchone()[0] == 1
        assert db.execute("SELECT count(*) FROM approved_plan_milestones").fetchone()[0] == 2
        assert db.execute("SELECT count(*) FROM approved_plan_tasks").fetchone()[0] == 2
        assert db.execute("SELECT content FROM approved_plans WHERE id='p1'").fetchone()[0] == json.dumps(CONTENT)
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []


def test_failed_legacy_migration_rolls_back_and_can_retry(tmp_path):
    database = legacy_database(tmp_path)
    config = {"TESTING": True, "DATABASE": database}
    with patch("trajectory.work_storage.import_milestones", side_effect=sqlite3.OperationalError):
        with pytest.raises(sqlite3.OperationalError):
            create_app(config)
    with sqlite3.connect(database) as db:
        assert db.execute("SELECT count(*) FROM approved_tasks").fetchone()[0] == 1
        assert db.execute("SELECT name FROM sqlite_master WHERE name='work_schema_migrations'").fetchone() is None
    assert create_app(config).test_client().get("/goals/goal/work").status_code == 200

def test_late_approval_failure_restores_live_work_and_snapshot(app):
    client = app.test_client()
    url, first = draft_for(client, app)
    assert post_review(client, url, first).status_code == 303
    previous = current(app, url)
    before = work_rows(app, url)
    changed = copy.deepcopy(CONTENT)
    changed["milestones"][0]["title"] = "Replacement milestone"
    changed["milestones"][0]["tasks"][0]["title"] = "Replacement task"
    _, second = draft_for(client, app, url, changed)
    with patch("trajectory.work_storage.bump_revision", side_effect=sqlite3.OperationalError):
        response = post_review(client, url, second, expected_plan_id=previous["id"])
    assert response.status_code == 503
    assert current(app, url)["id"] == previous["id"]
    assert work_rows(app, url) == before
    with sqlite3.connect(app.config["DATABASE"]) as db:
        assert db.execute("SELECT count(*) FROM approved_plans").fetchone()[0] == 1
        assert db.execute("SELECT count(*) FROM work_milestones").fetchone()[0] == 1
        assert db.execute("SELECT count(*) FROM approved_plan_tasks").fetchone()[0] == 1
        assert db.execute("SELECT count(*) FROM approved_tasks").fetchone()[0] == 1


def test_moving_task_between_milestones_preserves_identity(app):
    client = app.test_client()
    url = ready_goal(client)
    add_milestone(client, url)
    add_milestone(client, url)
    milestones, _ = work_rows(app, url)
    assert add_task(client, url, milestone_id=milestones[0]["id"]).status_code == 303
    task = work_rows(app, url)[1][0]
    assert work_post(client, f'{url}/work/tasks/{task["id"]}/edit',
                     title=task["title"], description=task["description"],
                     estimated_minutes="", milestone_id=milestones[1]["id"]).status_code == 303
    moved = work_rows(app, url)[1][0]
    assert moved["id"] == task["id"] and moved["milestone_id"] == milestones[1]["id"]
    assert moved["estimated_minutes"] is None


def test_legacy_backfill_keeps_removed_work_archived(tmp_path):
    database = legacy_database(tmp_path)
    changed = copy.deepcopy(CONTENT)
    changed["milestones"][0]["title"] = "Current milestone"
    changed["milestones"][0]["tasks"][0]["title"] = "Current task"
    with sqlite3.connect(database) as db:
        db.execute("UPDATE approved_tasks SET archived=1 WHERE id='task'")
        db.execute("INSERT INTO approved_tasks VALUES ('new-task','goal','Current task','Current description',20,0)")
        db.execute("UPDATE approved_plan_tasks SET task_id='new-task' WHERE plan_id='p2'")
        db.execute("UPDATE approved_plans SET content=? WHERE id='p2'", (json.dumps(changed),))
    migrated = create_app({"TESTING": True, "DATABASE": database})
    with migrated.app_context():
        tasks = work_storage.tasks("goal")
        milestones = work_storage.milestones("goal")
        assert len(tasks) == len(milestones) == 1
        assert tasks[0]["id"] == "new-task"
        assert milestones[0]["title"] == "Current milestone"
    with sqlite3.connect(database) as db:
        assert db.execute("SELECT archived FROM approved_tasks WHERE id='task'").fetchone()[0] == 1
        assert db.execute("SELECT count(*) FROM work_task_links").fetchone()[0] == 2
        assert db.execute("SELECT count(*) FROM approved_plan_milestones").fetchone()[0] == 2
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
