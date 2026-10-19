"""HTML editing and explicit review actions; no model calls during approval."""
import sqlite3
from flask import Blueprint, abort, redirect, render_template, request, url_for
from pydantic import ValidationError
from . import draft_editor, review_service, review_storage, storage

bp = Blueprint('reviews', __name__)


def selected_draft(goal_id, draft_id):
    goal = storage.find_goal(goal_id)
    draft = review_storage.draft_for_review(draft_id)
    if goal is None or draft is None or draft['goal_id'] != goal_id:
        abort(404)
    return goal, draft


@bp.route('/goals/<goal_id>/drafts/<draft_id>/edit', methods=['GET', 'POST'])
def edit(goal_id, draft_id):
    goal, draft = selected_draft(goal_id, draft_id)
    values, error, status = draft['proposal'], None, 200
    revision = request.form.get('revision', draft['revision'])
    try:
        if request.method == 'POST':
            values = draft_editor.parse_form(request.form)
            content = draft_editor.validation_content(values)
            review_service.save_edits(goal_id, draft_id, int(revision), content)
            return redirect(url_for('goals.detail', goal_id=goal_id), code=303)
        review_service.check_editable(draft, goal, draft['revision'])
    except ValidationError as failure:
        error = '; '.join('.'.join(map(str, item['loc'])) + ': ' + item['msg'] for item in failure.errors())
        status = 422
    except ValueError as failure:
        error, status = str(failure), 422
    except review_service.ReviewConflict as failure:
        error, status = str(failure), 409
    except sqlite3.Error:
        error, status = 'Unsaved: the database could not save the draft. Your entries remain below.', 503
    return render_template('draft_form.html', goal=goal, draft=draft, values=values,
                           revision=revision, error=error), status


@bp.route('/goals/<goal_id>/drafts/<draft_id>/<action>', methods=['POST'])
def decide(goal_id, draft_id, action):
    goal, draft = selected_draft(goal_id, draft_id)
    if action not in ('approve', 'reject'):
        abort(404)
    try:
        revision = int(request.form.get('revision', '0'))
        if action == 'approve':
            review_service.approve(goal_id, draft_id, revision,
                                   request.form.get('expected_plan_id', ''),
                                   request.form.get('confirmed') == 'on')
        else:
            review_service.reject(goal_id, draft_id, revision, request.form.get('confirmed') == 'on')
        return redirect(url_for('goals.detail', goal_id=goal_id), code=303)
    except (ValueError, review_service.ReviewConflict) as failure:
        message, status = str(failure), 409
    except sqlite3.Error:
        message, status = 'The review could not be saved. The prior approved plan is preserved. Please retry.', 503
    from .clarification import questions_for
    return render_template('workspace.html', goal=storage.find_goal(goal_id), goals=storage.list_goals(),
                           draft=review_storage.draft_for_review(draft_id),
                           approved=review_storage.current_plan(goal_id), questions=questions_for(goal),
                           generation_error=message), status
