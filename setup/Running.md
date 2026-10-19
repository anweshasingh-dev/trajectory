# Running the first application slice

Implemented: create, list, reopen and edit goals; deterministic clarification questions and explicit unknown/no-deadline answers with SQLite persistence, input validation and stale-edit protection. This is an incremental build, not the complete Phase 1 MVP. Model generation, plan approval, progress logging and deletion are not implemented yet.

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

A per-process random session key protects form tokens. Restarting the server expires open forms; reload before saving after a restart. Goal data remains on disk. No model or external service receives goal data in this slice.

References: [Flask application factory](https://flask.palletsprojects.com/en/stable/tutorial/factory/) and [SQLite connection lifecycle](https://flask.palletsprojects.com/en/stable/tutorial/database/).

## Clarification slice

Existing databases receive an additive `goal_context_answers` table on startup; existing goal rows are preserved. Explicit alternatives are stored separately from missing values and saved atomically with the goal revision. All four context questions must have a value or explicit alternative for the goal to display Context ready for a proposal. This is context readiness, not proof of model readiness or a feasible deadline. Blank fields alone remain unanswered. Dates in natural-language descriptions are never silently interpreted as confirmed deadlines. Users can revise answers through Edit goal.
