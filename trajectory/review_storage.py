"""Review persistence; helpers participate in a service-owned write transaction."""
from contextlib import contextmanager
import json
from uuid import uuid4
from .storage import get_db

SCHEMA = """
CREATE TABLE IF NOT EXISTS draft_reviews (
    draft_id TEXT PRIMARY KEY REFERENCES plan_drafts(id) ON DELETE CASCADE,
    revision INTEGER NOT NULL DEFAULT 1 CHECK(revision >= 1),
    status TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft', 'approved', 'rejected'))
);
CREATE TABLE IF NOT EXISTS approved_plans (
    id TEXT PRIMARY KEY,
    goal_id TEXT NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    draft_id TEXT NOT NULL UNIQUE REFERENCES plan_drafts(id),
    draft_revision INTEGER NOT NULL CHECK(draft_revision >= 1),
    source_revision INTEGER NOT NULL,
    content TEXT NOT NULL,
    provenance TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('current', 'superseded')),
    approved_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE UNIQUE INDEX IF NOT EXISTS one_current_plan ON approved_plans(goal_id) WHERE status='current';
CREATE TABLE IF NOT EXISTS approved_tasks (
    id TEXT PRIMARY KEY,
    goal_id TEXT NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    estimated_minutes INTEGER,
    archived INTEGER NOT NULL DEFAULT 0 CHECK(archived IN (0, 1))
);
CREATE TABLE IF NOT EXISTS approved_plan_tasks (
    plan_id TEXT NOT NULL REFERENCES approved_plans(id),
    task_id TEXT NOT NULL REFERENCES approved_tasks(id),
    milestone_position INTEGER NOT NULL,
    task_position INTEGER NOT NULL,
    PRIMARY KEY(plan_id, milestone_position, task_position),
    UNIQUE(plan_id, task_id)
);
"""


@contextmanager
def write_transaction():
    connection = get_db()
    try:
        connection.execute("BEGIN IMMEDIATE")
        yield
        connection.commit()
    except Exception:
        connection.rollback()
        raise


def draft_for_review(draft_id):
    row = get_db().execute(
        """SELECT d.*, COALESCE(r.revision, 1) AS revision,
        COALESCE(r.status, 'draft') AS status FROM plan_drafts d
        LEFT JOIN draft_reviews r ON r.draft_id=d.id WHERE d.id=?""", (draft_id,)
    ).fetchone()
    if row is None:
        return None
    result = dict(row)
    result['proposal'] = json.loads(result['content'])
    result['provenance'] = json.loads(result['provenance'])
    return result


def current_plan(goal_id):
    row = get_db().execute("SELECT * FROM approved_plans WHERE goal_id=? AND status='current'", (goal_id,)).fetchone()
    if row is None:
        return None
    result = dict(row)
    result['proposal'] = json.loads(result['content'])
    return result


def plan_for_draft(draft_id):
    return get_db().execute("SELECT * FROM approved_plans WHERE draft_id=?", (draft_id,)).fetchone()


def change_review(draft_id, status, content=None):
    connection = get_db()
    connection.execute("INSERT OR IGNORE INTO draft_reviews (draft_id) VALUES (?)", (draft_id,))
    connection.execute("UPDATE draft_reviews SET revision=revision+1, status=? WHERE draft_id=?", (status, draft_id))
    if content is not None:
        connection.execute("UPDATE plan_drafts SET content=? WHERE id=?", (content, draft_id))


def insert_approved_plan(draft, proposal, previous):
    connection = get_db()
    plan_id = str(uuid4())
    connection.execute("UPDATE approved_plans SET status='superseded' WHERE goal_id=? AND status='current'", (draft['goal_id'],))
    connection.execute(
        """INSERT INTO approved_plans (id,goal_id,draft_id,draft_revision,source_revision,content,provenance,status)
        VALUES (?,?,?,?,?,?,?,'current')""",
        (plan_id, draft['goal_id'], draft['id'], draft['revision'], draft['source_revision'],
         proposal.model_dump_json(), json.dumps(draft['provenance'])),
    )
    carry_tasks_forward(plan_id, draft['goal_id'], proposal, previous)
    return plan_id


def carry_tasks_forward(plan_id, goal_id, proposal, previous):
    from .work_storage import apply_plan
    apply_plan(plan_id, goal_id, proposal, previous)
