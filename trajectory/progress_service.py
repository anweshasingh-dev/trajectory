"""Validate actual-work changes and derive task status from dated entries."""
from collections import defaultdict
from datetime import date
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from . import progress_storage, work_storage
from .review_storage import write_transaction


class ProgressConflict(Exception):
    pass


class EntryInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    work_date: date
    outcome: str = Field(pattern="^(partial|completed|reopened)$")
    actual_minutes: int | None = Field(default=None, ge=0, le=1440)
    notes: str = Field(default="", max_length=2000)
    blocker_action: str = Field(default="none", pattern="^(none|raised|cleared)$")
    blocker_text: str = Field(default="", max_length=1000)

    @field_validator("actual_minutes", mode="before")
    @classmethod
    def blank_minutes_are_unknown(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        if isinstance(value, str) and not value.strip().isdigit():
            raise ValueError("Enter whole minutes from 0 to 1440, or leave blank.")
        return value

    @model_validator(mode="after")
    def meaningful_entry(self):
        if self.work_date > date.today():
            raise ValueError("Actual work cannot be dated in the future.")
        if (self.blocker_action == "raised") != bool(self.blocker_text):
            raise ValueError("A raised blocker needs text; clear blocker text for other choices.")
        if self.outcome == "completed" and self.blocker_action == "raised":
            raise ValueError("Complete the task or raise a blocker, not both in one entry.")
        if (self.outcome == "partial" and not self.notes and self.blocker_action == "none"
                and not (self.actual_minutes is not None and self.actual_minutes > 0)):
            raise ValueError("Partial progress needs time, a note or a blocker change.")
        return self


def fold_entries(entries):
    """Chronological explicit outcomes decide status; elapsed time cannot complete a task."""
    result = dict(status="open", actual_minutes=0, measured_entries=0,
                  unmeasured_entries=0, blocker="")
    for entry in entries:
        if entry["actual_minutes"] is None:
            result["unmeasured_entries"] += 1
        else:
            result["actual_minutes"] += entry["actual_minutes"]
            result["measured_entries"] += 1
        result["status"] = {"partial": "in_progress", "completed": "completed",
                            "reopened": "open"}[entry["outcome"]]
        if entry["blocker_action"] == "raised":
            result["blocker"] = entry["blocker_text"]
        elif entry["blocker_action"] == "cleared" or entry["outcome"] == "completed":
            result["blocker"] = ""
    return result


def summaries_for_goal(goal_id, tasks, milestones):
    grouped = defaultdict(list)
    for entry in progress_storage.entries_for_goal(goal_id):
        grouped[entry["task_id"]].append(entry)
    summaries = {task["id"]: fold_entries(grouped[task["id"]]) for task in tasks}
    counts = {milestone["id"]: {"completed": 0, "total": 0} for milestone in milestones}
    for task in tasks:
        if task["milestone_id"] in counts:
            count = counts[task["milestone_id"]]
            count["total"] += 1
            count["completed"] += summaries[task["id"]]["status"] == "completed"
    return summaries, counts


def save_entry(goal_id, task_id, entry_id, revision, raw_values, request_id=None):
    values = EntryInput.model_validate(raw_values)
    with write_transaction():
        task = progress_storage.find_task(goal_id, task_id)
        if task is None:
            raise ProgressConflict("This task does not belong to this goal.")
        if entry_id:
            entry = progress_storage.find_entry(entry_id)
            if entry is None or entry["task_id"] != task_id:
                raise ProgressConflict("This work entry is unavailable for this task.")
            if entry["revision"] != revision:
                raise ProgressConflict("This entry changed. Reopen it before saving corrections.")
            progress_storage.update_entry(entry_id, values)
        else:
            try:
                new_id = str(UUID(request_id))
            except (ValueError, TypeError, AttributeError) as error:
                raise ProgressConflict("Reload the form before saving work.") from error
            existing = progress_storage.find_entry(new_id)
            if existing:
                if existing["task_id"] != task_id or any(
                    existing[key] != value for key, value in (
                        ("work_date", values.work_date.isoformat()),
                        ("outcome", values.outcome), ("actual_minutes", values.actual_minutes),
                        ("notes", values.notes), ("blocker_action", values.blocker_action),
                        ("blocker_text", values.blocker_text))
                ):
                    raise ProgressConflict("This entry request was already used. Reload the form.")
                return new_id
            if task["archived"]:
                raise ProgressConflict("This task is archived. You can correct its history, but cannot add work.")
            if work_storage.revision(goal_id) != revision:
                raise ProgressConflict("Saved work changed. Reopen this form before logging work.")
            progress_storage.insert_entry(new_id, task_id, values)
            entry_id = new_id
        work_storage.bump_revision(goal_id)
        return entry_id


def remove_entry(goal_id, task_id, entry_id, revision, confirmed):
    if not confirmed:
        raise ProgressConflict("Confirm removal of this work entry.")
    with write_transaction():
        if progress_storage.find_task(goal_id, task_id) is None:
            raise ProgressConflict("This task does not belong to this goal.")
        entry = progress_storage.find_entry(entry_id)
        if entry is None or entry["task_id"] != task_id:
            raise ProgressConflict("This work entry is unavailable for this task.")
        if entry["revision"] != revision:
            raise ProgressConflict("This entry changed. Review it before removing it.")
        progress_storage.delete_entry(entry_id)
        work_storage.bump_revision(goal_id)
