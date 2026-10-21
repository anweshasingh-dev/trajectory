"""Actual-work behavior through HTTP and restartable SQLite storage."""
import copy
from datetime import date, timedelta
import re
import sqlite3
from unittest.mock import patch
import pytest
from trajectory import create_app, progress_storage, progress_service
from test_goals import app
from test_generation import ready_goal, CONTENT
from test_review import post_review, current
from test_work import add_milestone, add_task, work_rows, draft_for


@pytest.fixture(autouse=True)
def enable_legacy_progress_for_regressions(app):
    """Retain legacy behavior coverage while the current UI defaults to hidden."""
    app.config["LEGACY_PROGRESS_UI"] = True


def task_url(goal_url, task_id):
    return f"{goal_url}/tasks/{task_id}"


def new_entry(client, goal_url, task_id, **changes):
    url = task_url(goal_url, task_id) + "/entries/new"
    page = client.get(url)
    assert page.status_code == 200
    with client.session_transaction() as state:
        token = state["csrf_token"]
    request_id = re.search(rb'name="request_id" value="([^"]+)"', page.data).group(1).decode()
    revision = re.search(rb'name="revision" value="([^"]+)"', page.data).group(1).decode()
    values = {
        "csrf_token": token, "request_id": request_id, "revision": revision,
        "work_date": date.today().isoformat(), "outcome": "partial",
        "actual_minutes": "", "notes": "", "blocker_action": "none", "blocker_text": "",
    }
    values.update(changes)
    return client.post(url, data=values), values


def entry_rows(app, task_id):
    with app.app_context():
        return progress_storage.entries_for_task(task_id)


def edit_entry(client, goal_url, task_id, entry_id, **changes):
    url = task_url(goal_url, task_id) + f"/entries/{entry_id}/edit"
    page = client.get(url)
    assert page.status_code == 200
    with client.session_transaction() as state:
        token = state["csrf_token"]
    entry = next(row for row in entry_rows(client.application, task_id) if row["id"] == entry_id)
    values = {
        "csrf_token": token, "revision": entry["revision"], "request_id": "",
        "work_date": entry["work_date"], "outcome": entry["outcome"],
        "actual_minutes": "" if entry["actual_minutes"] is None else entry["actual_minutes"],
        "notes": entry["notes"], "blocker_action": entry["blocker_action"],
        "blocker_text": entry["blocker_text"],
    }
    values.update(changes)
    return client.post(url, data=values)


def remove_entry(client, goal_url, task_id, entry_id, revision, confirmed="on"):
    client.get(task_url(goal_url, task_id) + "/progress")
    with client.session_transaction() as state:
        token = state["csrf_token"]
    return client.post(task_url(goal_url, task_id) + f"/entries/{entry_id}/delete",
                       data={"csrf_token": token, "revision": revision, "confirmed": confirmed})


def test_partial_blocker_time_and_milestone_count_survive_restart(app):
    client = app.test_client()
    url = ready_goal(client)
    assert add_milestone(client, url).status_code == 303
    milestone = work_rows(app, url)[0][0]
    assert add_task(client, url, milestone_id=milestone["id"]).status_code == 303
    task_id = work_rows(app, url)[1][0]["id"]
    result, _ = new_entry(client, url, task_id, actual_minutes="35",
                          notes="Reviewed the data", blocker_action="raised",
                          blocker_text="Need sample records")
    assert result.status_code == 303
    page = client.get(url + "/work")
    assert b"In progress" in page.data
    assert b"35 minutes recorded" in page.data
    assert b"Need sample records" in page.data
    assert b"0 of 1 tasks completed" in page.data
    restarted = create_app(dict(app.config)).test_client()
    detail = restarted.get(task_url(url, task_id) + "/progress")
    assert b"Reviewed the data" in detail.data and b"Need sample records" in detail.data
    assert b"35 minutes" in detail.data
    with app.app_context():
        assert progress_service.fold_entries(progress_storage.entries_for_task(task_id))["status"] == "in_progress"


def test_completion_reopening_and_blocker_only_entry(app):
    client = app.test_client()
    url = ready_goal(client)
    add_milestone(client, url)
    milestone = work_rows(app, url)[0][0]
    add_task(client, url, milestone_id=milestone["id"])
    task_id = work_rows(app, url)[1][0]["id"]
    assert new_entry(client, url, task_id, actual_minutes="0",
                     blocker_action="raised", blocker_text="Waiting for access")[0].status_code == 303
    assert b"Waiting for access" in client.get(url + "/work").data
    assert new_entry(client, url, task_id, outcome="completed")[0].status_code == 303
    page = client.get(url + "/work")
    assert b"1 of 1 tasks completed" in page.data
    assert b"Waiting for access" not in page.data
    assert b"0 minutes recorded" in page.data
    assert new_entry(client, url, task_id, outcome="reopened")[0].status_code == 303
    page = client.get(url + "/work")
    assert b"0 of 1 tasks completed" in page.data
    assert b"To do" in page.data
    assert b"Reopen task" not in page.data


