"""Transactional review invariants exercised through HTTP and independent clients."""
import copy
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from uuid import uuid4
import pytest
from trajectory import create_app, review_storage, storage
from test_goals import app, submit
from test_generation import ready_goal, generate, fake_result, CONTENT


def draft_for(client, app, goal_url=None, content=None):
    goal_url = goal_url or ready_goal(client)
    result = fake_result()
    if content is not None:
        result = (result[0].validate_response(json.dumps(content)), result[1])
    request_id = str(uuid4())
    with patch('trajectory.ai.OllamaAdapter.generate', return_value=result):
        assert generate(client, goal_url, request_id).status_code == 303
    return goal_url, request_id


def post_review(client, goal_url, draft_id, action='approve', **changes):
    client.get(goal_url)
    with client.session_transaction() as state:
        token = state['csrf_token']
    data = {'csrf_token': token, 'revision': '1', 'expected_plan_id': '', 'confirmed': 'on'}
    data.update(changes)
    return client.post(f'{goal_url}/drafts/{draft_id}/{action}', data=data)


def editor_fields(content=CONTENT):
    fields = {'revision': '1', 'summary': content['summary'],
              'assumptions': '\n'.join(content['assumptions']), 'questions': '\n'.join(content['questions']),
              'milestone_count': str(len(content['milestones']))}
    for m, milestone in enumerate(content['milestones']):
        fields.update({f'm{m}_title': milestone['title'],
                       f'm{m}_completion_criterion': milestone['completion_criterion'],
                       f'm{m}_task_count': str(len(milestone['tasks']))})
        for t, task in enumerate(milestone['tasks']):
            fields.update({f'm{m}_t{t}_{key}': '' if value is None else str(value) for key, value in task.items()})
    return fields


def edit_draft(client, goal_url, draft_id, **changes):
    client.get(goal_url)
    with client.session_transaction() as state:
        token = state['csrf_token']
    return client.post(f'{goal_url}/drafts/{draft_id}/edit', data={**editor_fields(), 'csrf_token': token, **changes})


def current(app, goal_url):
    with app.app_context():
        return review_storage.current_plan(goal_url.rsplit('/', 1)[1])


def test_edit_then_approve_exact_revision_and_restart(app):
    client = app.test_client()
    url, draft_id = draft_for(client, app)
    assert client.get(f'{url}/drafts/{draft_id}/edit').status_code == 200
    assert edit_draft(client, url, draft_id, m0_t0_title='Inspect missing values').status_code == 303
    assert current(app, url) is None
    assert post_review(client, url, draft_id).status_code == 409
    assert post_review(client, url, draft_id, revision='2').status_code == 303
    assert current(app, url)['proposal']['milestones'][0]['tasks'][0]['title'] == 'Inspect missing values'
    reopened = create_app(dict(app.config)).test_client().get(url)
    assert b'Your current plan' in reopened.data
    assert b'Inspect missing values' in reopened.data


def test_duplicate_approval_has_one_snapshot_and_one_task(app):
    client = app.test_client()
    url, draft_id = draft_for(client, app)
    assert post_review(client, url, draft_id).status_code == 303
    assert post_review(client, url, draft_id).status_code == 303
    with sqlite3.connect(app.config['DATABASE']) as db:
        assert db.execute('SELECT count(*) FROM approved_plans').fetchone()[0] == 1
        assert db.execute('SELECT count(*) FROM approved_tasks').fetchone()[0] == 1


def test_stale_editor_and_invalid_minutes_preserve_entries(app):
    client = app.test_client()
    url, draft_id = draft_for(client, app)
    response = edit_draft(client, url, draft_id, m0_t0_estimated_minutes='1.5')
    assert response.status_code == 422 and b'1.5' in response.data
    assert edit_draft(client, url, draft_id, summary='First edit').status_code == 303
    response = edit_draft(client, url, draft_id, summary='Unsaved second edit')
    assert response.status_code == 409 and b'Unsaved second edit' in response.data
    with app.app_context():
        assert review_storage.draft_for_review(draft_id)['proposal']['summary'] == 'First edit'


def test_reject_preserves_plan_and_cannot_be_approved(app):
    client = app.test_client()
    url, first = draft_for(client, app)
    post_review(client, url, first)
    old_id = current(app, url)['id']
    _, second = draft_for(client, app, url)
    assert post_review(client, url, second, action='reject').status_code == 303
    assert post_review(client, url, second, action='reject').status_code == 303
    assert post_review(client, url, second).status_code == 409
    assert current(app, url)['id'] == old_id


def test_goal_change_prevents_edit_or_approval(app):
    client = app.test_client()
    url, draft_id = draft_for(client, app)
    submit(client, url + '/edit', title='Changed context')
    assert edit_draft(client, url, draft_id).status_code == 409
    assert post_review(client, url, draft_id).status_code == 409
    assert current(app, url) is None


