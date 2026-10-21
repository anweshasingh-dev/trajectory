"""Current MVP hides legacy progress without losing saved work or handlers."""
from datetime import date
from uuid import uuid4
from unittest.mock import patch
import pytest
from trajectory import create_app, progress_service, progress_storage, work_storage
from test_goals import app, submit
from test_work import add_milestone, add_task, work_rows


@pytest.fixture
def saved_legacy_work(app):
    client = app.test_client()
    goal_url = submit(client).location.split("?")[0]
    assert add_milestone(client, goal_url).status_code == 303
    milestone_id = work_rows(app, goal_url)[0][0]["id"]
    assert add_task(client, goal_url, milestone_id=milestone_id).status_code == 303
    task_id = work_rows(app, goal_url)[1][0]["id"]
    goal_id = goal_url.rsplit("/", 1)[1]
    with app.app_context():
        entry_id = progress_service.save_entry(
            goal_id, task_id, None, work_storage.revision(goal_id),
            {"work_date": date.today().isoformat(), "outcome": "completed",
             "actual_minutes": 37, "notes": "Legacy notes to preserve"}, str(uuid4()))
        entries = progress_storage.entries_for_task(task_id)
    return goal_url, task_id, entry_id, entries


def test_current_ui_hides_progress_but_preserves_goal_and_task_editing(app, saved_legacy_work):
    goal_url, task_id, _, _ = saved_legacy_work
    client = app.test_client()
    assert app.config["LEGACY_PROGRESS_UI"] is False
    goal_page = client.get(goal_url)
    with patch("trajectory.progress_service.summaries_for_goal") as summaries:
        work_page = client.get(goal_url + "/work")
        summaries.assert_not_called()
    assert goal_page.status_code == work_page.status_code == 200
    assert b"Generate proposal" in goal_page.data
    assert b"Manage milestones and tasks" in goal_page.data
    assert b"Write demo" in work_page.data and b"Edit task" in work_page.data
    for hidden in (b"/progress", b"/entries/", b"View work history", b"Mark complete",
                   b"Reopen task", b"tasks completed", b"minutes recorded",
                   b"Legacy notes to preserve", b"Record dated progress"):
        assert hidden not in goal_page.data + work_page.data
    assert client.get(goal_url + "/edit").status_code == 200
    assert client.get(f"{goal_url}/work/tasks/{task_id}/edit").status_code == 200


@pytest.mark.parametrize("method,suffix", [
    ("GET", "/progress"),
    ("GET", "/entries/new"),
    ("GET", "/entries/{entry_id}/edit"),
    ("POST", "/entries/new"),
    ("POST", "/entries/{entry_id}/edit"),
    ("POST", "/entries/{entry_id}/delete"),
])
def test_bookmarked_progress_routes_are_hidden_and_cannot_change_data(
        app, saved_legacy_work, method, suffix):
    goal_url, task_id, entry_id, before = saved_legacy_work
    client = app.test_client()
    client.get(goal_url)
    with client.session_transaction() as state:
        token = state["csrf_token"]
    url = f"{goal_url}/tasks/{task_id}" + suffix.format(entry_id=entry_id)
    response = client.open(url, method=method, data={"csrf_token": token})
    assert response.status_code == 404
    with app.app_context():
        assert progress_storage.entries_for_task(task_id) == before


def test_legacy_records_survive_restart_and_existing_code_remains_usable(app, saved_legacy_work):
    goal_url, task_id, _, before = saved_legacy_work
    restarted = create_app(dict(app.config))
    client = restarted.test_client()
    assert restarted.config["LEGACY_PROGRESS_UI"] is False
    assert b"View work history" not in client.get(goal_url + "/work").data
    with restarted.app_context():
        entries = progress_storage.entries_for_task(task_id)
        assert entries == before
        assert progress_service.fold_entries(entries)["status"] == "completed"
        assert progress_service.fold_entries(entries)["actual_minutes"] == 37
    assert client.get(f"{goal_url}/tasks/{task_id}/progress").status_code == 404
    # This opt-in is server controlled; there is no user-facing toggle.
    restarted.config["LEGACY_PROGRESS_UI"] = True
    assert b"37 minutes" in client.get(f"{goal_url}/tasks/{task_id}/progress").data