def test_correction_and_removal_recompute_status_time_and_blocker(app):
    client = app.test_client()
    url = ready_goal(client)
    add_task(client, url)
    task_id = work_rows(app, url)[1][0]["id"]
    new_entry(client, url, task_id, actual_minutes="30", notes="Started",
              blocker_action="raised", blocker_text="Waiting")
    first_id = entry_rows(app, task_id)[0]["id"]
    new_entry(client, url, task_id, outcome="completed", actual_minutes="10")
    second_id = entry_rows(app, task_id)[1]["id"]
    assert edit_entry(client, url, task_id, first_id, actual_minutes="45").status_code == 303
    page = client.get(task_url(url, task_id) + "/progress")
    assert b"55 minutes" in page.data
    assert b"Current blocker" not in page.data
    assert remove_entry(client, url, task_id, second_id, 1).status_code == 303
    page = client.get(task_url(url, task_id) + "/progress")
    assert b"In progress" in page.data and b"45 minutes" in page.data
    assert b"Current blocker" in page.data
    assert edit_entry(client, url, task_id, first_id,
                      blocker_action="cleared", blocker_text="").status_code == 303
    page = client.get(task_url(url, task_id) + "/progress")
    assert b"Current blocker" not in page.data
    assert remove_entry(client, url, task_id, first_id, 3).status_code == 303
    assert b"No time recorded" in client.get(task_url(url, task_id) + "/progress").data
    assert entry_rows(app, task_id) == []


def test_backdated_correction_changes_current_status(app):
    client = app.test_client()
    url = ready_goal(client)
    add_task(client, url)
    task_id = work_rows(app, url)[1][0]["id"]
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    new_entry(client, url, task_id, outcome="completed", work_date=yesterday)
    completed_id = entry_rows(app, task_id)[0]["id"]
    new_entry(client, url, task_id, outcome="partial", notes="More work found")
    with app.app_context():
        assert progress_service.fold_entries(progress_storage.entries_for_task(task_id))["status"] == "in_progress"
    assert edit_entry(client, url, task_id, completed_id,
                      work_date=date.today().isoformat()).status_code == 303
    with app.app_context():
        assert progress_service.fold_entries(progress_storage.entries_for_task(task_id))["status"] == "in_progress"
    # Moving the later partial record to yesterday makes completion the latest event.
    partial_id = next(row["id"] for row in entry_rows(app, task_id) if row["outcome"] == "partial")
    assert edit_entry(client, url, task_id, partial_id, work_date=yesterday).status_code == 303
    with app.app_context():
        assert progress_service.fold_entries(progress_storage.entries_for_task(task_id))["status"] == "completed"


@pytest.mark.parametrize("changes", [
    {}, {"actual_minutes": "-1"}, {"actual_minutes": "1.5"},
    {"actual_minutes": "nan"}, {"actual_minutes": "1441"},
    {"work_date": "2026-02-30", "notes": "invalid"},
    {"work_date": (date.today() + timedelta(days=1)).isoformat(), "notes": "future"},
    {"blocker_action": "raised"}, {"outcome": "completed", "blocker_action": "raised", "blocker_text": "Wait"},
])
def test_invalid_entries_preserve_form_and_database(app, changes):
    client = app.test_client()
    url = ready_goal(client)
    add_task(client, url)
    task_id = work_rows(app, url)[1][0]["id"]
    response, _ = new_entry(client, url, task_id, **changes)
    assert response.status_code == 422
    assert b"Unsaved" in response.data
    assert entry_rows(app, task_id) == []


def test_duplicate_submission_is_idempotent_and_stale_correction_rejected(app):
    client = app.test_client()
    url = ready_goal(client)
    add_task(client, url)
    task_id = work_rows(app, url)[1][0]["id"]
    result, values = new_entry(client, url, task_id, notes="Started")
    assert result.status_code == 303
    same = client.post(task_url(url, task_id) + "/entries/new", data=values)
    assert same.status_code == 303
    assert len(entry_rows(app, task_id)) == 1
    entry_id = entry_rows(app, task_id)[0]["id"]
    assert edit_entry(client, url, task_id, entry_id, notes="Corrected").status_code == 303
    stale = edit_entry(client, url, task_id, entry_id, notes="Old form", revision="1")
    assert stale.status_code == 409 and b"Old form" in stale.data
    assert entry_rows(app, task_id)[0]["notes"] == "Corrected"


