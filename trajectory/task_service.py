"""Validate standalone tasks and serialize edits, status changes and removal."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from . import task_storage
from .review_storage import write_transaction


class TaskConflict(Exception):
    """The form no longer describes the current saved task."""


class TaskInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, strict=True)
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=1200)
    # Before Part 2 the input model accepted only title and description.
    deadline: Literal["none", "2", "4", "7"] = "none"


def validate_revision(revision: int | None) -> None:
    if type(revision) is not int or not 1 <= revision <= 9223372036854775807:
        raise ValueError("Reload the saved task before submitting this form.")


def check_current(task: dict, expected_revision: int) -> None:
    if task["revision"] != expected_revision:
        raise TaskConflict(
            "This task changed in another tab. Review the latest saved task before trying again."
        )


def save_task(data: dict, task_id: str | None = None,
              expected_revision: int | None = None) -> str:
    values = TaskInput.model_validate(data)
    deadline_days = None if values.deadline == "none" else int(values.deadline)
    if task_id is not None:
        validate_revision(expected_revision)
    with write_transaction():
        if task_id is None:
            # Previously: insert_task(values.title, values.description).
            return task_storage.insert_task(values.title, values.description, deadline_days)
        task = task_storage.find_task(task_id)
        if task is None:
            raise TaskConflict("This task was deleted. Your edits have not been saved.")
        check_current(task, expected_revision)
        if "deadline" not in values.model_fields_set:
            deadline_days = task["deadline_days"]
        task_storage.update_task(task_id, values.title, values.description, deadline_days)
        return task_id


def set_status(task_id: str, status: str, expected_revision: int) -> None:
    """Set an explicit state; repeated requests can never toggle it back."""
    if type(status) is not str or status not in ("done", "undone"):
        raise ValueError("Choose done or undone for the task status.")
    validate_revision(expected_revision)
    with write_transaction():
        task = task_storage.find_task(task_id)
        if task is None:
            raise TaskConflict("This task was deleted. Its status could not be changed.")
        check_current(task, expected_revision)
        if task["status"] != status:
            task_storage.update_status(task_id, status)


def remove_task(task_id: str, expected_revision: int, confirmed: bool) -> bool:
    """Return false for an already absent task; never recreate a deleted record."""
    if confirmed is not True:
        raise ValueError("Confirm permanent deletion of this task.")
    validate_revision(expected_revision)
    with write_transaction():
        task = task_storage.find_task(task_id)
        if task is None:
            return False
        check_current(task, expected_revision)
        task_storage.delete_task(task_id)
        return True
