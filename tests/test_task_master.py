"""Standalone task workflows through HTTP and restartable temporary storage."""
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
import pytest
from werkzeug.datastructures import MultiDict
from trajectory import create_app, task_service, task_storage
from test_goals import app


def post(client, url="/tasks/new", **changes):
    client.get("/tasks/new")
    with client.session_transaction() as state:
        token = state["csrf_token"]
    return client.post(url, data={"csrf_token": token, **changes})


def rows(app):
    with app.app_context():
        return task_storage.list_tasks()


def create(client, **changes):
    return post(client, **{"title": "Finish assignment", **changes})


def test_navigation_empty_page_and_no_future_controls(app):
    client = app.test_client()
    home, tasks = client.get("/"), client.get("/tasks")
    assert home.status_code == tasks.status_code == 200
    assert b'href="/tasks"' in home.data
    assert b'aria-current="page">Task Master' in tasks.data
    assert b'aria-current="page">Goal Planner' in home.data
    assert b"What needs doing?" in tasks.data
    for future in (b"Generate plan", b"Daily available time", b"progress analytics"):
        assert future not in tasks.data


def test_title_only_and_notes_survive_edits_and_restart(app):
    client = app.test_client()
    assert create(client, title="  Finish assignment  ").status_code == 303
    original = rows(app)[0]
    assert original["title"] == "Finish assignment" and original["description"] == ""
    assert original["status"] == "undone" and original["revision"] == 1
    assert original["created_at"] == original["updated_at"]
    assert original["created_at"].endswith("Z")
    url = f'/tasks/{original["id"]}/edit'
    assert post(client, url, title="Submit assignment", description="  Check references.  ",
                revision="1").status_code == 303
    saved = rows(app)[0]
    assert saved["id"] == original["id"] and saved["created_at"] == original["created_at"]
    assert saved["description"] == "Check references." and saved["revision"] == 2
    restarted = create_app(dict(app.config))
    assert rows(restarted) == [saved]
    page = restarted.test_client().get("/tasks")
    assert b"Submit assignment" in page.data and b"Check references." in page.data
    with restarted.app_context():
        assert task_storage.list_tasks()[0]["status"] == "undone"


@pytest.mark.parametrize("changes", [
    {"title": ""}, {"title": " \t\n "}, {"title": "x" * 161},
    {"description": "x" * 1201}, {"status": "done"},
    {"goal_id": "invented"}, {"estimated_minutes": "30"}, {"id": "chosen-id"},
    {"created_at": "2026-01-01"}, {"revision": "1"},
])
def test_invalid_or_unexpected_input_preserves_form_without_writing(app, changes):
    response = create(app.test_client(), **changes)
    assert response.status_code == 422 and b"Unsaved" in response.data
    assert rows(app) == []


def test_missing_title_and_duplicate_fields_are_rejected(app):
    client = app.test_client()
    assert post(client).status_code == 422
    client.get("/tasks")
    with client.session_transaction() as state:
        token = state["csrf_token"]
    response = client.post("/tasks/new", data=MultiDict([
        ("csrf_token", token), ("title", "First"), ("title", "Second"),
    ]))
    assert response.status_code == 422 and rows(app) == []


def test_equal_titles_keep_distinct_ids_and_deterministic_order(app):
    client = app.test_client()
    create(client)
    create(client)
    tasks = rows(app)
    assert len(tasks) == 2 and tasks[0]["id"] != tasks[1]["id"]
    with sqlite3.connect(app.config["DATABASE"]) as connection:
        connection.execute("UPDATE standalone_tasks SET created_at='2026-10-21T00:00:00.000Z'")
    assert [task["id"] for task in rows(app)] == sorted(task["id"] for task in tasks)


def test_stale_edit_preserves_latest_task_and_unsaved_input(app):
    client = app.test_client()
    create(client)
    task = rows(app)[0]
    url = f'/tasks/{task["id"]}/edit'
    assert post(client, url, title="Latest", revision="1").status_code == 303
    response = post(client, url, title="Unsaved older edit", description="Keep notes", revision="1")
    assert response.status_code == 409 and b"Unsaved older edit" in response.data
    assert b"Keep notes" in response.data
    assert rows(app)[0]["title"] == "Latest" and rows(app)[0]["revision"] == 2


@pytest.mark.parametrize("revision", ["", "0", "-1", "1.0", "nan", "9223372036854775808"])
def test_bad_revision_cannot_edit_or_delete(app, revision):
    client = app.test_client()
    create(client)
    task = rows(app)[0]
    assert post(client, f'/tasks/{task["id"]}/edit',
                title="Rejected", revision=revision).status_code == 422
    assert post(client, f'/tasks/{task["id"]}/delete',
                confirmed="on", revision=revision).status_code == 422
    assert rows(app) == [task]
