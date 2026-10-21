# Task Master Part 2 review — October 21, 2026

Implemented and available at http://127.0.0.1:5000/tasks. Refresh previously open pages after the server restart.

## Behavior

- Mark done retains the task; Mark undone reopens the same record. Status and all task content survive restart/day changes.
- New/edit forms offer exactly No deadline, 2 days, 4 days or 1 week; the default is no deadline.
- Use the computer's local creation day, saved once. October 21 + 2 days is due through October 23; an unfinished task is overdue October 24. Only an explicit change to the deadline choice changes its duration, still counted from the original creation day. Completion and ordinary edits preserve it.
- Existing tasks keep every original field and receive no deadline. Migration 4 derives their missing local creation day from the original UTC timestamp using the computer's timezone at upgrade; Part 1 did not record the original timezone.
- No daily availability, AI plan generation, plan approval, detailed progress entries or analytics were added. Parts 3 and 4 remain pending.

## Before and after / execution flow

Previously the task form accepted title/notes and the database stored an initial undone state. Now the form also accepts an allowlisted deadline choice, and a separate POST carries the desired completion state. Routes parse transport controls; services validate and serialize writes; storage retains the original creation day and duration. Pure date functions derive the due date and receive today's date explicitly for display.

A status operation re-reads the saved task inside the existing short write transaction and compares its revision before changing anything. Fresh no-ops do not write; repeated stale submissions report a conflict and cannot toggle the task back. Actual changes increment the revision, also invalidating old edit/delete forms. Database failures roll back and render current saved state or preserve entered form values.

The migration keeps version 3's schema unchanged, rebuilds only the independent standalone table with version 4's date/duration constraints, copies every original field and commits the table replacement plus ledger entry together. A failure after replacement restores the original table and ledger; retry succeeds. No other data table is rewritten. Future daily-plan references require a separately reviewed migration/deletion policy.

The two short learning comments in task_service.py describe the previous input/insert behavior. The longer before/after explanation here covers the multi-file change. The 350-line Part 2 test module is retained as one cohesive workflow/upgrade regression file; production modules remain below the project's approximate 300-line guideline.

## Verification actually completed

- Task Master suite: **92 passed in 4.91s**, including 53 added Part 2 cases. Command: `.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider tests/test_task_master.py tests/test_task_storage.py tests/test_task_deadlines.py`.
- Full regression suite: **191 passed in 13.17s**. Command: `.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider`. Existing Goal Planner and preserved legacy progress regressions pass.
- Covered four choices, default/missing deadline, invalid/injected/duplicate fields, local midnight versus UTC timestamps, month/year/leap-day boundaries, DST calendar dates, inclusive due date, overdue display, deadline editing/removal, done/undone restart/day retention, stale/duplicate/concurrent requests, CSRF/method protection, rollback and upgrade retry with exact original-field preservation.
- Headless Chrome used a temporary database to create a task with a four-day deadline, mark it done, undo completion and edit to one week without moving its creation day. Checked all four actual selector options, a 153-character unbroken title and both list/form at an actual emulated 390px viewport without horizontal overflow. Desktop screenshot used 1440px. Inspected all three screenshots. This is focused layout/interaction coverage, not a complete accessibility audit.
- Python syntax parsing passed for changed Python modules. No dependencies, model configuration or legacy progress settings changed.

Browser screenshots and its isolated database are temporary artifacts under `C:/Users/anwes/AppData/Local/Temp/trajectory-task-master-part2-1kd8tv8t/`; no personal task content was used in browser tests.

## Local app upgrade

The previous loopback Flask server was running older source. After tests passed, it was stopped, SQLite's backup API created `instance/trajectory.before-task-master-part2-548d1706.sqlite`, and migration 4 was applied. Compared original-column values for all rows in all 13 pre-existing data tables, including all three standalone tasks; all matched the backup. Non-standalone table columns were unchanged. The ledger now contains 1/2/3/4; SQLite quick-check returned ok and foreign-key-check returned no violations.

