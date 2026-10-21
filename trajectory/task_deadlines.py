"""Calendar-date deadline calculations, independent of today's date and storage."""
from datetime import date, timedelta

DEADLINE_CHOICES = (("none", "No deadline"), ("2", "2 days"),
                    ("4", "4 days"), ("7", "1 week"))


def due_date(created_on: str, deadline_days: int | None) -> str | None:
    """A two-day deadline on October 21 is due through October 23."""
    if deadline_days is None:
        return None
    return (date.fromisoformat(created_on) + timedelta(days=deadline_days)).isoformat()


def task_details(task: dict, today: date) -> dict:
    due_on = due_date(task["created_on"], task["deadline_days"])
    return {
        **task,
        "deadline": str(task["deadline_days"]) if task["deadline_days"] is not None else "none",
        "due_on": due_on,
        "overdue": task["status"] == "undone" and due_on is not None and due_on < today.isoformat(),
        "due_today": task["status"] == "undone" and due_on == today.isoformat(),
    }
