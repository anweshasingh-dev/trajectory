"""Validated direct work editing with aggregate optimistic concurrency."""
from pydantic import BaseModel, ConfigDict, Field, field_validator
from . import storage, work_storage
from .review_storage import write_transaction


class WorkConflict(Exception):
    pass


class MilestoneInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=160)
    completion_criterion: str = Field(min_length=1, max_length=800)


class TaskInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1, max_length=1200)
    estimated_minutes: int | None = Field(default=None, ge=1, le=10080)
    milestone_id: str | None = Field(default=None, max_length=36)

    @field_validator("estimated_minutes", "milestone_id", mode="before")
    @classmethod
    def blank_is_unknown(cls, value):
        return None if isinstance(value, str) and not value.strip() else value


def save(goal_id: str, kind: str, item_id: str | None, revision: int, data: dict) -> str:
    if kind not in ("tasks", "milestones"):
        raise ValueError("Unknown work type.")
    values = (TaskInput if kind == "tasks" else MilestoneInput).model_validate(data)
    with write_transaction():
        if storage.find_goal(goal_id) is None:
            raise WorkConflict("This goal no longer exists.")
        if item_id and work_storage.find_item(goal_id, kind, item_id) is None:
            raise WorkConflict("This item no longer belongs to this goal.")
        if work_storage.revision(goal_id) != revision:
            raise WorkConflict("Your saved work changed. Your entries are unsaved; reopen the form before retrying.")
        if kind == "tasks" and values.milestone_id:
            if work_storage.find_item(goal_id, "milestones", values.milestone_id) is None:
                raise ValueError("Choose an active milestone belonging to this goal.")
        return work_storage.save_item(goal_id, kind, item_id, values)
