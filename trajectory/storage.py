"""SQLite connections and parameterized goal queries."""
import sqlite3
from uuid import uuid4
from flask import current_app, g
from .clarification import FLAGS

SCHEMA = """
CREATE TABLE IF NOT EXISTS goals (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL CHECK(length(trim(title)) BETWEEN 1 AND 160),
    description TEXT NOT NULL,
    desired_outcome TEXT NOT NULL DEFAULT '',
    starting_point TEXT NOT NULL DEFAULT '',
    weekly_hours REAL CHECK(weekly_hours > 0 AND weekly_hours <= 168),
    target_date TEXT,
    revision INTEGER NOT NULL DEFAULT 1 CHECK(revision >= 1),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE TABLE IF NOT EXISTS goal_context_answers (
    goal_id TEXT NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    field TEXT NOT NULL CHECK(field IN ('outcome_unknown', 'starting_point_unknown', 'hours_unknown', 'no_deadline')),
    PRIMARY KEY (goal_id, field)
);
"""


def get_db():
    if "db" not in g:
        connection = sqlite3.connect(current_app.config["DATABASE"], timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        g.db = connection
    return g.db


def close_db(error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def initialize():
    # Non-destructive bootstrap for the first schema; future changes need migrations.
    get_db().executescript(SCHEMA)


def list_goals():
    return get_db().execute(
        "SELECT * FROM goals ORDER BY updated_at DESC, id"
    ).fetchall()


def find_goal(goal_id):
    row = get_db().execute("SELECT * FROM goals WHERE id = ?", (goal_id,)).fetchone()
    if row is None:
        return None
    goal = dict(row)
    answers = get_db().execute(
        "SELECT field FROM goal_context_answers WHERE goal_id = ?", (goal_id,)
    ).fetchall()
    selected = {answer["field"] for answer in answers}
    goal.update({flag: flag in selected for flag in FLAGS})
    return goal


def insert_goal(values, answers=()):
    goal_id = str(uuid4())
    with get_db() as connection:
        connection.execute(
            """INSERT INTO goals
            (id, title, description, desired_outcome, starting_point, weekly_hours, target_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (goal_id, *values),
        )
        replace_answers(connection, goal_id, answers)
    return goal_id


def update_goal(goal_id, revision, values, answers=()):
    with get_db() as connection:
        cursor = connection.execute(
            """UPDATE goals SET title=?, description=?, desired_outcome=?,
            starting_point=?, weekly_hours=?, target_date=?, revision=revision+1,
            updated_at=strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
            WHERE id=? AND revision=?""",
            (*values, goal_id, revision),
        )
        if cursor.rowcount != 1:
            return False
        replace_answers(connection, goal_id, answers)
        return True


def replace_answers(connection, goal_id, answers):
    # Called inside the same transaction as the goal change.
    connection.execute("DELETE FROM goal_context_answers WHERE goal_id = ?", (goal_id,))
    connection.executemany(
        "INSERT INTO goal_context_answers (goal_id, field) VALUES (?, ?)",
        [(goal_id, field) for field in answers],
    )
