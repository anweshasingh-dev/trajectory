"""Versioned, transactional backfill of live work from immutable approved history."""
import json
from .storage import get_db
from .review_storage import write_transaction

SCHEMA = """
CREATE TABLE IF NOT EXISTS work_schema_migrations (
    version INTEGER PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS work_state (
    goal_id TEXT PRIMARY KEY REFERENCES goals(id) ON DELETE CASCADE,
    revision INTEGER NOT NULL DEFAULT 0 CHECK(revision >= 0)
);
CREATE TABLE IF NOT EXISTS work_milestones (
    id TEXT PRIMARY KEY,
    goal_id TEXT NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    title TEXT NOT NULL CHECK(length(trim(title)) BETWEEN 1 AND 160),
    completion_criterion TEXT NOT NULL CHECK(length(trim(completion_criterion)) BETWEEN 1 AND 800),
    position INTEGER NOT NULL CHECK(position >= 0),
    managed_by_plan INTEGER NOT NULL DEFAULT 1 CHECK(managed_by_plan IN (0, 1)),
    archived INTEGER NOT NULL DEFAULT 0 CHECK(archived IN (0, 1))
);
CREATE TABLE IF NOT EXISTS work_task_links (
    task_id TEXT PRIMARY KEY REFERENCES approved_tasks(id) ON DELETE CASCADE,
    milestone_id TEXT REFERENCES work_milestones(id),
    position INTEGER NOT NULL CHECK(position >= 0),
    managed_by_plan INTEGER NOT NULL DEFAULT 1 CHECK(managed_by_plan IN (0, 1))
);
CREATE TABLE IF NOT EXISTS approved_plan_milestones (
    plan_id TEXT NOT NULL REFERENCES approved_plans(id) ON DELETE CASCADE,
    milestone_position INTEGER NOT NULL CHECK(milestone_position >= 0),
    milestone_id TEXT NOT NULL REFERENCES work_milestones(id),
    PRIMARY KEY(plan_id, milestone_position),
    UNIQUE(plan_id, milestone_id)
);
"""


def migrate():
    from . import work_storage
    connection = get_db()
    with write_transaction():
        for statement in SCHEMA.split(";"):
            if statement.strip():
                connection.execute(statement)
        if connection.execute("SELECT 1 FROM work_schema_migrations WHERE version=1").fetchone():
            return
        previous_by_goal = {}
        for row in connection.execute("SELECT * FROM approved_plans ORDER BY rowid").fetchall():
            plan = dict(row)
            plan["proposal"] = json.loads(plan["content"])
            milestones = work_storage.import_milestones(
                plan["id"], plan["goal_id"], plan["proposal"], previous_by_goal.get(plan["goal_id"])
            )
            for member in connection.execute(
                "SELECT * FROM approved_plan_tasks WHERE plan_id=?", (plan["id"],)
            ).fetchall():
                connection.execute(
                    """INSERT INTO work_task_links(task_id,milestone_id,position) VALUES (?,?,?)
                    ON CONFLICT(task_id) DO UPDATE SET
                    milestone_id=excluded.milestone_id, position=excluded.position""",
                    (member["task_id"], milestones[member["milestone_position"]], member["task_position"]),
                )
            previous_by_goal[plan["goal_id"]] = plan
        connection.execute(
            """INSERT OR IGNORE INTO work_task_links(task_id,position)
            SELECT id,rowid FROM approved_tasks"""
        )
        connection.execute(
            """UPDATE work_milestones SET archived=1 WHERE id NOT IN (
                SELECT pm.milestone_id FROM approved_plan_milestones pm
                JOIN approved_plans p ON p.id=pm.plan_id WHERE p.status='current'
            ) AND NOT EXISTS (
                SELECT 1 FROM work_task_links l JOIN approved_tasks t ON t.id=l.task_id
                WHERE l.milestone_id=work_milestones.id AND t.archived=0
            )"""
        )
        connection.execute("INSERT INTO work_schema_migrations(version) VALUES (1)")
