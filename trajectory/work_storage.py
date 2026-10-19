"""Live work queries and approved-snapshot imports; callers own transactions."""
from collections import defaultdict, deque
from uuid import uuid4
from .storage import get_db


def revision(goal_id):
    row = get_db().execute("SELECT revision FROM work_state WHERE goal_id=?", (goal_id,)).fetchone()
    return row["revision"] if row else 0


def bump_revision(goal_id):
    get_db().execute(
        """INSERT INTO work_state(goal_id,revision) VALUES (?,1)
        ON CONFLICT(goal_id) DO UPDATE SET revision=revision+1""", (goal_id,)
    )


def milestones(goal_id):
    return [dict(row) for row in get_db().execute(
        "SELECT * FROM work_milestones WHERE goal_id=? AND archived=0 ORDER BY position,id", (goal_id,)
    )]


def tasks(goal_id):
    return [dict(row) for row in get_db().execute(
        """SELECT t.*,l.milestone_id,l.position,l.managed_by_plan FROM approved_tasks t
        JOIN work_task_links l ON l.task_id=t.id WHERE t.goal_id=? AND t.archived=0
        ORDER BY l.position,t.id""", (goal_id,)
    )]


def find_item(goal_id, kind, item_id):
    # Read editable values and their revision in one SQLite snapshot.
    if kind == "milestones":
        query = """SELECT m.*,COALESCE(s.revision,0) AS work_revision FROM work_milestones m
        LEFT JOIN work_state s ON s.goal_id=m.goal_id
        WHERE m.id=? AND m.goal_id=? AND m.archived=0"""
    else:
        query = """SELECT t.*,l.milestone_id,l.position,l.managed_by_plan,
        COALESCE(s.revision,0) AS work_revision FROM approved_tasks t
        JOIN work_task_links l ON l.task_id=t.id LEFT JOIN work_state s ON s.goal_id=t.goal_id
        WHERE t.id=? AND t.goal_id=? AND t.archived=0"""
    row = get_db().execute(query, (item_id, goal_id)).fetchone()
    return dict(row) if row else None


def task_signature(task):
    return (task["title"], task["description"], task["estimated_minutes"])


def import_milestones(plan_id, goal_id, proposal, previous):
    connection = get_db()
    reusable = defaultdict(deque)
    if previous:
        members = connection.execute(
            """SELECT m.*,pm.milestone_position FROM work_milestones m
            JOIN approved_plan_milestones pm ON pm.milestone_id=m.id
            WHERE pm.plan_id=? ORDER BY pm.milestone_position""", (previous["id"],)
        ).fetchall()
        for member in members:
            original = previous["proposal"]["milestones"][member["milestone_position"]]
            for signature in {(member["title"], member["completion_criterion"]),
                              (original["title"], original["completion_criterion"])}:
                reusable[signature].append(member["id"])
    # An exact match can also reuse manually created work without duplicating it.
    for member in milestones(goal_id):
        reusable[(member["title"], member["completion_criterion"])].append(member["id"])
    assigned, used = [], set()
    for position, milestone in enumerate(proposal["milestones"]):
        candidates = reusable[(milestone["title"], milestone["completion_criterion"])]
        while candidates and candidates[0] in used:
            candidates.popleft()
        milestone_id = candidates.popleft() if candidates else str(uuid4())
        used.add(milestone_id)
        connection.execute(
            """INSERT INTO work_milestones(id,goal_id,title,completion_criterion,position)
            VALUES (?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET archived=0,
            position=CASE WHEN managed_by_plan=1 THEN excluded.position ELSE position END""",
            (milestone_id, goal_id, milestone["title"], milestone["completion_criterion"], position),
        )
        connection.execute(
            "INSERT INTO approved_plan_milestones VALUES (?,?,?)", (plan_id, position, milestone_id)
        )
        assigned.append(milestone_id)
    return assigned


