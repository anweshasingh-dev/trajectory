# Trajectory

**Turn ambition into a plan you can follow—and revise.**

> **Core MVP in progress:** Goal capture with optional context, local AI draft generation, editing/review/approval, saving and goal-linked milestone/task editing are implemented. Legacy progress tracking is hidden with code/data preserved. Standalone task creation, editing, confirmed deletion and restart persistence are implemented. Saved done/undone controls and creation-based deadlines are implemented in Part 2. Daily AI planning remains pending. Status updated October 21, 2026.

## Overview

Trajectory is a personal goal-to-action and progress system for students, independent learners and freelancers managing learning goals, projects and competing commitments. It connects long-term direction to realistic daily work while preserving multiple interests and intentional exploration. It starts with a Goal-to-Plan Assistant and aims to grow into a personal planning and career navigator grounded in actual progress.

## Problem and solution

A goal such as “Learn machine learning and finish a portfolio project in eight weeks” leaves practical questions: What should I do first? What fits my available time? How do I keep the plan useful after things change?

Trajectory aims to turn that description into proposed tasks and milestones, offer optional follow-up questions, and let the user edit and approve the work without requiring availability or target dates. Later phases add capacity-aware scheduling and evidence-based completion estimates. A target entered by the user is not a guaranteed outcome.

## Key features

**Implemented:** Create/edit/reopen goals, genuinely optional context, validated local AI drafts, editing/review/approval, saving, goal-linked milestone/task editing and standalone Task Master create/edit/delete, done/undone controls and deadlines. **Preserved but hidden:** Legacy dated progress/work logs and summaries. **Pending MVP:** Task Master daily availability and reviewed daily AI planning. The table distinguishes this MVP scope from deferred work.

| Scope | Planned capabilities |
| --- | --- |
| Phase 1 MVP | Goal Planner with optional context, structured proposals, edit/review/approval and persistence. Task Master standalone to-do management is implemented. Done/undone controls and creation-based local-calendar-day deadlines are implemented. Daily availability and reviewed AI allocations remain pending. |
| Phase 2 Planning | Advanced scheduling, recurring commitments, overload, planned-versus-actual analysis, evidence-based forecasts and adaptive replanning. |
| Phase 3 Personal Career Navigator | Multiple career interests, editable persistent preferences/decisions, relevant learning resources, alignment advice and intentional detours. |
| Phase 4 future possibilities | Historical-note retrieval/RAG, richer learning roadmaps, exploration reviews and the dedicated Sketch Journal/artistic development module. Each needs separate scope approval. |

Goals, milestone checklists and goal-linked tasks persist. Legacy dated work entries, actual minutes, blockers and completion summaries remain stored with their code intact, but hidden from the current UI. Task Master manages ordinary to-dos independently of goals or milestones, with title, optional notes, editing, confirmed permanent deletion and restart persistence. Done/undone status and the four deadline choices are implemented. Daily-plan continuity is still planned.

