"""Fake-adapter workflow checks; live model evidence is recorded separately."""
import json
import sqlite3
from uuid import uuid4
from unittest.mock import Mock, patch
from urllib.error import URLError
import pytest
from trajectory import create_app, storage
from trajectory.ai import OllamaAdapter, InferenceError
from trajectory.plan_models import PlanProposal
from test_goals import app, submit

CONTENT = {
    "summary": "Build a reproducible baseline.", "assumptions": [], "questions": [],
    "milestones": [{"title": "Baseline", "completion_criterion": "Record a baseline score",
                    "tasks": [{"title": "Inspect the data", "description": "Check missing values.",
                               "estimated_minutes": 30}]}],
}


def ready_goal(client):
    result = submit(client, desired_outcome="Portfolio demo", starting_point="Basic Python",
                    weekly_hours="4", no_deadline="on")
    return result.location.split("?")[0]


def generate(client, goal_url, request_id=None, revision="1"):
    client.get(goal_url)
    with client.session_transaction() as state:
        token = state["csrf_token"]
    return client.post(goal_url + "/generate", data={"csrf_token": token,
                       "request_id": request_id or str(uuid4()), "revision": revision})


def fake_result():
    return PlanProposal.validate_response(json.dumps(CONTENT)), {
        "model": "test-model", "digest": "test-digest", "prompt_version": "test-v1"}


def test_draft_is_saved_reopened_and_duplicate_request_is_idempotent(app):
    client = app.test_client()
    goal_url = ready_goal(client)
    request_id = str(uuid4())
    with patch("trajectory.ai.OllamaAdapter.generate", return_value=fake_result()) as adapter:
        assert generate(client, goal_url, request_id).status_code == 303
        assert generate(client, goal_url, request_id).status_code == 303
        assert adapter.call_count == 1
    page = create_app(dict(app.config)).test_client().get(goal_url)
    assert b"Inspect the data" in page.data
    assert b"Draft saved locally" in page.data
    with sqlite3.connect(app.config["DATABASE"]) as connection:
        assert connection.execute("SELECT count(*) FROM plan_drafts").fetchone()[0] == 1


@pytest.mark.parametrize("optional", [
    {},
    {"weekly_hours": "", "target_date": ""},
    {"desired_outcome": "Publish a demo", "starting_point": "Know Python"},
    {"weekly_hours": "3", "target_date": "2026-12-01"},
])
def test_optional_context_does_not_block_generation_or_invent_goal_facts(app, optional):
    client = app.test_client()
    goal_url = submit(client, **optional).location.split("?")[0]
    goal_id = goal_url.rsplit("/", 1)[1]
    with app.app_context():
        before = storage.find_goal(goal_id)
    with patch("trajectory.ai.OllamaAdapter.generate", return_value=fake_result()) as adapter:
        assert generate(client, goal_url).status_code == 303
        context = adapter.call_args.args[0]
    assert context["weekly_hours"] == before["weekly_hours"]
    assert context["target_date"] == before["target_date"]
    assert context["desired_outcome"] == before["desired_outcome"]
    assert context["starting_point"] == before["starting_point"]
    assert not any(context[flag] for flag in (
        "outcome_unknown", "starting_point_unknown", "hours_unknown", "no_deadline"))
    with app.app_context():
        assert storage.find_goal(goal_id) == before
    page = create_app(dict(app.config)).test_client().get(goal_url)
    assert b"Inspect the data" in page.data
    assert b"Draft saved locally" in page.data


def test_goal_change_during_generation_discards_response(app):
    client = app.test_client()
    goal_url = ready_goal(client)
    def change_goal(context):
        with storage.get_db() as connection:
            connection.execute("UPDATE goals SET revision=revision+1")
        return fake_result()
    with patch("trajectory.ai.OllamaAdapter.generate", side_effect=change_goal):
        response = generate(client, goal_url)
    assert response.status_code == 409
    assert b"response was discarded" in response.data
    with sqlite3.connect(app.config["DATABASE"]) as connection:
        assert connection.execute("SELECT count(*) FROM plan_drafts").fetchone()[0] == 0


def test_failed_generation_preserves_previous_draft(app):
    client = app.test_client()
    goal_url = ready_goal(client)
    with patch("trajectory.ai.OllamaAdapter.generate", return_value=fake_result()):
        generate(client, goal_url)
    with patch("trajectory.ai.OllamaAdapter.generate", side_effect=InferenceError("Runtime unavailable")):
        response = generate(client, goal_url)
    assert response.status_code == 502
    assert b"Runtime unavailable" in response.data
    assert b"Inspect the data" in response.data


def test_draft_save_failure_leaves_no_partial_record(app):
    client = app.test_client()
    goal_url = ready_goal(client)
    with patch("trajectory.ai.OllamaAdapter.generate", return_value=fake_result()), patch(
        "trajectory.draft_storage.insert_draft", side_effect=sqlite3.OperationalError
    ):
        response = generate(client, goal_url)
    assert response.status_code == 503
    assert b"could not be saved" in response.data


def test_draft_marked_outdated_after_goal_edit(app):
    client = app.test_client()
    goal_url = ready_goal(client)
    with patch("trajectory.ai.OllamaAdapter.generate", return_value=fake_result()):
        generate(client, goal_url)
    submit(client, goal_url + "/edit", title="Revised ambition")
    assert b"Outdated draft" in client.get(goal_url).data


@pytest.mark.parametrize("content, reason", [
    ("not json", "stop"),
    (json.dumps({**CONTENT, "milestones": []}), "stop"),
    (json.dumps({**CONTENT, "approved": True}), "stop"),
    (json.dumps(CONTENT), "length"),
])
def test_invalid_or_truncated_model_output_is_rejected(content, reason):
    adapter = OllamaAdapter()
    adapter._request = Mock(side_effect=[
        {"models": [{"name": "qwen3:4b", "digest": "sha256:test"}]},
        {"done": True, "done_reason": reason, "message": {"content": content}},
    ])
    with pytest.raises(InferenceError, match="invalid proposal"):
        adapter.generate({"title": "test"})


def test_adapter_sends_schema_and_uses_bounded_local_options():
    adapter = OllamaAdapter()
    adapter._request = Mock(side_effect=[
        {"models": [{"name": "qwen3:4b", "digest": "sha256:test"}]},
        {"done": True, "done_reason": "stop", "message": {"content": json.dumps(CONTENT)}},
    ])
    proposal, provenance = adapter.generate({"title": "test"})
    payload = adapter._request.call_args.args[1]
    assert payload["stream"] is False
    assert payload["think"] is False
    assert payload["format"]["additionalProperties"] is False
    assert payload["options"]["num_predict"] == 2200
    assert provenance["digest"] == "sha256:test"
    assert proposal.milestones[0].tasks[0].estimated_minutes == 30


@pytest.mark.parametrize("error", [URLError("offline"), TimeoutError()])
def test_unavailable_or_timeout_is_actionable(error):
    adapter = OllamaAdapter()
    adapter.opener.open = Mock(side_effect=error)
    with pytest.raises(InferenceError):
        adapter.generate({"title": "test"})


def test_missing_model_has_install_instruction():
    adapter = OllamaAdapter()
    adapter._request = Mock(return_value={"models": []})
    with pytest.raises(InferenceError, match="ollama pull qwen3:4b"):
        adapter.generate({"title": "test"})


def test_generation_requires_csrf(app):
    client = app.test_client()
    goal_url = ready_goal(client)
    assert client.post(goal_url + "/generate").status_code == 400
