# Running the first application slice

Implemented: goal capture and clarification, local model proposals, draft review and approval, persistent milestone/task editing, and dated actual-work logging with correction and entry removal. This is an incremental build, not the complete Core MVP. Goal and task deletion are still pending.

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

Existing databases receive an additive `goal_context_answers` table on startup; existing goal rows are preserved. Explicit alternatives are stored separately from missing values and saved atomically with the goal revision. All four context questions must have a value or explicit alternative for the goal to display Context ready for a proposal. This is context readiness, not proof of model readiness or a feasible deadline. Blank fields alone remain unanswered. Dates in natural-language descriptions are never silently interpreted as confirmed deadlines. Users can revise answers through Edit goal.

## Local AI generation (Part 3)

Prerequisite: Ollama running locally with `qwen3:4b` installed:

```powershell
ollama pull qwen3:4b
```

The default is Qwen3 4B Q4_K_M (approximately 2.5 GB), published under Apache 2.0. The pre-existing qwen2.5:3b model has a different, non-commercial research license and is not the selected default. No model weights are bundled with this repository. Model license/attribution obligations remain applicable if weights are redistributed. No challenge eligibility is claimed.

Sources reviewed October 19, 2026: [Ollama artifact and license](https://ollama.com/library/qwen3:4b), [upstream license](https://huggingface.co/Qwen/Qwen3-4B/blob/main/LICENSE), [structured outputs](https://docs.ollama.com/capabilities/structured-outputs), [chat API](https://docs.ollama.com/api/chat).

Open a goal, resolve each context question with a value or explicit alternative, then select Generate proposal. The request is synchronous with static pending feedback. A complete response is validated before saving; generation cannot approve tasks or modify goal facts. The adapter uses standard-library HTTP, disables proxies for local requests, sets a 120-second request timeout, limits the response to 128 KiB, requests at most 2,200 output tokens, uses an 8,192-token context and disables thinking/streaming. There is no automatic retry or paid service. A browser disconnect does not guarantee cancellation of local inference.

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


## Saved work and actual progress (Core MVP Parts 1-2)

Open a goal and choose **Manage milestones and tasks**. Add or edit tasks directly, link them to a milestone, or leave them under the goal. Task identities survive direct edits and matching plan replacements. The saved-work page shows current task states and each milestone's completed-task count.

Choose **View work history** on a task to record a dated partial-progress, completion or reopening entry. Actual minutes may be blank (unknown) or 0 (known zero); notes and blockers are optional. A blocker remains visible until cleared or the task is completed. Completion requires an explicit entry; minutes alone never complete a task. **Correct entry** updates a mistaken record, and **Remove mistaken entry** removes it after confirmation. Task state, blockers and recorded-time totals are recalculated from dated entries. Archived tasks retain readable, correctable history.

Startup applies versioned SQLite migrations without recreating existing goals, plans or task IDs. Tests use temporary databases. The local browser must reach a restarted Flask server to load new routes and templates. The automated suite currently passes 87 cases; this does not establish visual accessibility or broad model quality. Daily intentions, capacity-aware schedules and carry-forward are later Core MVP parts.
