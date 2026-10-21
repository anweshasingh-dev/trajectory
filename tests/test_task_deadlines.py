"""Task Master Part 2: calendar deadlines, explicit completion and safe upgrades."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
import sqlite3
from unittest.mock import patch

import pytest
from werkzeug.datastructures import MultiDict

from trajectory import create_app, storage, task_service, task_storage
from trajectory.task_deadlines import due_date
from test_goals import app
from test_task_master import create, post, rows
from test_task_storage import existing_database, old_work


def create_on(client, local_time, **changes):
    with patch("trajectory.task_storage.datetime", wraps=datetime) as clock:
        clock.now.return_value = datetime.fromisoformat(local_time).astimezone()
        return create(client, **changes)


def change_status(client, task, status="done", **changes):
    return post(client, f'/tasks/{task["id"]}/status',
                **{"status": status, "revision": str(task["revision"]), **changes})


@pytest.mark.parametrize("choice,days,expected", [
    ("none", None, None), ("2", 2, "2026-10-23"),
    ("4", 4, "2026-10-25"), ("7", 7, "2026-10-28"),
])
def test_all_deadline_choices_survive_restart(app, choice, days, expected):
    client = app.test_client()
    assert create_on(client, "2026-10-21T23:59:59", deadline=choice).status_code == 303
    task = rows(app)[0]
    assert task["deadline_days"] == days and task["created_on"] == "2026-10-21"
    assert due_date(task["created_on"], task["deadline_days"]) == expected
    assert task["created_at"] == task["updated_at"]
    restarted = create_app(dict(app.config))
    assert rows(restarted) == [task]
    page = restarted.test_client().get("/tasks").data
    assert (expected.encode() if expected else b"No deadline") in page
    form = restarted.test_client().get(f'/tasks/{task["id"]}/edit').data
    assert f'value="{choice}" selected'.encode() in form


def test_form_has_exactly_four_choices_and_safe_default(app):
    client = app.test_client()
    page = client.get("/tasks/new").data
    for choice, label in (("none", "No deadline"), ("2", "2 days"),
                          ("4", "4 days"), ("7", "1 week")):
        assert f'<option value="{choice}"'.encode() in page
        assert label.encode() in page
    assert page.count(b"<option ") == 4
    assert b'value="none" selected' in page
    assert create(client).status_code == 303
    assert rows(app)[0]["deadline_days"] is None


@pytest.mark.parametrize("invalid", ["", "3", "2 days", "1 week", "2.0", "-2",
                                     "0", "8", "2026-10-23", "null"])
def test_invalid_deadline_preserves_input_and_existing_task(app, invalid):
    client = app.test_client()
    assert create(client, deadline=invalid).status_code == 422
    assert rows(app) == []
    create(client, deadline="4")
    before = rows(app)[0]
    response = post(client, f'/tasks/{before["id"]}/edit',
                    title="Keep these edits", description="Keep these notes",
                    deadline=invalid, revision="1")
    assert response.status_code == 422
    assert b"Keep these edits" in response.data and b"Keep these notes" in response.data
    assert b'id="deadline-error"' in response.data
    assert rows(app) == [before]


@pytest.mark.parametrize("injected", [
    {"created_on": "2020-01-01"}, {"due_on": "2099-01-01"}, {"deadline_days": "2"},
])
def test_server_owns_deadline_anchor_and_encoding(app, injected):
    assert create(app.test_client(), **injected).status_code == 422
    assert rows(app) == []


def test_midnight_does_not_mean_elapsed_hours_or_utc_date(app):
    client = app.test_client()
    create_on(client, "2026-10-21T23:59:59", title="Before midnight", deadline="2")
    create_on(client, "2026-10-22T00:00:01", title="After midnight", deadline="2")
    tasks = {task["title"]: task for task in rows(app)}
    assert tasks["Before midnight"]["created_on"] == "2026-10-21"
    assert tasks["After midnight"]["created_on"] == "2026-10-22"
    assert due_date(tasks["Before midnight"]["created_on"], 2) == "2026-10-23"
    assert due_date(tasks["After midnight"]["created_on"], 2) == "2026-10-24"
    expected_utc = datetime(2026, 10, 22, 0, 0, 1).astimezone().astimezone(
        timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    assert tasks["After midnight"]["created_at"] == expected_utc


@pytest.mark.parametrize("created,days,expected", [
    ("2026-01-30", 2, "2026-02-01"), ("2026-12-30", 4, "2027-01-03"),
    ("2028-02-27", 2, "2028-02-29"), ("2026-02-27", 2, "2026-03-01"),
    ("2026-03-07", 2, "2026-03-09"), ("2026-10-31", 2, "2026-11-02"),
])
def test_calendar_arithmetic_across_months_leap_year_and_dst_dates(created, days, expected):
    assert due_date(created, days) == expected


def test_explicit_deadline_edits_always_use_original_creation_day(app):
    client = app.test_client()
    create_on(client, "2026-10-21T23:59:59", deadline="2")
    original = rows(app)[0]
    url = f'/tasks/{original["id"]}/edit'
    with patch("trajectory.task_routes.date", wraps=date) as clock:
        clock.today.return_value = date(2026, 11, 1)
        assert post(client, url, title="Rename only", revision="1").status_code == 303
        assert rows(app)[0]["deadline_days"] == 2
        assert post(client, url, title="Extend explicitly", deadline="7", revision="2").status_code == 303
        assert b"2026-10-28" in client.get("/tasks").data
        assert post(client, url, title="Remove deadline", deadline="none", revision="3").status_code == 303
        assert rows(app)[0]["deadline_days"] is None
        assert post(client, url, title="Restore deadline", deadline="4", revision="4").status_code == 303
        assert b"2026-10-25" in client.get("/tasks").data
    saved = rows(app)[0]
    assert saved["created_on"] == original["created_on"]
    assert saved["created_at"] == original["created_at"] and saved["id"] == original["id"]


def test_due_day_overdue_done_and_no_deadline_display_without_writes(app):
    client = app.test_client()
    create_on(client, "2026-10-21T12:00:00", deadline="2")
    task = rows(app)[0]
    with patch("trajectory.task_routes.date", wraps=date) as clock:
        clock.today.return_value = date(2026, 10, 22)
        assert b"Due today" not in client.get("/tasks").data
        clock.today.return_value = date(2026, 10, 23)
        page = client.get("/tasks").data
        assert b"Due today" in page and b"Overdue" not in page
        clock.today.return_value = date(2026, 10, 24)
        assert b"Overdue" in client.get("/tasks").data
        assert rows(app) == [task]
        assert change_status(client, task).status_code == 303
        page = client.get("/tasks").data
        assert b"Overdue" not in page and b"2026-10-23" in page
        assert change_status(client, rows(app)[0], "undone").status_code == 303
        assert b"Overdue" in client.get("/tasks").data
    create(client, title="No date")
    assert b"No deadline" in client.get("/tasks").data


def test_done_undone_identity_deadline_and_notes_survive_day_change_and_restart(app):
    client = app.test_client()
    create_on(client, "2026-10-21T12:00:00", deadline="4", description="Keep notes")
    original = rows(app)[0]
    response = change_status(client, original)
    assert response.status_code == 303
    page = client.get(response.location).data
    assert b"Task marked done." in page and b"Mark undone" in page
    done = rows(app)[0]
    assert done["status"] == "done" and done["revision"] == 2
    for field in ("id", "created_on", "created_at", "deadline_days", "title", "description"):
        assert done[field] == original[field]
    restarted = create_app(dict(app.config))
    with patch("trajectory.task_routes.date", wraps=date) as clock:
        clock.today.return_value = date(2027, 1, 10)
        assert b"Mark undone" in restarted.test_client().get("/tasks").data
        assert rows(restarted) == [done]
    client = restarted.test_client()
    assert change_status(client, done, "undone").status_code == 303
    undone = rows(restarted)[0]
    assert undone["status"] == "undone" and undone["revision"] == 3
    assert rows(create_app(dict(app.config))) == [undone]


def test_duplicate_desired_state_is_not_a_toggle_and_fresh_noop_does_not_write(app):
    client = app.test_client()
    create(client, deadline="2")
    task = rows(app)[0]
    assert change_status(client, task, "undone").status_code == 303
    assert rows(app) == [task]
    assert change_status(client, task).status_code == 303
    done = rows(app)[0]
    assert change_status(client, task).status_code == 409
    assert change_status(client, done).status_code == 303
    assert rows(app) == [done]


def test_status_change_invalidates_stale_edit_and_delete_and_deleted_task_stays_absent(app):
    client = app.test_client()
    create(client, deadline="2")
    task = rows(app)[0]
    assert change_status(client, task).status_code == 303
    assert post(client, f'/tasks/{task["id"]}/edit', title="Stale",
                deadline="7", revision="1").status_code == 409
    assert post(client, f'/tasks/{task["id"]}/delete',
                confirmed="on", revision="1").status_code == 409
    done = rows(app)[0]
    assert done["status"] == "done" and done["deadline_days"] == 2
    assert post(client, f'/tasks/{task["id"]}/delete',
                confirmed="on", revision="2").status_code == 303
    response = change_status(client, done, "undone")
    assert response.status_code == 409 and b"deleted" in response.data
    assert rows(app) == []


@pytest.mark.parametrize("changes", [
    {"status": ""}, {"status": "completed"}, {"status": "toggle"}, {"status": "DONE"},
    {"revision": ""}, {"revision": "0"}, {"revision": "1.5"}, {"revision": "9223372036854775808"},
    {"title": "Injected"}, {"deadline": "7"},
])
def test_status_request_validation_preserves_data(app, changes):
    client = app.test_client()
    create(client)
    task = rows(app)[0]
    assert change_status(client, task, **changes).status_code == 422
    assert rows(app) == [task]


def test_status_requires_csrf_post_single_fields_and_no_goal_task_access(app):
    client = app.test_client()
    create(client)
    task = rows(app)[0]
    url = f'/tasks/{task["id"]}/status'
    assert client.get(url).status_code == 405
    assert client.put(url).status_code == 405
    assert client.post(url, data={"status": "done", "revision": "1"}).status_code == 400
    with client.session_transaction() as session:
        token = session["csrf_token"]
    for field, value in (("status", "done"), ("revision", "1"), ("deadline", "2")):
        entries = [("csrf_token", token), ("status", "done"), ("revision", "1"),
                   (field, value)]
        if field == "deadline":
            entries.append((field, "4"))
        assert client.post(url, data=MultiDict(entries)).status_code == 422
    assert post(client, url, revision="1").status_code == 422
    assert post(client, "/tasks/task/status", status="done", revision="1").status_code == 409
    assert rows(app) == [task]


def test_status_and_deadline_failure_after_write_roll_back_and_allow_retry(app):
    client = app.test_client()
    create(client, deadline="2")
    task = rows(app)[0]
    update = task_storage.update_status
    def fail_after_write(*args):
        update(*args)
        raise sqlite3.OperationalError("synthetic failure")
    with patch("trajectory.task_storage.update_status", side_effect=fail_after_write):
        response = change_status(client, task)
    assert response.status_code == 503 and b"did not save" in response.data
    assert rows(app) == [task] and b"Mark done" in response.data
    update_task = task_storage.update_task
    def fail_edit(*args):
        update_task(*args)
        raise sqlite3.OperationalError("synthetic failure")
    with patch("trajectory.task_storage.update_task", side_effect=fail_edit):
        response = post(client, f'/tasks/{task["id"]}/edit',
                        title="Retry this", deadline="7", revision="1")
    assert response.status_code == 503 and b'value="7" selected' in response.data
    assert rows(app) == [task]
    assert change_status(client, task).status_code == 303


def test_concurrent_edit_and_status_have_one_winner(app):
    client = app.test_client()
    create(client, deadline="2")
    task = rows(app)[0]
    def mutate(operation):
        with app.app_context():
            try:
                if operation == "status":
                    task_service.set_status(task["id"], "done", 1)
                else:
                    task_service.save_task({"title": "Edited", "deadline": "7"}, task["id"], 1)
                return "saved"
            except task_service.TaskConflict:
                return "conflict"
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(mutate, ("status", "edit"))) == ["conflict", "saved"]
    assert rows(app)[0]["revision"] == 2


def part1_database(tmp_path):
    database = existing_database(tmp_path)
    with sqlite3.connect(database) as connection:
        connection.execute(task_storage.SCHEMA)
        connection.execute("INSERT INTO work_schema_migrations(version) VALUES (3)")
        connection.execute("""INSERT INTO standalone_tasks
            (id,title,description,status,revision,created_at,updated_at)
            VALUES ('original','Old task','Original notes','done',5,
                    '2026-10-20T23:30:00.000Z','2026-10-21T01:00:00.000Z')""")
    return database


def test_part1_upgrade_preserves_every_original_field_and_legacy_work(tmp_path):
    database = part1_database(tmp_path)
    before = old_work(database)
    with sqlite3.connect(database) as connection:
        original = connection.execute("SELECT * FROM standalone_tasks").fetchone()
    config = {"TESTING": True, "DATABASE": database}
    upgraded = create_app(config)
    task = rows(upgraded)[0]
    assert tuple(task[key] for key in ("id", "title", "description", "status",
                                       "revision", "created_at", "updated_at")) == original
    assert task["deadline_days"] is None
    assert task["created_on"] == datetime.fromisoformat(original[5]).astimezone().date().isoformat()
    assert rows(create_app(config)) == [task]
    assert old_work(database) == before
    with upgraded.app_context():
        assert storage.get_db().execute("PRAGMA foreign_key_check").fetchall() == []


def test_part2_migration_failure_restores_original_table_and_retries(tmp_path):
    database = part1_database(tmp_path)
    before = old_work(database)
    with sqlite3.connect(database) as connection:
        original = connection.execute("SELECT * FROM standalone_tasks").fetchall()
        columns = connection.execute("PRAGMA table_info(standalone_tasks)").fetchall()
        connection.execute("""CREATE TRIGGER fail_deadline_migration
            BEFORE INSERT ON work_schema_migrations WHEN NEW.version=4
            BEGIN SELECT RAISE(ABORT, 'synthetic failure after table rebuild'); END""")
    config = {"TESTING": True, "DATABASE": database}
    with pytest.raises(sqlite3.IntegrityError):
        create_app(config)
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT * FROM standalone_tasks").fetchall() == original
        assert connection.execute("PRAGMA table_info(standalone_tasks)").fetchall() == columns
        assert not connection.execute("SELECT 1 FROM work_schema_migrations WHERE version=4").fetchall()
        assert not connection.execute("SELECT 1 FROM sqlite_master WHERE name='standalone_tasks_next'").fetchall()
        connection.execute("DROP TRIGGER fail_deadline_migration")
    assert old_work(database) == before
    assert rows(create_app(config))[0]["status"] == "done"


@pytest.mark.parametrize("field,value", [
    ("created_on", None), ("created_on", ""), ("created_on", "2026-02-30"),
    ("created_on", "2026-1-01"), ("deadline_days", 0), ("deadline_days", 3),
    ("deadline_days", 2.5), ("deadline_days", "week"),
])
def test_database_enforces_calendar_date_and_deadline_choices(app, field, value):
    with app.app_context():
        connection = storage.get_db()
        with pytest.raises(sqlite3.IntegrityError):
            if field == "created_on":
                connection.execute("INSERT INTO standalone_tasks(id,title,created_on) VALUES ('bad','Valid',?)",
                                   (value,))
            else:
                connection.execute("""INSERT INTO standalone_tasks(id,title,created_on,deadline_days)
                    VALUES ('bad','Valid','2026-10-21',?)""", (value,))
        connection.rollback()
        assert task_storage.list_tasks() == []
