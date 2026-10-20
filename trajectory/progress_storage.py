"""Dated actual-work persistence. Status and totals are derived, never stored twice."""
from uuid import uuid4
from .storage import get_db

SCHEMA = """
CREATE TABLE IF NOT EXISTS work_entries (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES approved_tasks(id) ON DELETE RESTRICT,
    work_date TEXT NOT NULL CHECK(length(work_date)=10),
    outcome TEXT NOT NULL CHECK(outcome IN ('partial','completed','reopened')),
    actual_minutes INTEGER CHECK(actual_minutes BETWEEN 0 AND 1440),
    notes TEXT NOT NULL DEFAULT '' CHECK(length(notes)<=2000),
    blocker_action TEXT NOT NULL DEFAULT 'none'
        CHECK(blocker_action IN ('none','raised','cleared')),
    blocker_text TEXT NOT NULL DEFAULT '' CHECK(length(blocker_text)<=1000),
    revision INTEGER NOT NULL DEFAULT 1 CHECK(revision>=1),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX IF NOT EXISTS work_entries_task_date
ON work_entries(task_id,work_date);
"""


def find_task(goal_id, task_id):
    row = get_db().execute(
        """SELECT t.*,l.milestone_id,m.title AS milestone_title
        FROM approved_tasks t LEFT JOIN work_task_links l ON l.task_id=t.id
        LEFT JOIN work_milestones m ON m.id=l.milestone_id
        WHERE t.goal_id=? AND t.id=?""", (goal_id, task_id)
    ).fetchone()
    return dict(row) if row else None


def find_entry(entry_id):
    row = get_db().execute(
        "SELECT rowid AS sequence,* FROM work_entries WHERE id=?", (entry_id,)
    ).fetchone()
    return dict(row) if row else None


def entries_for_task(task_id):
    return [dict(row) for row in get_db().execute(
        """SELECT rowid AS sequence,* FROM work_entries
        WHERE task_id=? ORDER BY work_date,sequence""", (task_id,)
    )]


def entries_for_goal(goal_id):
    return [dict(row) for row in get_db().execute(
        """SELECT e.rowid AS sequence,e.* FROM work_entries e
        JOIN approved_tasks t ON t.id=e.task_id WHERE t.goal_id=?
        ORDER BY e.task_id,e.work_date,sequence""", (goal_id,)
    )]


def archived_tasks(goal_id):
    return [dict(row) for row in get_db().execute(
        """SELECT id,title FROM approved_tasks WHERE goal_id=? AND archived=1
        ORDER BY title,id""", (goal_id,)
    )]


def insert_entry(entry_id, task_id, values):
    get_db().execute(
        """INSERT INTO work_entries
        (id,task_id,work_date,outcome,actual_minutes,notes,blocker_action,blocker_text)
        VALUES (?,?,?,?,?,?,?,?)""",
        (entry_id, task_id, values.work_date.isoformat(), values.outcome,
         values.actual_minutes, values.notes, values.blocker_action, values.blocker_text),
    )


def update_entry(entry_id, values):
    get_db().execute(
        """UPDATE work_entries SET work_date=?,outcome=?,actual_minutes=?,notes=?,
        blocker_action=?,blocker_text=?,revision=revision+1,
        updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?""",
        (values.work_date.isoformat(), values.outcome, values.actual_minutes,
         values.notes, values.blocker_action, values.blocker_text, entry_id),
    )


def delete_entry(entry_id):
    get_db().execute("DELETE FROM work_entries WHERE id=?", (entry_id,))