The future Sketch Journal preserves dated sketches, practice/time/notes, exercise/skill/goal links and comparisons across time, with eventual vision-assisted feedback and practice suggestions that communicate uncertainty. Its architecture, storage, privacy and model choices remain open; see [the full artistic vision](setup/Product.md#6-future-scope).

## AI approach

The application sends selected goal context to a local Ollama adapter and validates structured task/milestone proposals before saving them as drafts. No generated task is approved automatically. Users can edit and explicitly approve a saved revision; draft changes never silently replace an approved plan.

The selected default is Qwen3 4B through local Ollama. Its published artifact uses Apache 2.0; no model weights are bundled. Actual inference evidence is recorded in [Model_Verification.json](setup/Model_Verification.json), separately from automated fake-adapter tests. No agent framework, vector database or full-chat archive is used. See [run and model setup instructions](setup/Running.md).

Scheduling constraints, data validation, persistence and numerical forecasts belong to deterministic application code. Model-generated dates are not completion forecasts. Open weights do not automatically establish license suitability, privacy, offline operation, low costs or challenge compliance. See [AI integration plans](setup/AI_Integration.md).

## Why Trajectory?

The intended value is continuity between a goal, an approved plan and the work that actually happened. Suggestions should become editable structured work instead of remaining disconnected chat responses.

The longer-term navigator is designed to respect changing interests: it can ask about a possible priority mismatch while leaving the user in control of intentional exploration. These are product intentions, not validated advantages over existing tools.

The visual foundation is calm and monochrome, with readable non-pixel typography, Lucide icons and restrained decoration. See the [design rulebook](setup/Design.md).

## Business potential

**Hypotheses, not customer validation:** Independent learners building portfolio projects are a proposed first customer group. Students and freelancers may also value less repetitive planning, clearer next actions and, later, capacity-aware replanning.

Possible monetization includes a one-time local-app purchase or paid convenience features. A hosted subscription would require a separate deployment/security decision and viable inference/support costs. No pricing or payment feature is approved; no customers, revenue or traction are evidenced. Willingness to pay must be tested against alternatives such as a free task list plus generic chat. See the [submission brief](setup/submission.md).

## Current development status

The current Goal Planner supports goal capture with blank optional context, local structured proposals, editing/review/approval and SQLite restart persistence. Invalid responses are rejected, changed context invalidates drafts, and failures preserve earlier saved work. Approved snapshots retain task identities; direct goal-linked task/milestone editing remains available. Legacy progress UI/routes are hidden by default with code/data preserved. Task Master Parts 1 and 2 are implemented at `/tasks`; daily AI planning remains pending. Choose 2 days, 4 days, 1 week or no deadline. Dates count from the saved local creation day, through the end of the due date; only an explicit deadline edit changes the choice.

All 191 automated regression tests pass, including 53 Part 2 cases for calendar deadlines, status changes, restart persistence, conflicts and migration rollback. The Task Master subset passes all 92 cases; desktop and 390px browser creation/edit/completion checks also pass. Existing Goal Planner and legacy progress regressions remain covered. Fake-adapter tests are separate from two synthetic local-model stabilization checks; neither establishes broad model quality. [Tasks.md](setup/Tasks.md) distinguishes implemented, pending and deferred work; [Running.md](setup/Running.md) records verification and limitations.

## Technology stack

The project uses a local virtual environment and pinned direct dependencies in requirements.txt. See Running.md for the verified environment and model configuration.

| Layer | Approved direction |
| --- | --- |
| Backend | Python and Flask, with routes, services and domain logic separated. |
| Interface | Jinja templates, HTML, shared CSS and modular browser JavaScript. |
| Persistence | SQLite through Python's sqlite3 module. |
| Validation and testing | Pydantic and pytest. |
| AI model/runtime | Local Ollama with Qwen3 4B; replaceable adapter, validated draft output. |

## Getting started

From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
ollama pull qwen3:4b
.\.venv\Scripts\python.exe -m flask --app trajectory run --host 127.0.0.1
```

Open http://127.0.0.1:5000. Keep Ollama running for generation. Goal capture and saved-work browsing remain available without inference. The local database is stored in `instance/trajectory.sqlite` and excluded from Git.

Run checks with `.\.venv\Scripts\python.exe -m pytest -q`. Full configuration, persistence behavior and limits are in [Running.md](setup/Running.md). This is a local single-user development app.

## Project structure

```text
trajectory/
|-- trajectory/         # Flask factory, routes, services and SQLite storage
|   |-- ai.py           # Local inference adapter
|   |-- plan_models.py  # Structured proposal validation
|   |-- templates/      # Jinja workspace and forms
|   `-- static/         # Shared CSS and focused browser modules
|-- tests/              # Isolated persistence and workflow regression checks
|-- setup/              # Product references, run instructions and evidence
`-- requirements.txt    # Pinned direct dependencies
```

The `instance/` database directory and `.venv/` are local and ignored by Git.

## Roadmap

| Phase | Outcome |
| --- | --- |
| **1 — Core MVP** | Goal capture -> proposed tasks/milestones -> user approval -> actual-work tracking and restart persistence. This is the first release, not a separate pre-MVP phase. |
| **2 — Planning** | Daily scheduling, capacity/overload handling, planned-versus-actual comparison and deterministic forecasting. |
| **3 — Personal Career Navigator** | User-editable direction, decisions, preferences, intentional exploration and grounded alignment advice. |
| **4 — Advanced capabilities** | Separately selected retrieval, roadmap, exploration and journal extensions. |

The full vision remains visible in [Tasks.md](setup/Tasks.md); later features do not expand Phase 1's exit criteria.

## Hacktober challenge context

Trajectory is being developed with the [Hacktoberfest Open-Source AI Challenge, Week 2: Side Hustle](https://dev.to/challenges/hacktoberfest-week2-2026-10-12) in mind:

> Build something with open-weight models or open-source AI that someone would actually pay for.

The intended fit is a useful planning workflow built around meaningful open-weight assistance, with a concrete customer-value hypothesis. **This is not a claim of eligibility or a completed submission.** The official page showed **Ended** when checked on October 19, 2026; any valid entry route needs organizer confirmation. See [submission requirements and open questions](setup/submission.md).

## Links and acknowledgements

| Resource | Link / status |
| --- | --- |
| Repository | [anweshasingh-dev/trajectory](https://github.com/anweshasingh-dev/trajectory) — configured Git remote; public availability and published contents not verified. |
| Live demo | **Pending** — local single-user app is the approved first-release direction; no hosted deployment is evidenced. |
| Demo video | **TODO: add a verified video URL.** |
| Screenshots | **TODO: add screenshots of the actual implemented interface.** No mock screenshot is presented as a working build. |
| Model and license | Qwen3 4B / local Ollama; see Running.md and the separately recorded live verification evidence. |
| DEV submission | **TODO: add the published entry URL if an eligible submission is made.** |

Acknowledgement of the challenge organizers: [DEV Community](https://dev.to/challenges/hacktoberfest-week2-2026-10-12). [Lucide](https://lucide.dev/) is the specified future icon system; its assets have not been integrated. Attribute the actual model, dependencies and any reused work when selected/used. A project license has not yet been supplied; this README does not assign one.