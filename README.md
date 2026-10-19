# Trajectory

**Turn ambition into a plan you can follow—and revise.**

> **Planning stage:** Product and technical documentation exist. The application, model integration and deployment are not implemented or verified. Status reviewed on October 19, 2026.

## Overview

Trajectory is a planned AI-assisted workspace for students, independent learners and freelancers managing learning goals, projects and competing commitments. It starts with a Goal-to-Plan Assistant and aims to grow into a personal planning and career navigator grounded in actual progress.

## Problem and solution

A goal such as “Learn machine learning and finish a portfolio project in eight weeks” leaves practical questions: What should I do first? What fits my available time? How do I keep the plan useful after things change?

Trajectory aims to turn that description into proposed tasks and milestones, ask about missing information, and let the user edit and approve the work before tracking progress. Later phases add capacity-aware scheduling and evidence-based completion estimates. A target entered by the user is not a guaranteed outcome.

## Key features

**Implemented application features: none yet.** The following are planned capabilities, not working product claims.

| Scope | Planned capabilities |
| --- | --- |
| Phase 1 MVP | Natural-language goal capture; open-weight task/milestone proposals and clarification; explicit review/edit/approval; task completion and actual-work records; persistence across restarts. |
| Later core capabilities | Daily schedules, recurring commitments, overload detection, planned-versus-actual comparison, deterministic forecasts and editable replanning. |
| Personal Career Navigator | Multiple career interests, editable persistent preferences/decisions, relevant learning resources, alignment advice and intentional detours. |
| Future possibilities | Historical-note retrieval/RAG, longer-term learning-roadmap suggestions, richer exploration reviews and a creative-practice journal with sketches. Each needs separate scope approval. |

## AI approach

A genuine open-weight model is intended to interpret goals, suggest actionable work and ask clarifying questions. Output will be validated and presented as a proposal; only confirmed changes become accepted plans or saved commitments.

The planned integration uses a replaceable backend adapter. **No model, model license or inference route has been selected or verified.** Ollama is a conditional local candidate; hosted inference or Colab may be evaluated if needed. No agent framework, vector database or full-chat archive is required for the first release.

Scheduling constraints, data validation, persistence and numerical forecasts belong to deterministic application code. Model-generated dates are not completion forecasts. Open weights do not automatically establish license suitability, privacy, offline operation, low costs or challenge compliance. See [AI integration plans](setup/AI_Integration.md).

## Why Trajectory?

The intended value is continuity between a goal, an approved plan and the work that actually happened. Suggestions should become editable structured work instead of remaining disconnected chat responses.

The longer-term navigator is designed to respect changing interests: it can ask about a possible priority mismatch while leaving the user in control of intentional exploration. These are product intentions, not validated advantages over existing tools.

The visual foundation is calm and monochrome, with readable non-pixel typography, Lucide icons and restrained decoration. See the [design rulebook](setup/Design.md).

## Business potential

**Hypotheses, not customer validation:** Independent learners building portfolio projects are a proposed first customer group. Students and freelancers may also value less repetitive planning, clearer next actions and, later, capacity-aware replanning.

Possible monetization includes a one-time local-app purchase or paid convenience features. A hosted subscription would require a separate deployment/security decision and viable inference/support costs. No pricing or payment feature is approved; no customers, revenue or traction are evidenced. Willingness to pay must be tested against alternatives such as a free task list plus generic chat. See the [submission brief](setup/submission.md).

## Current development status

The repository workspace contains setup documents covering requirements, architecture, design, data, AI integration, development rules, testing, decisions and the roadmap. **P1.01 prerequisite review is In Progress; implementation tasks remain Not Started.** No application tests, model benchmarks or usability results are recorded as completed.

Before implementation, the ordered Phase 1 plan/milestone schema and AI contracts need alignment, alongside model/runtime selection and the remaining design/evaluation review. Some earlier documents still label choices open that were subsequently approved in [Tasks.md](setup/Tasks.md); that review records the later local-app/stack approval. Other proposals remain open.

## Technology stack

These technologies are **approved implementation choices recorded in Tasks.md**, not installed or verified application dependencies. No dependency versions or environment setup have been established in the codebase.

| Layer | Approved direction |
| --- | --- |
| Backend | Python and Flask, with routes, services and domain logic separated. |
| Interface | Jinja templates, HTML, shared CSS and modular browser JavaScript. |
| Persistence | SQLite through Python's sqlite3 module. |
| Validation and testing | Pydantic and pytest. |
| AI model/runtime | Undecided; Ollama remains a candidate, not a completed integration. |

## Getting started

**Installation and run instructions are pending.** There is no runnable application, dependency manifest or verified start/test command yet. Cloning this repository provides the current documentation, not a working assistant.

Start with the [product requirements](setup/Product.md) and [phased roadmap](setup/Tasks.md). Follow [project rules](setup/Rules.md) for the one-authorized-scope-at-a-time workflow. Tested installation, configuration, model setup and run instructions will be added after the implementation exists.

## Project structure

Selected files currently present; this is not the proposed application scaffold:

```text
trajectory/
|-- README.md                 # Project introduction
`-- setup/                    # Planning and development documentation
    |-- Product.md            # Product vision and requirements
    |-- Architecture.md       # Component boundaries and technical proposals
    |-- Design.md             # Visual and interaction foundation
    |-- AI_Integration.md     # Model integration and evaluation plans
    |-- Tasks.md              # Phased roadmap and prerequisite review
    `-- submission.md         # Challenge brief and submission checklist
```

Data, testing, rules and decision documents also live in `setup/`. The application directories described in Architecture.md have not been created.

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
| Model and license | **TODO: exact model card, artifact/version, license and verified inference setup.** |
| DEV submission | **TODO: add the published entry URL if an eligible submission is made.** |

Acknowledgement of the challenge organizers: [DEV Community](https://dev.to/challenges/hacktoberfest-week2-2026-10-12). [Lucide](https://lucide.dev/) is the specified future icon system; its assets have not been integrated. Attribute the actual model, dependencies and any reused work when selected/used. A project license has not yet been supplied; this README does not assign one.