def test_confirmation_and_cancel_do_not_delete_then_removal_is_permanent(app):
    client = app.test_client()
    create(client, description="Notes to remove")
    task = rows(app)[0]
    url = f'/tasks/{task["id"]}/delete'
    confirmation = client.get(url)
    assert confirmation.status_code == 200 and b"Undone" in confirmation.data
    assert b"Finish assignment" in confirmation.data and b"Notes to remove" in confirmation.data
    assert rows(app) == [task]
    client.get("/tasks")  # Cancel is a normal link without a mutation.
    assert post(client, url, revision="1").status_code == 422
    assert post(client, url, revision="1", confirmed="true").status_code == 422
    assert rows(app) == [task]
    deleted = post(client, url, revision="1", confirmed="on")
    assert deleted.status_code == 303 and rows(app) == []
    assert b"Task permanently deleted." in client.get(deleted.location).data
    repeated = post(client, url, revision="1", confirmed="on")
    assert repeated.status_code == 303 and b"already been deleted" in client.get(repeated.location).data
    assert client.get(url).status_code == 404
    assert client.get(f'/tasks/{task["id"]}/edit').status_code == 404
    assert rows(create_app(dict(app.config))) == []


def test_stale_deletion_requires_fresh_review_and_deleted_task_is_not_recreated(app):
    client = app.test_client()
    create(client)
    task = rows(app)[0]
    edit_url, delete_url = f'/tasks/{task["id"]}/edit', f'/tasks/{task["id"]}/delete'
    client.get(delete_url)
    assert post(client, edit_url, title="Revised title", revision="1").status_code == 303
    response = post(client, delete_url, confirmed="on", revision="1")
    assert response.status_code == 409 and b"Review latest task" in response.data
    assert b'type="submit"' not in response.data
    assert rows(app)[0]["title"] == "Revised title"
    assert post(client, delete_url, confirmed="on", revision="2").status_code == 303
    response = post(client, edit_url, title="Do not recreate", revision="2")
    assert response.status_code == 409 and b"Do not recreate" in response.data
    assert rows(app) == []


def test_shared_csrf_method_protection_and_escaped_content(app):
    client = app.test_client()
    assert client.post("/tasks/new", data={"title": "No token"}).status_code == 400
    create(client, title="<script>alert(1)</script>", description="<b>Private notes</b>")
    task = rows(app)[0]
    for suffix in ("edit", "delete"):
        url = f'/tasks/{task["id"]}/{suffix}'
        assert client.post(url, data={"revision": "1", "confirmed": "on"}).status_code == 400
        assert client.put(url).status_code == 405
        page = client.get(url)
        assert b"<script>alert(1)</script>" not in page.data and b"&lt;script&gt;" in page.data
    page = client.get("/tasks")
    assert b"&lt;b&gt;Private notes&lt;/b&gt;" in page.data
    assert len(rows(app)) == 1


@pytest.mark.parametrize("operation", ["insert", "update", "delete"])
def test_failure_after_write_rolls_back_and_preserves_retry_values(app, operation):
    client = app.test_client()
    if operation != "insert":
        create(client)
    before = rows(app)
    target = getattr(task_storage, f"{operation}_task")
    def fail_after_write(*args):
        target(*args)
        raise sqlite3.OperationalError("synthetic failure after the mutation")
    with patch(f"trajectory.task_storage.{operation}_task", side_effect=fail_after_write):
        if operation == "insert":
            response = create(client, title="Keep entered text", description="Keep entered notes")
        elif operation == "update":
            response = post(client, f'/tasks/{before[0]["id"]}/edit',
                            title="Keep entered text", description="Keep entered notes", revision="1")
        else:
            response = post(client, f'/tasks/{before[0]["id"]}/delete', revision="1", confirmed="on")
    assert response.status_code == 503 and rows(app) == before
    if operation != "delete":
        assert b"Keep entered text" in response.data and b"Keep entered notes" in response.data
    else:
        assert b"Deletion did not complete" in response.data
    if operation == "insert":
        assert create(client, title="Keep entered text").status_code == 303
        assert len(rows(app)) == 1


def test_task_list_read_failure_is_actionable(app):
    with patch("trajectory.task_storage.list_tasks", side_effect=sqlite3.OperationalError):
        response = app.test_client().get("/tasks")
    assert response.status_code == 503 and b"Reload this page" in response.data
    assert b"What needs doing?" not in response.data


def test_serialized_concurrent_edits_have_one_winner(app):
    client = app.test_client()
    create(client)
    task = rows(app)[0]
    def change(title):
        with app.app_context():
            try:
                task_service.save_task({"title": title}, task["id"], 1)
                return "saved"
            except task_service.TaskConflict:
                return "conflict"
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(change, ["First update", "Second update"]))
    assert sorted(results) == ["conflict", "saved"]
    assert rows(app)[0]["revision"] == 2
