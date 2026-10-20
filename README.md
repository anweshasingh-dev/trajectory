# Trajectory

**Turn ambition into a plan you can follow—and revise.**

> **Core MVP in progress:** Goal capture, local AI draft generation, review and approval, persistent milestones/tasks, and dated actual-work tracking are implemented. Two real-model generation checks are recorded separately. Daily planning remains to be built. Status updated October 19, 2026.

## Overview

Trajectory is a personal goal-to-action and progress system for students, independent learners and freelancers managing learning goals, projects and competing commitments. It connects long-term direction to realistic daily work while preserving multiple interests and intentional exploration. It starts with a Goal-to-Plan Assistant and aims to grow into a personal planning and career navigator grounded in actual progress.

## Problem and solution

A goal such as “Learn machine learning and finish a portfolio project in eight weeks” leaves practical questions: What should I do first? What fits my available time? How do I keep the plan useful after things change?

Trajectory aims to turn that description into proposed tasks and milestones, ask about missing information, and let the user edit and approve the work before tracking progress. Later phases add capacity-aware scheduling and evidence-based completion estimates. A target entered by the user is not a guaranteed outcome.

## Key features

**Implemented:** Create/edit/reopen goals, clarification, validated local AI drafts, review/approval, persistent milestone/task editing, dated work entries, partial progress, completion, blockers, corrections and reopening. **Pending:** Daily planning and complete end-to-end MVP verification. The table below describes the earlier phase boundaries.

| Scope | Planned capabilities |
| --- | --- |
| Phase 1 MVP | Natural-language goal capture; open-weight task/milestone proposals and clarification; explicit review/edit/approval; task completion and actual-work records; persistence across restarts. |
| Phase 2 Planning | Natural-language daily intentions; prioritized editable schedules linked to persistent goals, milestones and tasks; recurring commitments, overload, planned-versus-actual, evidence-based forecasts and next-day replanning. |
| Phase 3 Personal Career Navigator | Multiple career interests, editable persistent preferences/decisions, relevant learning resources, alignment advice and intentional detours. |
| Phase 4 future possibilities | Historical-note retrieval/RAG, richer learning roadmaps, exploration reviews and the dedicated Sketch Journal/artistic development module. Each needs separate scope approval. |

Goals, milestone checklists and master tasks persist. Dated work entries record explicit completion, partial work, blockers, actual minutes and optional notes; corrections recalculate task status and milestone completion counts. Future daily plans will reference these same tasks and work records.

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

The first working slices support goal capture, correction, explicit unknown/no-deadline clarification, local structured proposal generation and SQLite restart persistence. Invalid responses are rejected, changed goal context invalidates generation, and failed attempts preserve earlier saved drafts. Plan review/edit/approval is implemented with immutable approved snapshots and retained task identities. Direct task/milestone editing and dated actual-work records are implemented with correction, removal and restart persistence.

Automated tests cover goal persistence, clarification, draft/review lifecycle, task identity, dated progress, corrections, migrations and inference failure paths. These use fake adapters for repeatability; a live model smoke check is separate and does not establish broad plan quality. Setup documents distinguish phased requirements from technical proposals; Tasks.md retains its earlier tracking snapshot without certifying completion; [Running.md](setup/Running.md) describes the implemented slice.

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