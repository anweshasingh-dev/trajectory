"""Exact-revision review policy; all state transitions are atomic."""
from . import storage, review_storage
from .plan_models import PlanProposal


class ReviewConflict(Exception):
    pass


def check_editable(draft, goal, revision):
    if draft is None or goal is None or draft['goal_id'] != goal['id']:
        raise ReviewConflict("This draft no longer belongs to the selected goal.")
    if draft['source_revision'] != goal['revision']:
        raise ReviewConflict("The goal changed. Generate a new draft from its current context.")
    if draft['status'] != 'draft' or draft['revision'] != revision:
        raise ReviewConflict("This draft changed or was already reviewed. Your changes are unsaved; reopen it before continuing.")


def save_edits(goal_id, draft_id, revision, content):
    proposal = PlanProposal.validate_response(content)
    with review_storage.write_transaction():
        draft = review_storage.draft_for_review(draft_id)
        check_editable(draft, storage.find_goal(goal_id), revision)
        review_storage.change_review(draft_id, 'draft', proposal.model_dump_json())


def approve(goal_id, draft_id, revision, expected_plan_id, confirmed):
    if not confirmed:
        raise ReviewConflict("Confirm that you reviewed the exact saved draft before approving.")
    with review_storage.write_transaction():
        draft = review_storage.draft_for_review(draft_id)
        goal = storage.find_goal(goal_id)
        previous = review_storage.current_plan(goal_id)
        approved = review_storage.plan_for_draft(draft_id)
        # A replay may acknowledge the same current approval, never reactivate history.
        if (approved and approved['goal_id'] == goal_id and approved['status'] == 'current'
                and approved['draft_revision'] == revision and goal
                and approved['source_revision'] == goal['revision']):
            return approved['id']
        check_editable(draft, goal, revision)
        if (previous['id'] if previous else '') != expected_plan_id:
            raise ReviewConflict("The approved plan changed in another tab. Review the current plan before replacing it.")
        proposal = PlanProposal.validate_response(draft['content'])
        plan_id = review_storage.insert_approved_plan(draft, proposal, previous)
        review_storage.change_review(draft_id, 'approved')
        return plan_id


def reject(goal_id, draft_id, revision, confirmed):
    if not confirmed:
        raise ReviewConflict("Confirm rejection of this draft. The approved plan will be preserved.")
    with review_storage.write_transaction():
        draft = review_storage.draft_for_review(draft_id)
        goal = storage.find_goal(goal_id)
        if (draft and goal and draft['goal_id'] == goal_id and draft['status'] == 'rejected'
                and draft['revision'] == revision + 1):
            return
        check_editable(draft, goal, revision)
        review_storage.change_review(draft_id, 'rejected')
