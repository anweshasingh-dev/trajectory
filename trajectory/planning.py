"""Coordinate inference without holding a database transaction open."""
from uuid import UUID
from . import storage, draft_storage
from .clarification import FLAGS


class DraftConflict(Exception):
    pass


def generate_draft(goal_id, revision, request_id, adapter):
    try:
        request_id = str(UUID(request_id))
    except (ValueError, TypeError, AttributeError) as error:
        raise DraftConflict("Reload the goal before generating a proposal.") from error
    goal = storage.find_goal(goal_id)
    if goal is None or goal["revision"] != revision:
        raise DraftConflict("The goal changed. Review its saved context before generating.")
    existing = draft_storage.find_draft(request_id)
    if existing is not None:
        if existing["goal_id"] != goal_id or existing["source_revision"] != revision:
            raise DraftConflict("This generation request is stale. Reload the goal.")
        return request_id
    context = {key: goal[key] for key in (
        "title", "description", "desired_outcome", "starting_point", "weekly_hours", "target_date", *FLAGS
    )}
    proposal, provenance = adapter.generate(context)
    if not draft_storage.insert_draft(request_id, goal_id, revision, proposal, provenance):
        existing = draft_storage.find_draft(request_id)
        if existing is None or existing["goal_id"] != goal_id or existing["source_revision"] != revision:
            raise DraftConflict("The goal changed during generation. The response was discarded; review the current goal and retry.")
    return request_id
