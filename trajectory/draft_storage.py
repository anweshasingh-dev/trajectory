"""Durable proposals kept separate from any future accepted plan/task records."""
import json
from .storage import get_db

SCHEMA = """
CREATE TABLE IF NOT EXISTS plan_drafts (
    id TEXT PRIMARY KEY,
    goal_id TEXT NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    source_revision INTEGER NOT NULL CHECK(source_revision >= 1),
    content TEXT NOT NULL,
    provenance TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
"""


def find_draft(draft_id):
    return get_db().execute("SELECT * FROM plan_drafts WHERE id=?", (draft_id,)).fetchone()


def latest_draft(goal_id):
    row = get_db().execute(
        "SELECT * FROM plan_drafts WHERE goal_id=? ORDER BY rowid DESC LIMIT 1", (goal_id,)
    ).fetchone()
    if row is None:
        return None
    result = dict(row)
    result["proposal"] = json.loads(result.pop("content"))
    result["provenance"] = json.loads(result["provenance"])
    return result


def insert_draft(draft_id, goal_id, revision, proposal, provenance):
    # A conditional insert rechecks source freshness atomically after inference.
    with get_db() as connection:
        cursor = connection.execute(
            """INSERT INTO plan_drafts (id, goal_id, source_revision, content, provenance)
            SELECT ?, id, revision, ?, ? FROM goals WHERE id=? AND revision=?
            ON CONFLICT(id) DO NOTHING""",
            (draft_id, proposal.model_dump_json(), json.dumps(provenance), goal_id, revision),
        )
        return cursor.rowcount == 1