def apply_plan(plan_id, goal_id, proposal, previous):
    """Reconcile exact matches; direct edits remain user-managed and retain IDs."""
    connection = get_db()
    content = proposal.model_dump()
    milestone_ids = import_milestones(plan_id, goal_id, content, previous)
    reusable = defaultdict(deque)
    if previous:
        rows = connection.execute(
            """SELECT t.*,m.milestone_position,m.task_position FROM approved_tasks t
            JOIN approved_plan_tasks m ON m.task_id=t.id WHERE m.plan_id=?
            ORDER BY m.milestone_position,m.task_position""", (previous["id"],)
        ).fetchall()
        for row in rows:
            original = previous["proposal"]["milestones"][row["milestone_position"]]["tasks"][row["task_position"]]
            for signature in {task_signature(row), task_signature(original)}:
                reusable[signature].append(row["id"])
    for task in tasks(goal_id):
        reusable[task_signature(task)].append(task["id"])
    connection.execute(
        """UPDATE approved_tasks SET archived=1 WHERE goal_id=? AND id IN (
        SELECT task_id FROM work_task_links WHERE managed_by_plan=1)""", (goal_id,)
    )
    used = set()
    for milestone_position, milestone in enumerate(content["milestones"]):
        for task_position, task in enumerate(milestone["tasks"]):
            candidates = reusable[task_signature(task)]
            while candidates and candidates[0] in used:
                candidates.popleft()
            task_id = candidates.popleft() if candidates else str(uuid4())
            used.add(task_id)
            connection.execute(
                """INSERT INTO approved_tasks(id,goal_id,title,description,estimated_minutes)
                VALUES (?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET archived=0""",
                (task_id, goal_id, *task_signature(task)),
            )
            connection.execute(
                """INSERT INTO work_task_links(task_id,milestone_id,position) VALUES (?,?,?)
                ON CONFLICT(task_id) DO UPDATE SET
                milestone_id=CASE WHEN managed_by_plan=1 THEN excluded.milestone_id ELSE milestone_id END,
                position=CASE WHEN managed_by_plan=1 THEN excluded.position ELSE position END""",
                (task_id, milestone_ids[milestone_position], task_position),
            )
            connection.execute(
                "INSERT INTO approved_plan_tasks VALUES (?,?,?,?)",
                (plan_id, task_id, milestone_position, task_position),
            )
    connection.execute(
        """UPDATE work_milestones SET archived=1 WHERE goal_id=? AND managed_by_plan=1
        AND id NOT IN (SELECT milestone_id FROM approved_plan_milestones WHERE plan_id=?)
        AND NOT EXISTS (SELECT 1 FROM work_task_links l JOIN approved_tasks t ON t.id=l.task_id
                        WHERE l.milestone_id=work_milestones.id AND t.archived=0)""",
        (goal_id, plan_id),
    )
    bump_revision(goal_id)


def save_item(goal_id, kind, item_id, values):
    connection = get_db()
    if kind == "milestones":
        if item_id:
            connection.execute(
                """UPDATE work_milestones SET title=?,completion_criterion=?,managed_by_plan=0
                WHERE id=? AND goal_id=?""",
                (values.title, values.completion_criterion, item_id, goal_id),
            )
        else:
            item_id = str(uuid4())
            connection.execute(
                """INSERT INTO work_milestones(id,goal_id,title,completion_criterion,position,managed_by_plan)
                SELECT ?,?,?,?,COALESCE(MAX(position),-1)+1,0 FROM work_milestones WHERE goal_id=?""",
                (item_id, goal_id, values.title, values.completion_criterion, goal_id),
            )
    else:
        if item_id:
            connection.execute(
                "UPDATE approved_tasks SET title=?,description=?,estimated_minutes=? WHERE id=? AND goal_id=?",
                (values.title, values.description, values.estimated_minutes, item_id, goal_id),
            )
        else:
            item_id = str(uuid4())
            connection.execute(
                "INSERT INTO approved_tasks(id,goal_id,title,description,estimated_minutes) VALUES (?,?,?,?,?)",
                (item_id, goal_id, values.title, values.description, values.estimated_minutes),
            )
        connection.execute(
            """INSERT INTO work_task_links(task_id,milestone_id,position,managed_by_plan)
            SELECT ?,?,COALESCE(MAX(position),-1)+1,0 FROM work_task_links WHERE 1
            ON CONFLICT(task_id) DO UPDATE SET milestone_id=excluded.milestone_id,managed_by_plan=0,
            position=CASE WHEN milestone_id IS excluded.milestone_id THEN position ELSE excluded.position END""",
            (item_id, values.milestone_id),
        )
    bump_revision(goal_id)
    # The goal revision covers planning context too: invalidate older/in-flight proposals.
    connection.execute(
        """UPDATE goals SET revision=revision+1,updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now')
        WHERE id=?""", (goal_id,)
    )
    return item_id