def test_csrf_confirmation_and_cross_goal_references(app):
    client = app.test_client()
    first, second = ready_goal(client), ready_goal(client)
    add_task(client, first)
    add_task(client, second)
    task_a = work_rows(app, first)[1][0]["id"]
    task_b = work_rows(app, second)[1][0]["id"]
    assert client.post(task_url(first, task_a) + "/entries/new").status_code == 400
    assert client.get(task_url(second, task_a) + "/progress").status_code == 404
    new_entry(client, first, task_a, notes="Work")
    entry_id = entry_rows(app, task_a)[0]["id"]
    assert client.get(task_url(second, task_b) + f"/entries/{entry_id}/edit").status_code == 404
    assert remove_entry(client, first, task_a, entry_id, 1, confirmed="").status_code == 409
    assert len(entry_rows(app, task_a)) == 1
    assert remove_entry(client, second, task_b, entry_id, 1).status_code == 409
    assert len(entry_rows(app, task_a)) == 1


def test_failed_write_rolls_back_entry_and_revision(app):
    client = app.test_client()
    url = ready_goal(client)
    add_task(client, url)
    task_id = work_rows(app, url)[1][0]["id"]
    with patch("trajectory.progress_service.work_storage.bump_revision",
               side_effect=sqlite3.OperationalError):
        response, _ = new_entry(client, url, task_id, notes="Keep this note")
    assert response.status_code == 503 and b"Keep this note" in response.data
    assert entry_rows(app, task_id) == []
    result, _ = new_entry(client, url, task_id, notes="Saved")
    assert result.status_code == 303
    entry_id = entry_rows(app, task_id)[0]["id"]
    with patch("trajectory.progress_service.work_storage.bump_revision",
               side_effect=sqlite3.OperationalError):
        response = edit_entry(client, url, task_id, entry_id, notes="Unsaved correction")
    assert response.status_code == 503 and b"Unsaved correction" in response.data
    assert entry_rows(app, task_id)[0]["notes"] == "Saved"
    with patch("trajectory.progress_service.work_storage.bump_revision",
               side_effect=sqlite3.OperationalError):
        response = remove_entry(client, url, task_id, entry_id, 1)
    assert response.status_code == 503
    assert len(entry_rows(app, task_id)) == 1


def test_archived_task_history_survives_replacement_and_is_correctable(app):
    client = app.test_client()
    url, first = draft_for(client, app)
    assert post_review(client, url, first).status_code == 303
    task_id = work_rows(app, url)[1][0]["id"]
    new_entry(client, url, task_id, actual_minutes="20")
    old_plan = current(app, url)
    changed = copy.deepcopy(CONTENT)
    changed["milestones"][0]["tasks"][0]["title"] = "Different work"
    _, second = draft_for(client, app, url, changed)
    assert post_review(client, url, second, expected_plan_id=old_plan["id"]).status_code == 303
    assert all(row["id"] != task_id for row in work_rows(app, url)[1])
    page = client.get(url + "/work")
    assert b"Archived tasks" in page.data and b"Inspect the data" in page.data
    history = client.get(task_url(url, task_id) + "/progress")
    assert history.status_code == 200 and b"20 minutes" in history.data
    assert client.get(task_url(url, task_id) + "/entries/new").status_code == 409
    entry_id = entry_rows(app, task_id)[0]["id"]
    assert edit_entry(client, url, task_id, entry_id, actual_minutes="25").status_code == 303
    assert b"25 minutes" in client.get(task_url(url, task_id) + "/progress").data
    restarted = create_app(dict(app.config)).test_client()
    assert b"25 minutes" in restarted.get(task_url(url, task_id) + "/progress").data


def test_progress_schema_migrates_existing_database_once(app):
    with sqlite3.connect(app.config["DATABASE"]) as db:
        assert db.execute("SELECT version FROM work_schema_migrations WHERE version IN (1,2) ORDER BY version").fetchall() == [(1,), (2,)]
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
    create_app(dict(app.config))
    with sqlite3.connect(app.config["DATABASE"]) as db:
        assert db.execute("SELECT count(*) FROM work_schema_migrations WHERE version IN (1,2)").fetchone()[0] == 2


def test_rendered_notes_are_escaped(app):
    client = app.test_client()
    url = ready_goal(client)
    add_task(client, url)
    task_id = work_rows(app, url)[1][0]["id"]
    assert new_entry(client, url, task_id, notes="<script>alert(1)</script>")[0].status_code == 303
    page = client.get(task_url(url, task_id) + "/progress")
    assert b"<script>alert(1)</script>" not in page.data
    assert b"&lt;script&gt;" in page.data
