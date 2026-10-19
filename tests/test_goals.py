"""Exercise persistence and failure paths through real HTTP form requests."""
import sqlite3
from unittest.mock import patch
import pytest
from trajectory import create_app


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "SECRET_KEY": "test-only", "DATABASE": str(tmp_path / "goals.sqlite")})


def submit(client, url="/goals/new", **overrides):
    client.get(url)
    with client.session_transaction() as state:
        token = state["csrf_token"]
    data = {"csrf_token": token, "title": "Learn ML", "description": "Build a portfolio project", "revision": "1"}
    data.update(overrides)
    return client.post(url, data=data)


def test_goal_survives_new_application_instance(app):
    response = submit(app.test_client(), weekly_hours="2.5")
    assert response.status_code == 303
    reopened = create_app(dict(app.config)).test_client().get(response.location)
    assert b"Learn ML" in reopened.data
    assert b"2.5 hours / week" in reopened.data
    assert b"Not specified" in reopened.data


@pytest.mark.parametrize("fields", [{"title": "   "}, {"weekly_hours": "nan"}, {"weekly_hours": "169"}, {"weekly_hours": "0"}, {"target_date": "2026-02-30"}])
def test_invalid_input_does_not_write(app, fields):
    response = submit(app.test_client(), **fields)
    assert response.status_code == 422
    assert b"Unsaved" in response.data
    with sqlite3.connect(app.config["DATABASE"]) as connection:
        assert connection.execute("SELECT count(*) FROM goals").fetchone()[0] == 0


def test_stale_edit_preserves_latest_goal(app):
    client = app.test_client()
    created = submit(client)
    url = created.location.split("?")[0] + "/edit"
    assert submit(client, url, title="Updated goal").status_code == 303
    response = submit(client, url, title="Stale goal", revision="1")
    assert response.status_code == 409
    assert b"Stale goal" in response.data
    assert b"Updated goal" in client.get(created.location).data


def test_failed_save_preserves_entered_text(app):
    with patch("trajectory.storage.insert_goal", side_effect=sqlite3.OperationalError):
        response = submit(app.test_client(), title="Keep my writing")
    assert response.status_code == 503
    assert b"Keep my writing" in response.data
    assert b"Unsaved" in response.data


def test_csrf_required_and_unknown_goal_returns_404(app):
    client = app.test_client()
    assert client.post("/goals/new", data={"title": "Rejected"}).status_code == 400
    assert client.get("/goals/missing").status_code == 404


def test_user_content_is_escaped_and_optional_values_stay_unknown(app):
    client = app.test_client()
    created = submit(client, title="<script>alert(1)</script>")
    page = client.get(created.location)
    assert b"<script>alert(1)</script>" not in page.data
    assert b"&lt;script&gt;" in page.data
    assert b"Unknown" in page.data


def test_update_persists_corrected_context(app):
    client = app.test_client()
    created = submit(client, weekly_hours="4")
    url = created.location.split("?")[0] + "/edit"
    updated = submit(client, url, weekly_hours="", desired_outcome="Publish a demo", target_date="2026-12-01")
    page = client.get(updated.location)
    assert b"Publish a demo" in page.data
    assert b"2026-12-01" in page.data
    assert b"Unknown" in page.data