def test_replacement_preserves_history_and_retains_unchanged_task_ids(app):
    client = app.test_client()
    url, first = draft_for(client, app)
    post_review(client, url, first)
    previous = current(app, url)
    with sqlite3.connect(app.config['DATABASE']) as db:
        old_task = db.execute('SELECT task_id FROM approved_plan_tasks WHERE plan_id=?', (previous['id'],)).fetchone()[0]
    changed = copy.deepcopy(CONTENT)
    changed['milestones'][0]['tasks'].append({'title': 'Write README', 'description': 'Document the run command.', 'estimated_minutes': None})
    _, second = draft_for(client, app, url, changed)
    assert post_review(client, url, second, expected_plan_id=previous['id']).status_code == 303
    with sqlite3.connect(app.config['DATABASE']) as db:
        assert db.execute('SELECT status FROM approved_plans WHERE id=?', (previous['id'],)).fetchone()[0] == 'superseded'
        assert db.execute('SELECT count(*) FROM approved_plan_tasks WHERE task_id=?', (old_task,)).fetchone()[0] == 2
        assert db.execute('SELECT count(*) FROM approved_tasks').fetchone()[0] == 2
    assert post_review(client, url, first).status_code == 409
    assert current(app, url)['draft_id'] == second


def test_old_baseline_cannot_overwrite_another_approval(app):
    client = app.test_client()
    url, first = draft_for(client, app)
    _, second = draft_for(client, app, url)
    post_review(client, url, first)
    assert post_review(client, url, second).status_code == 409
    assert current(app, url)['draft_id'] == first


def test_failure_after_snapshot_insert_rolls_back_every_change(app):
    client = app.test_client()
    url, first = draft_for(client, app)
    post_review(client, url, first)
    previous = current(app, url)
    _, second = draft_for(client, app, url)
    with patch('trajectory.review_storage.carry_tasks_forward', side_effect=sqlite3.OperationalError):
        response = post_review(client, url, second, expected_plan_id=previous['id'])
    assert response.status_code == 503
    assert current(app, url)['id'] == previous['id']
    with app.app_context():
        assert review_storage.draft_for_review(second)['status'] == 'draft'
    with sqlite3.connect(app.config['DATABASE']) as db:
        assert db.execute('SELECT count(*) FROM approved_plans').fetchone()[0] == 1


def test_edit_save_failure_keeps_saved_draft_and_unsaved_text(app):
    client = app.test_client()
    url, draft_id = draft_for(client, app)
    with patch('trajectory.review_storage.change_review', side_effect=sqlite3.OperationalError):
        response = edit_draft(client, url, draft_id, summary='Keep these edits')
    assert response.status_code == 503 and b'Keep these edits' in response.data
    with app.app_context():
        assert review_storage.draft_for_review(draft_id)['revision'] == 1


def test_review_requires_explicit_confirmation_and_csrf(app):
    client = app.test_client()
    url, draft_id = draft_for(client, app)
    assert post_review(client, url, draft_id, confirmed='').status_code == 409
    assert post_review(client, url, draft_id, action='reject', confirmed='').status_code == 409
    assert client.post(f'{url}/drafts/{draft_id}/approve').status_code == 400
    assert client.post(f'{url}/drafts/{draft_id}/edit').status_code == 400


def test_draft_cannot_be_reviewed_under_another_goal(app):
    client = app.test_client()
    url, draft_id = draft_for(client, app)
    other = ready_goal(client)
    assert post_review(client, other, draft_id).status_code == 404


def test_saved_content_revalidated_before_approval(app):
    client = app.test_client()
    url, draft_id = draft_for(client, app)
    with sqlite3.connect(app.config['DATABASE']) as db:
        db.execute('UPDATE plan_drafts SET content=? WHERE id=?', (json.dumps({**CONTENT, 'milestones': []}), draft_id))
    assert post_review(client, url, draft_id).status_code == 409
    assert current(app, url) is None


def test_simultaneous_approval_is_duplicate_safe(app):
    client = app.test_client()
    url, draft_id = draft_for(client, app)
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: post_review(app.test_client(), url, draft_id).status_code, range(2)))
    assert responses == [303, 303]
    with sqlite3.connect(app.config['DATABASE']) as db:
        assert db.execute('SELECT count(*) FROM approved_plans').fetchone()[0] == 1


def test_removed_task_is_archived_and_history_preserved(app):
    client = app.test_client()
    url, first = draft_for(client, app)
    post_review(client, url, first)
    previous = current(app, url)
    changed = copy.deepcopy(CONTENT)
    changed['milestones'][0]['tasks'][0]['title'] = 'Different work'
    _, second = draft_for(client, app, url, changed)
    post_review(client, url, second, expected_plan_id=previous['id'])
    with sqlite3.connect(app.config['DATABASE']) as db:
        assert db.execute('SELECT count(*) FROM approved_tasks WHERE archived=1').fetchone()[0] == 1
        assert db.execute('SELECT count(*) FROM approved_plan_tasks').fetchone()[0] == 2


def test_editor_reorders_adds_and_removes_without_accepting(app):
    client = app.test_client()
    url, draft_id = draft_for(client, app)
    changes = {'milestone_count': '2', 'm0_title': 'First', 'm0_task_count': '1',
               'm1_title': 'Second', 'm1_completion_criterion': 'A report exists', 'm1_task_count': '1',
               'm1_t0_title': 'Write report', 'm1_t0_description': 'Explain findings.', 'm1_t0_estimated_minutes': ''}
    assert edit_draft(client, url, draft_id, **changes).status_code == 303
    with app.app_context():
        draft = review_storage.draft_for_review(draft_id)
    assert [m['title'] for m in draft['proposal']['milestones']] == ['First', 'Second']
    assert draft['proposal']['milestones'][1]['tasks'][0]['estimated_minutes'] is None
    assert current(app, url) is None
