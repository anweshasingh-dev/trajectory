"""Clarification persistence, contradictory answers and migration regressions."""
import sqlite3
from unittest.mock import patch
import pytest
from trajectory import create_app
from test_goals import app, submit


def test_unanswered_goal_shows_questions(app):
    client = app.test_client()
    created = submit(client, description="Finish in eight weeks")
    page = client.get(created.location)
    assert b"A few details to clarify" in page.data
    assert b"specific target date" in page.data
    assert b"Context ready" not in page.data


def test_explicit_unknowns_survive_restart(app):
    client = app.test_client()
    created = submit(client, outcome_unknown="on", starting_point_unknown="on", hours_unknown="on", no_deadline="on")
    restarted = create_app(dict(app.config)).test_client()
    page = restarted.get(created.location)
    assert b"Context ready for a proposal" in page.data
    assert b"No fixed deadline" in page.data
    assert b"Unknown" in page.data
    form = restarted.get(created.location.split("?")[0] + "/edit")
    assert b'name="no_deadline" checked' in form.data


@pytest.mark.parametrize("fields", [
    {"desired_outcome": "Publish", "outcome_unknown": "on"},
    {"starting_point": "Beginner", "starting_point_unknown": "on"},
    {"weekly_hours": "4", "hours_unknown": "on"},
    {"target_date": "2026-12-01", "no_deadline": "on"},
])
def test_conflicting_answers_are_rejected(app, fields):
    response = submit(app.test_client(), **fields)
    assert response.status_code == 422
    assert b"not both" in response.data


def test_real_values_are_ready_without_alternatives(app):
    client = app.test_client()
    created = submit(client, desired_outcome="Publish a demo", starting_point="Know Python", weekly_hours="4", target_date="2026-12-01")
    assert b"Context ready for a proposal" in client.get(created.location).data


def test_revision_and_answer_change_are_atomic(app):
    client = app.test_client()
    created = submit(client, no_deadline="on")
    url = created.location.split("?")[0] + "/edit"
    with patch("trajectory.storage.replace_answers", side_effect=sqlite3.OperationalError):
        assert submit(client, url, title="Must roll back").status_code == 503
    page = client.get(created.location)
    assert b"Must roll back" not in page.data
    assert b"No fixed deadline" in page.data
    assert submit(client, url, target_date="2026-12-01").status_code == 303
    stale = submit(client, url, no_deadline="on")
    assert stale.status_code == 409
    page = client.get(created.location)
    assert b"2026-12-01" in page.data
    assert b"No fixed deadline" not in page.data


def test_existing_database_receives_additive_schema(app):
    client = app.test_client()
    created = submit(client)
    with sqlite3.connect(app.config["DATABASE"]) as connection:
        connection.execute("DROP TABLE goal_context_answers")
    restarted = create_app(dict(app.config)).test_client()
    page = restarted.get(created.location)
    assert page.status_code == 200
    assert b"Learn ML" in page.data
    assert b"A few details to clarify" in page.data
