"""Validate goal changes before asking persistence to commit them."""
from .models import GoalInput
from . import storage
from .clarification import FLAGS


class StaleGoalError(Exception):
    pass


def save_goal(fields, goal_id=None, revision=None):
    goal = GoalInput.model_validate(fields)
    values = (
        goal.title, goal.description, goal.desired_outcome, goal.starting_point,
        goal.weekly_hours, goal.target_date.isoformat() if goal.target_date else None,
    )
    answers = [flag for flag in FLAGS if getattr(goal, flag)]
    if goal_id is None:
        return storage.insert_goal(values, answers)
    if not storage.update_goal(goal_id, revision, values, answers):
        raise StaleGoalError("This goal changed in another tab. Your edits are unsaved. Open the saved goal to compare before retrying.")
    return goal_id
