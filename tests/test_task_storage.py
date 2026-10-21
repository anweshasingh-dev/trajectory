"""Additive migration, constraints and isolation from existing goal-plan data."""
import sqlite3
from unittest.mock import patch
import pytest
from trajectory import create_app, storage, task_storage
from test_goals import app
from test_task_master import create, post, rows
from test_work import legacy_database


def old_work(database):
    with sqlite3.connect(database) as connection:
        return {
            table: connection.execute(f"SELECT * FROM {table} ORDER BY rowid").fetchall()
            for table in ("goals", "plan_drafts", "approved_plans", "approved_tasks",
                          "approved_plan_tasks", "work_milestones", "work_task_links",
                          "approved_plan_milestones", "work_state", "work_entries")
        }


def existing_database(tmp_path):
    database = legacy_database(tmp_path)
    with patch("trajectory.task_storage.migrate"):
        create_app({"TESTING": True, "DATABASE": database})
    with sqlite3.connect(database) as connection:
        connection.execute(
            """INSERT INTO work_entries(id,task_id,work_date,outcome,notes)
            VALUES ('entry','task','2026-10-20','completed','Preserve legacy history')"""
        )
    return database


def test_additive_migration_and_standalone_crud_preserve_all_legacy_records(tmp_path):
    database = existing_database(tmp_path)
    before = old_work(database)
    config = {"TESTING": True, "SECRET_KEY": "test-only", "DATABASE": database}
    app = create_app(config)
    client = app.test_client()
    assert create(client).status_code == 303
    task = rows(app)[0]
    assert post(client, f'/tasks/{task["id"]}/edit', title="Updated", revision="1").status_code == 303
    # Goal-linked IDs are never accepted by standalone edit/delete actions.
    assert client.get("/tasks/task/edit").status_code == 404
    assert post(client, "/tasks/task/delete", revision="1", confirmed="on").status_code == 303
    assert old_work(database) == before
    assert post(client, f'/tasks/{task["id"]}/delete', revision="2", confirmed="on").status_code == 303
    create_app(config)
    assert old_work(database) == before
    with app.app_context():
        connection = storage.get_db()
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
        assert [row[0] for row in connection.execute(
            "SELECT version FROM work_schema_migrations ORDER BY version"
        )] == [1, 2, 3, 4]


def test_failed_migration_rolls_back_table_and_version_and_can_retry(tmp_path):
    database = existing_database(tmp_path)
    before = old_work(database)
    with sqlite3.connect(database) as connection:
        connection.execute(
            """CREATE TRIGGER fail_task_migration BEFORE INSERT ON work_schema_migrations
            WHEN NEW.version=3 BEGIN SELECT RAISE(ABORT, 'synthetic migration failure'); END"""
        )
    config = {"TESTING": True, "DATABASE": database}
    with pytest.raises(sqlite3.IntegrityError):
        create_app(config)
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT name FROM sqlite_master WHERE name='standalone_tasks'"
        ).fetchone() is None
        assert connection.execute("SELECT 1 FROM work_schema_migrations WHERE version=3").fetchone() is None
        connection.execute("DROP TRIGGER fail_task_migration")
    assert old_work(database) == before
    assert create_app(config).test_client().get("/tasks").status_code == 200


@pytest.mark.parametrize("field,value", [
    ("title", ""), ("title", " " * 2), ("title", "x" * 161),
    ("description", "x" * 1201), ("status", "archived"),
    ("revision", 0), ("revision", 1.5),
])
def test_database_constraints_reject_invalid_rows(app, field, value):
    with app.app_context():
        connection = storage.get_db()
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                f"INSERT INTO standalone_tasks(id,title,created_on,{field}) VALUES ('bad','Valid','2026-10-21',?)"
                if field != "title" else "INSERT INTO standalone_tasks(id,title,created_on) VALUES ('bad',?,'2026-10-21')",
                (value,),
            )
        connection.rollback()
        assert task_storage.list_tasks() == []


def test_existing_status_is_preserved_by_ordinary_edit(app):
    client = app.test_client()
    create(client)
    task = rows(app)[0]
    # Seed an existing done task and verify the ordinary edit preserves its state.
    with sqlite3.connect(app.config["DATABASE"]) as connection:
        connection.execute("UPDATE standalone_tasks SET status='done' WHERE id=?", (task["id"],))
    assert post(client, f'/tasks/{task["id"]}/edit', title="Renamed", revision="1").status_code == 303
    assert rows(app)[0]["status"] == "done"
    assert b"Done" in client.get(f'/tasks/{task["id"]}/delete').data
