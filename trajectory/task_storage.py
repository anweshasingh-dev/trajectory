"""Standalone task persistence; services own mutation transaction boundaries."""
from datetime import datetime, timezone
from uuid import uuid4
from .storage import get_db
from .review_storage import write_transaction

# Keep migration 3 unchanged so existing installations follow the same upgrade path.
SCHEMA = """
CREATE TABLE standalone_tasks (
    id TEXT PRIMARY KEY NOT NULL,
    title TEXT NOT NULL CHECK(length(trim(title)) BETWEEN 1 AND 160),
    description TEXT NOT NULL DEFAULT '' CHECK(length(description) <= 1200),
    status TEXT NOT NULL DEFAULT 'undone' CHECK(status IN ('undone', 'done')),
    revision INTEGER NOT NULL DEFAULT 1 CHECK(typeof(revision) = 'integer' AND revision >= 1),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
)
"""

DEADLINE_SCHEMA = """
CREATE TABLE standalone_tasks_next (
    id TEXT PRIMARY KEY NOT NULL,
    title TEXT NOT NULL CHECK(length(trim(title)) BETWEEN 1 AND 160),
    description TEXT NOT NULL DEFAULT '' CHECK(length(description) <= 1200),
    status TEXT NOT NULL DEFAULT 'undone' CHECK(status IN ('undone', 'done')),
    revision INTEGER NOT NULL DEFAULT 1 CHECK(typeof(revision) = 'integer' AND revision >= 1),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    created_on TEXT NOT NULL CHECK(
        length(created_on) = 10 AND date(created_on, '+0 days') IS NOT NULL
        AND date(created_on, '+0 days') = created_on),
    deadline_days INTEGER CHECK(
        deadline_days IS NULL OR
        (typeof(deadline_days) = 'integer' AND deadline_days IN (2, 4, 7)))
)
"""


def migrate() -> None:
    """Preserve every task field while adding a fixed local creation date."""
    connection = get_db()
    with write_transaction():
        if not connection.execute(
            "SELECT 1 FROM work_schema_migrations WHERE version=3"
        ).fetchone():
            connection.execute(SCHEMA)
            connection.execute("INSERT INTO work_schema_migrations(version) VALUES (3)")
        if connection.execute(
            "SELECT 1 FROM work_schema_migrations WHERE version=4"
        ).fetchone():
            return
        # Rebuild only the standalone table to enforce a non-null date on old and new rows.
        # No other table references standalone tasks in Parts 1 or 2.
        connection.execute(DEADLINE_SCHEMA)
        for row in connection.execute("SELECT * FROM standalone_tasks").fetchall():
            created_on = datetime.fromisoformat(row["created_at"]).astimezone().date().isoformat()
            connection.execute(
                """INSERT INTO standalone_tasks_next
                (id,title,description,status,revision,created_at,updated_at,created_on)
                VALUES (?,?,?,?,?,?,?,?)""",
                (*tuple(row), created_on),
            )
        connection.execute("DROP TABLE standalone_tasks")
        connection.execute("ALTER TABLE standalone_tasks_next RENAME TO standalone_tasks")
        connection.execute("INSERT INTO work_schema_migrations(version) VALUES (4)")


def list_tasks() -> list[dict]:
    rows = get_db().execute(
        "SELECT * FROM standalone_tasks ORDER BY created_at DESC, id"
    ).fetchall()
    return [dict(row) for row in rows]


def find_task(task_id: str) -> dict | None:
    row = get_db().execute(
        "SELECT * FROM standalone_tasks WHERE id=?", (task_id,)
    ).fetchone()
    return dict(row) if row else None


def insert_task(title: str, description: str, deadline_days: int | None = None) -> str:
    task_id = str(uuid4())
    # Capture the UTC instant and local calendar day from the same clock reading.
    now = datetime.now().astimezone()
    timestamp = now.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    get_db().execute(
        """INSERT INTO standalone_tasks
        (id,title,description,created_at,updated_at,created_on,deadline_days)
        VALUES (?,?,?,?,?,?,?)""",
        (task_id, title, description, timestamp, timestamp, now.date().isoformat(), deadline_days),
    )
    return task_id


def update_task(task_id: str, title: str, description: str, deadline_days: int | None) -> None:
    get_db().execute(
        """UPDATE standalone_tasks SET title=?,description=?,deadline_days=?,revision=revision+1,
        updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?""",
        (title, description, deadline_days, task_id),
    )


def update_status(task_id: str, status: str) -> None:
    get_db().execute(
        """UPDATE standalone_tasks SET status=?,revision=revision+1,
        updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?""",
        (status, task_id),
    )


def delete_task(task_id: str) -> None:
    # Future task references must restrict deletion until their cleanup is reviewed.
    get_db().execute("DELETE FROM standalone_tasks WHERE id=?", (task_id,))
