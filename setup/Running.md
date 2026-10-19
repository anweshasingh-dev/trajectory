# Running the first application slice

Implemented: create, list, reopen and edit goals; deterministic clarification questions and explicit unknown/no-deadline answers with SQLite persistence, input validation and stale-edit protection. This is an incremental build, not the complete Phase 1 MVP. Local model generation and persistent draft display are implemented. Draft editing/approval, progress logging and deletion are not implemented yet.

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

An additive `plan_drafts` table stores the draft JSON, goal source revision, model name/digest, prompt version and returned performance counters. No accepted-task tables are created. Earlier drafts are retained; the workspace displays the most recently saved draft and labels it outdated if goal context changed. A replacement attempt does not erase a previous draft when inference fails. Source revision is checked again atomically when saving, so a result generated against changed/deleted goal context is rejected. Reposting the same generation request ID cannot create duplicate drafts. Editing and approval are the next build slice.

Tests use fake model adapters for repeatable failure checks. Real model results, once recorded, are separate evidence; one successful example is a smoke check, not a broad quality evaluation. Configuration defaults are in the application factory; runtime-specific details stay in `trajectory/ai.py`.

### Live verification recorded October 19, 2026

[Model_Verification.json](Model_Verification.json) records the exact local digest, synthetic inputs, responses, timings, prompt versions and manual findings. Two v2 live requests completed in 9.04 and 9.63 seconds; both saved drafts reopened after a fresh application instance. A cold v1 request took 33.73 seconds. Ollama reported full GPU execution with an 8,192-token context and 3.9 GB loaded memory. These are observations on this machine, not latency promises.

The first content review found an unsupported duration and accuracy example; prompt v2 removed those from the reviewed outputs and added the requested documentation deliverable. Residual model limitations remain: known facts can be repeated as assumptions, and availability/routine assumptions may still be proposed. They remain visibly unconfirmed and never update goal context. Most reviewed effort estimates were unknown. Review all generated suggestions before using them. All 35 automated regression cases passed separately.