Restarted Flask using the project interpreter, loopback address and a hidden background process. Goal Planner, Task Master, the new-task form and localhost Task Master returned HTTP 200. The live form contains the deadline selector. This upgrade did not create, edit, complete or delete personal tasks. Reload old forms because the restart replaces session/CSRF tokens.

Local generated files: the binary backup above has no source line range; runtime logs are `instance/flask-task-master-part2.stdout.log` and `instance/flask-task-master-part2.stderr.log`. They are ignored by Git. No login/startup service was installed.

## File inventory and verified final line ranges

Paths are relative to the workspace `C:/Users/anwes/Desktop/projects 2026/trajectory`. Existing unrelated edits and earlier Part 1 files were preserved; Git still lists several Part 1 files as untracked. No source file was renamed or deleted.

| File | Operation this part | Final lines for changed sections | Purpose |
| --- | --- | --- | --- |
| `trajectory/task_deadlines.py` | Created | 1–23 | Pure date arithmetic, exact choices and display metadata with an explicit today input. |
| `trajectory/task_storage.py` | Modified | 1–114 | Atomic migration 4; fixed local creation date and validated deadline duration; explicit status persistence. |
| `trajectory/task_service.py` | Modified | 1–77 | Deadline validation/preservation and revision-protected desired-state completion. |
| `trajectory/task_routes.py` | Modified | 2–7; 28–32; 35–38; 42–50; 55–91; 95–110; 114–143 | Parse forms, share deadline display data and return safe status/error feedback. |
| `trajectory/templates/task_master.html` | Modified | 1–35 | Saved state, mark-done/undone forms and deadline display; usable current-state list after a failed mutation. |
| `trajectory/templates/task_form.html` | Modified | 28–41 | Four-choice deadline selector, original creation day, current due date and field errors. |
| `trajectory/templates/_task_deadline.html` | Created | 1–5 | Shared due/no-deadline, due-today and overdue text. |
| `trajectory/templates/task_delete.html` | Modified | 13 | Show the saved deadline during permanent-deletion review. |
| `tests/test_task_deadlines.py` | Created | 1–350 | 53 Part 2 regression cases covering calendar semantics, persistence, conflicts, request validation, rollback and upgrade. |
| `tests/test_task_master.py` | Modified | 35 | Keep assertions limited to the still-pending planner/analytics controls. |
| `tests/test_task_storage.py` | Modified | 55; 89; 90; 101 | Expect migration 4 and supply a valid creation day so earlier constraint tests continue testing the intended field. |
| `README.md` | Modified | 5; 19; 23; 28; 56; 58 | Current Part 2 behavior, remaining scope and verification result. |
| `setup/Database.md` | Modified | 3; 12; 56–58; 68; 72; 127; 410–412; 421–429 | Storage contract, migration and local-calendar semantics; historical Part 1 details marked accordingly. |
| `setup/Product.md` | Modified | 59; 81; 91; 96; 110; 113; 137 | Reflect implemented status/deadlines while retaining the remaining planned daily workflow. |
| `setup/Tasks.md` | Modified | 8; 20; 38; 52; 71; 76–77; 83–91 | Record Part 2 completion, checks and defaults for review; leave Parts 3/4 pending. |
| `setup/DECISIONS.md` | Modified | 45–48 | Distinguish implementation defaults from explicitly supplied user preferences. |
| `setup/Running.md` | Modified | 3; 97; 99; 134–152 | Usage, date semantics, migration limits, actual tests/browser evidence and live restart. |
| `setup/Task_Master_Part2_Report.md` | Created | 1–68 | This review record and verified file inventory. |

## Review boundary

Review the done/undone controls, deadline choices and the inclusive creation-day semantics. Computer-local dates and explicit deadline edits are documented implementation defaults for this local app. Daily planning is still pending; completing Part 2 does not begin Part 3.
