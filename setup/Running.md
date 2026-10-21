# Running the first application slice

Implemented in the current UI: goal capture with genuinely optional context, local model proposals, draft editing/review/approval, saving, and persistent goal-linked milestone/task editing. Legacy dated-work tracking code and data are preserved but hidden by default. Task Master Part 1 adds a separate page for standalone task creation, listing, editing and confirmed permanent deletion, with restart persistence. Part 2 adds saved done/undone controls and creation-based deadlines. Daily AI planning and goal/goal-linked-task deletion remain pending; this is not the complete MVP.

Verified environment: Windows, Python 3.14.5. From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app trajectory run --host 127.0.0.1
```

Open http://127.0.0.1:5000. Stop with Ctrl+C. No activation is required. Keep the server bound to loopback; this build has no account system or hosted deployment configuration. Debug mode is off.

The database is created automatically at `instance/trajectory.sqlite` and is ignored by Git. Startup preserves existing rows. Back up this file while the app is stopped if needed; it contains personal goal text. Tests use isolated temporary databases.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Implementation uses a Flask application factory, a goal input model, route/service/persistence modules and shared Jinja/CSS assets. The initial `goals` table is the minimal Phase 1 goal-context slice; the broader schema in Database.md remains a proposal for later alignment. Future schema changes need explicit migrations. Optional blank hours/date are stored as NULL. Time and target dates are user context, not computed forecasts.

A per-process random session key protects form tokens. Restarting the server expires open forms; reload before saving after a restart. Goal data remains on disk. Generating a proposal sends only the selected goal context to Ollama on 127.0.0.1. It does not send other goals or use hosted inference.

References: [Flask application factory](https://flask.palletsprojects.com/en/stable/tutorial/factory/) and [SQLite connection lifecycle](https://flask.palletsprojects.com/en/stable/tutorial/database/).

## Clarification slice

Existing databases retain the additive `goal_context_answers` table and saved goal rows. Explicit alternatives remain separate from blank values and save atomically with the goal revision. A title and description are enough to generate a proposal; all four context fields are optional, with no required unknown/no-deadline acknowledgement. Missing details appear as optional suggestions and do not block the generate button or service. Supplied values still receive validation; blank hours/date remain NULL and no unknown flags are silently asserted. Dates in prose never become confirmed deadlines. Use Edit goal to add or revise context.

## Local AI generation (Part 3)

Prerequisite: Ollama running locally with `qwen3:4b` installed:

```powershell
ollama pull qwen3:4b
```

The default is Qwen3 4B Q4_K_M (approximately 2.5 GB), published under Apache 2.0. The pre-existing qwen2.5:3b model has a different, non-commercial research license and is not the selected default. No model weights are bundled with this repository. Model license/attribution obligations remain applicable if weights are redistributed. No challenge eligibility is claimed.

Sources reviewed October 19, 2026: [Ollama artifact and license](https://ollama.com/library/qwen3:4b), [upstream license](https://huggingface.co/Qwen/Qwen3-4B/blob/main/LICENSE), [structured outputs](https://docs.ollama.com/capabilities/structured-outputs), [chat API](https://docs.ollama.com/api/chat).

Open a saved goal and select Generate proposal, even when optional context is blank. Add optional details later if useful. The request is synchronous with static pending feedback. A complete response is validated before saving; generation cannot approve tasks or modify goal facts. The adapter uses standard-library HTTP, disables proxies for local requests, sets a 120-second request timeout, limits the response to 128 KiB, requests at most 2,200 output tokens, uses an 8,192-token context and disables thinking/streaming. There is no automatic retry or paid service. A browser disconnect does not guarantee cancellation of local inference.

Plans are ordered milestones, each with a completion criterion and ordered tasks. Effort estimates are suggestions; unknown estimates remain null. Assumptions and remaining model questions are visible. Validation proves structure and bounds, not factual accuracy or practical plan quality. Users must review the content.

An additive `plan_drafts` table stores the draft JSON, goal source revision, model name/digest, prompt version and returned performance counters. Generation alone creates no approved tasks; Part 4 approval creates the separate approved-plan/task records described below. Earlier drafts are retained; the workspace displays the most recently saved draft and labels it outdated if goal context changed. A replacement attempt does not erase a previous draft when inference fails. Source revision is checked again atomically when saving, so a result generated against changed/deleted goal context is rejected. Reposting the same generation request ID cannot create duplicate drafts. Editing and approval are available through the Part 4 review workflow.

Tests use fake model adapters for repeatable failure checks. Real model results, once recorded, are separate evidence; one successful example is a smoke check, not a broad quality evaluation. Configuration defaults are in the application factory; runtime-specific details stay in `trajectory/ai.py`.

### Live verification recorded October 19, 2026

[Model_Verification.json](Model_Verification.json) records the exact local digest, synthetic inputs, responses, timings, prompt versions and manual findings. Two v2 live requests completed in 9.04 and 9.63 seconds; both saved drafts reopened after a fresh application instance. A cold v1 request took 33.73 seconds. Ollama reported full GPU execution with an 8,192-token context and 3.9 GB loaded memory. These are observations on this machine, not latency promises.

The first content review found an unsupported duration and accuracy example; prompt v2 removed those from the reviewed outputs and added the requested documentation deliverable. Residual model limitations remain: known facts can be repeated as assumptions, and availability/routine assumptions may still be proposed. They remain visibly unconfirmed and never update goal context. Most reviewed effort estimates were unknown. Review all generated suggestions before using them. All 35 automated regression cases passed separately.

## Draft editing and approval (Part 4)

1. Open a generated draft and choose **Edit draft**. Revise the summary, assumptions/questions, milestone checkpoints and task text/effort. Add/remove/reorder milestones and tasks through labeled buttons. Limits remain four milestones and five tasks per milestone; each milestone needs at least one task. Blank effort stays unknown.
2. Choose **Save draft for review**. This revalidates and saves a new draft revision, then returns to the workspace. Saving is separate from approval. Cancel leaves the saved revision intact; the browser warns before leaving unsaved edits.
3. Review the saved proposal, confirm the review checkbox, then choose **Approve this plan**. If there is an existing approved plan, **Approve replacement plan** explicitly replaces it and retains the historical snapshot. Assumptions remain proposed assumptions; approval does not turn them into goal facts or a daily schedule.
4. Alternatively, expand **Reject this draft**, confirm rejection, and submit. Rejection preserves any current approved plan and does not delete the draft record.

Approval, rejection and draft edits recheck the goal source revision and draft revision inside a short `BEGIN IMMEDIATE` transaction. Approval also compares the current approved-plan ID to the version shown during review. A competing approval requires fresh review. Duplicate approval acknowledges the same current snapshot without adding tasks or reactivating a superseded plan. No inference runs inside a database write transaction. Failures roll back every change.

The additive tables are `draft_reviews`, `approved_plans`, `approved_tasks` and `approved_plan_tasks`; existing goal/draft rows are preserved. Older drafts without a review row are read as revision 1 in Draft state. Approved snapshots are immutable and one plan per goal can be current. Original AI provenance is retained, while the approved draft revision identifies the human-reviewed content.

Proposal imports reuse matching task identities and preserve direct edits. Removed proposal-managed tasks are archived, while manual work and historical approved snapshots remain. Dated work entries stay linked to task IDs through plan replacement and can be corrected after a task is archived.

A changed goal labels the existing approved plan as needing review rather than deleting it. Old-source drafts cannot be edited or approved. Open questions/assumptions remain visible; users can revise or remove them before approval. The editor does not change confirmed goal context.

Verification: 50 automated cases pass, including rejection, stale/duplicate/concurrent approval, invalid edited data, exact-revision persistence, retained task identity and rollback after a partial replacement attempt. An isolated headless Chrome check passes add/remove/reorder, input naming, bounds and entered-data retention. [Review_Verification.json](Review_Verification.json) records the separate real-model edit/approve/restart smoke check. This is not a broad visual accessibility audit or a quality guarantee for model suggestions.


## Saved work and preserved legacy progress

Open a goal and choose **Manage milestones and tasks**. Add or edit tasks directly, link them to a milestone, or leave them under the goal. Task identities survive direct edits and matching plan replacements. The current saved-work page lists editable milestones/tasks and effort estimates; progress states and completion counts are hidden.

**Historical legacy workflow — hidden from the current UI:** Choose **View work history** on a task to record a dated partial-progress, completion or reopening entry. Actual minutes may be blank (unknown) or 0 (known zero); notes and blockers are optional. A blocker remains visible until cleared or the task is completed. Completion requires an explicit entry; minutes alone never complete a task. **Correct entry** updates a mistaken record, and **Remove mistaken entry** removes it after confirmation. Task state, blockers and recorded-time totals are recalculated from dated entries. Archived tasks retain readable, correctable history.

Startup applies versioned SQLite migrations without recreating existing goals, plans or task IDs. Tests use temporary databases. The local browser must reach a restarted Flask server to load new routes and templates. The earlier automated verification passed 87 cases; this does not establish visual accessibility or broad model quality. Daily intentions, capacity-aware schedules and carry-forward are later Core MVP parts.

## Goal Planner stabilization milestone — October 20, 2026

Optional context no longer blocks generation in the service or UI. Prompt goal-plan-v4 requests a useful work breakdown from the goal description when optional fields are missing, with deliverables covered and follow-up questions kept optional. Existing edit/review/approval/save and concurrency behavior remain intact.

LEGACY_PROGRESS_UI defaults to false in the application factory. Current work pages omit progress controls, history, blockers, actual-time totals and milestone completion counts; bookmarked legacy progress routes return 404 before their handlers run. Progress services, templates, routes, migrations and stored records remain preserved. Legacy regression tests explicitly opt into the server-controlled switch; the application has no user-facing toggle. No schema changes or new dependencies were introduced.

Verification used temporary databases:

- Baseline: 87 tests passed.
- Optional-context stage: 54 goal/clarification/generation/review tests passed.
- Progress UI stage: 61 UI/work/progress/review tests passed, including the preserved legacy workflow.
- Final full suite: 99 tests passed with `.\.venv\Scripts\python.exe -m pytest -q`.
- Two synthetic real Qwen3 4B checks generated with all optional context blank, then edited, approved and reopened the plan after restart without changing unknown goal facts. Prompt v3 took 20.05 seconds but omitted requested totals and usage instructions; the refined v4 check took 14.43 seconds and included both. These are observations, not latency or quality guarantees. No personal database was used or altered.

The v4 output still proposed unconfirmed Python-experience and storage assumptions. They stayed visible for review and never became saved goal facts. Automated checks use fake adapters; the two local smoke checks are separate evidence, not broad model-quality or visual-accessibility validation. At that stabilization milestone Task Master and daily planning were unimplemented; the later Part 1 milestone below records standalone task management. Task creation day is the confirmed deadline anchor. The Part 2 milestone below records its local timezone, due-day and overdue implementation choices; daily-plan lifecycle details remain open.

## Task Master Part 1 - October 21, 2026 (historical milestone)

Use the shared **Task Master** navigation link, or open http://127.0.0.1:5000/tasks after restarting Flask with the command above. Goal Planner keeps its existing routes. The page lists ordinary standalone tasks; **New task** requires a title (1-160 trimmed characters) and optional notes (up to 1,200 trimmed characters). **Edit task** preserves identity and creation time. **Delete task** opens a confirmation page; cancel is read-only, and confirmed deletion permanently removes the live row and its notes.

Part 1 creates tasks with stored status `undone`; completion controls and deadlines are Part 2 work. Daily availability, AI priorities/allocations and review/approval are Part 3; combined next-day planning continuity is Part 4. No planner controls, placeholder panels, detailed progress tracking or analytics are added here. The user confirmed that future deadlines start on the task's creation day, using local calendar days; timezone and due-day-boundary details still need decisions before implementing deadlines.

The new route/service/storage modules use the existing CSRF protection, SQLite connection and short write-transaction helper. The task-input model rejects extra fields. Edits and deletion compare the submitted revision after serializing writes; stale forms cannot overwrite or remove newer work. Failed mutations roll back and retain entered form text. An already deleted task is not recreated by an old edit form; a repeated confirmed deletion reports that it is already absent.

Startup adds `standalone_tasks` through version 3 in `work_schema_migrations`, leaving existing goals, approved snapshots, goal-linked tasks, milestone links and preserved legacy work entries intact. Migration failure rolls back the new table and version marker and permits a later retry. The new table does not reference goals or milestones. Future daily-plan dependencies require extending deletion cleanup before referenced tasks can be removed. Development tests and browser checks used temporary databases. The later startup recovery below records the separately authorized backup and migration of the local application database.

Verification actually run:

- Baseline: `.\.venv\Scripts\python.exe -m pytest -q` - 99 passed.
- New workflow/storage checks: `.\.venv\Scripts\python.exe -m pytest -q tests/test_task_master.py tests/test_task_storage.py` - 39 passed.
- Initial combined run: 137 passed, one legacy test failed because it assumed there would only ever be two migration versions. Its assertions now check preservation/idempotency of legacy versions 1 and 2; the new tests separately check migration 3.
- Final combined run: `.\.venv\Scripts\python.exe -m pytest -q` - 138 passed.
- Headless Chrome: inspected the populated desktop page and new-task form; checked active navigation. Used device emulation to verify an actual 390px viewport with a 153-character unbroken task title and no horizontal overflow. Temporary screenshots were inspected and cleaned up. Browser checks cover these layouts, not a complete accessibility audit or every interactive state.
- `git diff --check` passed for the final changes.

No new dependencies or model calls were required. Part 1 is ready for user review; this does not authorize Part 2 or establish the full MVP.

## Local startup recovery - October 21, 2026

No Flask/Python server was running and nothing was listening on port 5000 when inspected. The global `flask.exe` resolved to a Python 3.13 installation, while the project environment uses Python 3.14.5 with Flask 3.1.2 and Pydantic 2.14.1. This is an interpreter mismatch in command resolution, not evidence of a reproduced startup exception. Use the project's interpreter explicitly instead of the bare `flask` command:

```powershell
.\.venv\Scripts\python.exe -m flask --app trajectory run --host 127.0.0.1 --port 5000
```

The local server was started in the background, bound to 127.0.0.1. Its output goes to `instance/flask.stdout.log` and `instance/flask.stderr.log`. Goal Planner (`/`), Task Master (`/tasks`), the new-task form (`/tasks/new`) and `localhost:5000/tasks` each returned HTTP 200. These checks did not create, edit or delete a user's tasks.

Before startup, SQLite's backup API created `instance/trajectory.before-task-master-1cd7de46.sqlite`. Startup applied migration 3 to the local database. All rows and columns in the 12 pre-existing data tables matched the backup afterward; the migration ledger now contains 1, 2 and 3, and `standalone_tasks` was created empty. Database quick-check and foreign-key checks passed. The backup and runtime logs are local ignored files; no source-code or dependency changes were needed to restore service.

Starting Flask this way does not install a login/startup service. Run the project-interpreter command again after the background process or machine stops. Reload any previously open forms after a server restart because session tokens are per process.

## Task Master Part 2 - October 21, 2026

On Task Master, **Mark done** retains a task and **Mark undone** reopens the same record. New/edit forms offer exactly **No deadline**, **2 days**, **4 days** and **1 week**. The default is no deadline. Restart Flask after updating source; existing forms must be reloaded after a restart.

Dates use the computer's local timezone, appropriate to this local single-user application. A task created October 21 with a two-day deadline is due through October 23 and becomes overdue October 24 if unfinished. Saving the local creation date once prevents timezone changes, ordinary edits, completion changes, day changes or restarts from moving the deadline. Explicit changes to the deadline choice still count from the original creation day. Completed tasks retain their deadline but do not show an overdue warning.

Migration 4 upgrades only the standalone table in one transaction, retaining every original field and deriving each existing task's local creation day from its original UTC creation timestamp using the computer's timezone at upgrade. Existing tasks receive no deadline. The original local timezone was not recorded in Part 1 and cannot be recovered if the computer's timezone changed before upgrading. Goals, plans and preserved legacy work remain untouched. Migration failure restores the original standalone schema/data and can be retried.

Status requests carry the desired state and revision. A fresh request for an already saved state does not write; stale submissions return a conflict instead of toggling or overwriting a newer change. Invalid requests and database failures preserve saved work. Daily availability, AI plans and daily-plan continuity remain Parts 3 and 4. No analytics or new dependencies are added.

Part 2 verification and file-level review evidence are recorded in [Task_Master_Part2_Report.md](Task_Master_Part2_Report.md).

Verification actually run for Part 2:

- Task Master subset: `.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider tests/test_task_master.py tests/test_task_storage.py tests/test_task_deadlines.py` - **92 passed**.
- Full suite: `.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider` - **191 passed**.
- Headless Chrome exercised the real create, deadline-selection, mark-done, mark-undone and deadline-edit forms against an isolated temporary database. Inspected screenshots at 1440px and an actual emulated 390px viewport; neither the list nor form overflowed horizontally. This is focused browser coverage, not a complete accessibility audit.
- Restarted the existing local app after backing up to `instance/trajectory.before-task-master-part2-548d1706.sqlite`. Upgrade preserved all rows in 13 pre-existing data tables, including every original field of all three standalone tasks. Migration ledger is now 1/2/3/4; SQLite quick-check and foreign-key checks passed.
- Goal Planner, Task Master, the new-task form and localhost Task Master returned HTTP 200; the live new-task form contains the deadline selector. Startup logs are `instance/flask-task-master-part2.stdout.log` and `instance/flask-task-master-part2.stderr.log`. No personal task was created, edited, completed or deleted for verification.
