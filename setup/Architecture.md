# Trajectory — Architecture

Status: Architecture responsibilities remain a proposal where labeled. Local single-user Phase 1 and Python/Flask/Jinja/SQLite/sqlite3/Pydantic/pytest are approved in Tasks.md; this alignment authorizes no implementation.
Source of truth: `setup/Product.md`, with release allocation in `setup/Tasks.md`. Existing `setup/Design.md` owns visual direction and remains outside this alignment scope. Detailed technical proposals are not approved merely by this update.

## A. Architecture Overview

**Recommendation:** One modular web application, one structured database, and a replaceable inference adapter. A single application keeps deployment and debugging manageable while separating responsibilities internally.

```text
Browser: templates + reusable UI + page-specific CSS/JavaScript
    -> routes: parse requests and return HTML or JSON
    -> application services: coordinate validated actions and approvals
        -> scheduling / progress / forecasting: deterministic calculations
        -> context service -> AI orchestration -> inference adapter -> model
        -> repositories -> structured database
```

The browser never talks directly to the model or database. Application services, rather than the model, authorize and persist changes. Modules receive explicit dependencies and inputs; avoid scattered mutable global state. Configuration and connection factories may be shared through the application factory.

**Phase 1 target:** Goal capture/clarification, bounded task/milestone proposals, editable ordered goal plans, exact approval, persistent tasks and actual-work tracking with restart persistence. **Phase 2** adds competing commitments, daily schedules, overload, planned-versus-actual and evidence-based forecasts. **Phase 3** adds the trajectory profile, resources, decisions, detours and grounded alignment explanations. The components below describe responsibilities across these phases, not a requirement to build all modules in Phase 1.

**Future extensions:** Broad historical-note/conversation retrieval, longer-term roadmap suggestions, and richer exploration reviews. Support these through existing context and AI interfaces only when approved; do not build unused infrastructure now. The Sketch Journal/artistic development module remains Phase 4; its architecture, storage, privacy and vision-model integration are open. See Product.md Section 6 for retained behavior. No visual layouts, animations, transitions, or detailed screen journeys are settled here.

## B. Proposed Technology Stack

Python, Flask/Jinja, modular browser assets, Pydantic, SQLite/sqlite3 and pytest are **CONFIRMED direction** in Tasks.md. Detailed component design remains proposed. Existing pinned versions and local model evidence are documented in requirements.txt and setup/Running.md; this update does not change or reverify them. Ollama's earlier candidate discussion below is retained as selection rationale, not current selection status.

| Choice                                                                        | Responsibility and reason                                                                                                                 | Limits and trade-offs                                                                                                                                 |
| ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Python                                                                        | Backend services, calculations, and inference integration in one language.                                                                | Team familiarity and hosting support still need confirmation.                                                                                         |
| Flask with an application factory and grouped routes                          | Small web application serving HTML and a limited JSON interface. Fits a server-rendered frontend without a separate frontend service.     | Validation and API contracts must be deliberately added; slow inference occupies a request worker in the initial synchronous design.                  |
| Jinja templates, semantic HTML, shared CSS tokens, browser JavaScript modules | Reusable server-rendered components with incremental editing and asynchronous requests where useful. No frontend build service initially. | Rich interactions require disciplined state handling; exact interaction needs await Design.md.                                                        |
| Pydantic                                                                      | Explicit request and model-output contracts, with type and value validation.                                                              | Adds a dependency justified by structured AI data; schema validity does not establish truth.                                                          |
| SQLite via Python's sqlite3 module                                            | Structured persistence with transactions and a small operational footprint. Repositories contain parameterized SQL.                       | One writer per database file; unsuitable for a scaled multi-writer deployment without reassessment. Migration discipline remains necessary.           |
| Ollama, conditional local candidate                                           | Run a separately selected open-weight model behind a backend adapter.                                                                     | Runtime availability does not verify model eligibility, license, memory fit, quality, or acceptable latency. Hosted inference remains an alternative. |
| pytest                                                                        | Unit and integration checks with temporary databases and fake inference adapters.                                                         | Browser checks may start manual; a browser automation dependency requires a demonstrated need.                                                        |

Flask supports the proposed factory pattern and templates; see its [application factories](https://flask.palletsprojects.com/en/stable/patterns/appfactories/) and [quickstart](https://flask.palletsprojects.com/en/stable/quickstart/). These capabilities support the recommendation, not a claim that it is the only suitable framework.

**Alternatives evaluated:** FastAPI offers integrated validation and API documentation, making it attractive if a separate API or multiple clients become central; see its [official features](https://fastapi.tiangolo.com/features/). Flask is the approved direction for this small server-rendered app. Django is worth revisiting if accounts and administrative workflows dominate, but is not the current recommendation. A React frontend adds a build and client-state layer whose need is not established by Product.md. No agent framework, queue, microservices, or vector database is initially justified.

SQLite's [official suitability guidance](https://www.sqlite.org/whentouse.html) supports local application storage but identifies its single-writer limit. Revisit a server database if concurrent users, multiple application replicas, or hosting storage constraints require it.

Ollama's [structured-output documentation](https://docs.ollama.com/capabilities/structured-outputs) describes JSON-schema output and application-side validation; it currently states that Ollama Cloud does not support structured outputs. Do not assume local and cloud API capabilities are identical. The adapter must expose unsupported capabilities explicitly. The current local implementation uses Qwen3 4B/Ollama, with recorded evidence in Running.md and Model_Verification.json. This document performs no new model/license/runtime verification or challenge-eligibility check.

## C. System Components

| Component                  | Owns                                                                                                                                    | Must not own                                                                        |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Frontend                   | Input forms, draft editing, confirmation, validation feedback, source visibility, reusable UI.                                          | Authoritative scheduling, secrets, SQL, or model calls.                             |
| Routes                     | Request parsing, identity scope when applicable, calling services, HTML/JSON responses.                                                 | Business calculations or database queries.                                          |
| Work service               | Persistent goals, milestone/task relationships and validated edits; categorized courses/projects, resource references and commitments as phased.                           | Specialized course tooling or resource scraping.                                    |
| Planning service           | Goal-plan drafts/acceptance, revisions and stale checks; separate daily plans referencing persistent tasks in Phase 2.                                                  | Treating a model response as an accepted plan.                                      |
| Scheduling logic           | Available intervals, reserved commitments, overlap/capacity checks, unscheduled work and shortfall calculations.                        | Inventing available time or silently changing priorities.                           |
| Progress and forecasting   | Validated actual-work records; remaining-work and completion estimates with visible assumptions.                                        | Equating time spent with progress or accepting model-generated numerical forecasts. |
| Trajectory/context service | Current interests, priorities, preferences, approved summaries, decisions, detours, source selection, correction/deletion coordination. | Silently promoting inferred preferences or storing all chats by default.            |
| AI orchestration           | Bounded context assembly, prompt/output contracts, adapter calls, output validation, clarification and error results.                   | Direct persistence, arbitrary tools, or autonomous goal changes.                    |
| Repositories               | Parameterized data access and mapping records to explicit return objects.                                                               | HTML rendering, prompt construction, or domain policy.                              |

Possible route groups are work, plans, progress, and trajectory. Endpoint names and browser payloads are not final. Use explicit actions for requesting a draft, accepting a draft, confirming a trajectory change, and recording a detour; an ordinary read must not mutate commitments.

## D. Proposed Directory Structure

Illustrative only: create none of these implementation files during setup. Names and grouping may change after stack and design approval. Package initializer files are omitted for readability.

```text
trajectory/                         # Project root
├── setup/                          # Planning and project documentation
│   ├── Product.md
│   ├── Architecture.md
│   ├── Design.md                   # Add later, after UX planning
│   ├── Database.md
│   ├── AI_Integration.md
│   ├── Rules.md
│   ├── Testing.md
│   ├── Tasks.md
│   ├── DECISIONS.md
│   ├── Submission.md
│   ├── AGENTS.md
│   └── README.md
│
├── trajectory/                     # Python application package
│   ├── __init__.py                 # Application factory
│   ├── config.py
│   ├── contracts.py
│   │
│   ├── routes/                     # Web request handlers
│   │   ├── work.py
│   │   ├── plans.py
│   │   ├── progress.py
│   │   └── trajectory.py
│   │
│   ├── services/                   # Application workflows
│   │   ├── work.py
│   │   ├── planning.py
│   │   ├── progress.py
│   │   └── context.py
│   │
│   ├── domain/                     # Pure business calculations
│   │   ├── scheduling.py
│   │   └── forecasting.py
│   │
│   ├── ai/                         # Model integration
│   │   ├── orchestration.py
│   │   ├── contracts.py
│   │   ├── runtime.py
│   │   └── prompts/
│   │
│   ├── persistence/                # Database access
│   │   ├── database.py
│   │   ├── repositories.py
│   │   └── migrations/
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── components/
│   │   └── pages/
│   │
│   └── static/
│       ├── css/
│       │   ├── tokens.css
│       │   ├── base.css
│       │   ├── components.css
│       │   └── pages/
│       └── js/
│           ├── api.js
│           ├── components/
│           └── pages/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── workflows/
│
├── instance/                       # Local runtime data; Git-ignored
├── pyproject.toml
├── .env.example
└── .gitignore
```

Routes call service interfaces; services use repositories and pure domain functions. AI receives explicit snapshots and returns proposals. No module should reach into another module's private state. Start with cohesive files, splitting when responsibilities diverge rather than enforcing a file count. Rules.md will formalize a soft file-length guideline. Shared tokens and components stay centralized; page-specific code stays separate when it has distinct behavior.

## E. Main Data and Request Flows

### 1. Natural-language goal to proposed plan

```text
Input -> route validation -> context snapshot -> AI extraction proposal
      -> schema + semantic checks -> user reviews/corrects missing details
      -> explicit confirmation -> persist approved goal/trajectory details
      -> AI task/milestone proposal -> semantic validation -> editable goal-plan draft
```

Extraction and plan acceptance are separate approval boundaries. AI may propose new work details but must mark missing effort, deadlines, or priorities for clarification; it must not store guesses as facts. Existing tasks are referenced by validated identifiers. New task proposals cannot masquerade as existing records. The source snapshot includes record versions so later edits can be detected.

### 2. Edited plan to persisted acceptance

```text
Edited draft + snapshot version -> route -> planning service
    -> reload current work (and availability for Phase 2) -> validate applicable constraints
    -> if stale, explain and require review of updated draft
    -> if valid and explicitly accepted, atomic persistence -> accepted plan
```

Validate again on acceptance, regardless of earlier browser checks. A rejected edit leaves the prior accepted plan intact. Repeated submission must not create duplicate acceptance records; use an acceptance identifier and transaction/version checks. Model invocation never holds a database write transaction open.

### 3. Actual progress to persistent work and later forecasts

```text
Progress/time entry -> validation -> progress service -> atomic save
    -> read validated progress + remaining work + future capacity
    -> forecasting function -> estimate, basis, and missing-data explanation
```

Phase 1 saves completion/partial progress, blockers, actual time and optional accomplishment/learning notes against stable tasks and milestone context; detailed roll-up policy remains open. Phase 2 compares actuals to daily allocations and proposes next-day work using remaining capacity, missed work and changed deadlines. Reuse task identity, preserve historical plans/contributions and require approval of each new daily plan; no midnight progress reset or blind duplication. Estimates remain adjustable; actual evidence may inform revisions under reviewed rules.

Record completed units separately from time spent. Forecasting below is Phase 2. Forecast in comparable approved workload units using observed completion rates and future usable capacity. If units are incompatible, history insufficient, or capacity unavailable, return an explicit unavailable/uncertain result rather than a made-up date. Formula, observation window, minimum history, and uncertainty display remain OPEN DECISION. Correcting actuals recalculates estimates. Forecast failure must not erase a successfully saved progress record.

### 4. New learning activity to alignment review (Phase 3)

```text
Activity -> context service retrieves current priorities + active detours
    -> AI comparison with source identifiers -> validate references
    -> possible mismatch explanation or clarification -> user review
```

New subject matter alone is not a distraction. Present interpretation separately from saved facts; unfamiliar or insufficient context calls for a question. No automatic priority change or punitive classification. Suggestions about an entire learning roadmap remain future scope.

### 5. Confirmed detour to updated context (Phase 3)

```text
User confirms reason/scope and optional duration/review date
    -> validated change proposal -> context service -> atomic detour/decision save
    -> refresh affected context -> future advice respects confirmed exploration
```

Allow later inspection, correction, or removal. A review date prompts a review; it does not authorize dropping a commitment or changing long-term goals. Requests involving important goal/commitment changes show the proposed before/after values and require confirmation of that exact revision.

## F. AI and Application Logic Boundaries

| Model may propose                                                                  | Application must enforce                                                                                   |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Extracted goals, tasks, learning interests, and clarifying questions.              | Types, allowed fields, ownership, existing references, valid units/dates, and explicit confirmation.       |
| Task ordering, workload breakdown, editable schedules, and alignment explanations. | Overlaps, reserved time, capacity, deadlines, dependencies, unscheduled workload reporting, and persisted plan versions. |
| Summaries and reasons grounded in supplied context.                                | Confirmation state, source validity, correction/deletion behavior, and current versus historical records.  |
| Plain-language explanation of a calculated forecast.                               | Remaining workload and numerical estimate; the model cannot override either.                               |

**Validation pipeline:** Limit response size; parse the expected JSON object; reject unknown fields and invalid types/ranges; validate referenced records and source IDs; run domain checks; then label the result as a proposal. Schema-constrained decoding helps formatting but does not prove semantic correctness or grounding. Unsupported source claims must be removed from advice or returned for clarification, not presented as verified facts.

Use a narrow adapter contract such as `generate(request, schema, timeout) -> response or typed failure`. Adapter replacement should not alter scheduling, forecasting, or persistence code. Separate extraction, planning, and alignment prompts/contracts; do not introduce autonomous agents for these bounded operations.

**Proposed failure policy:** One initial bounded inference call; no automatic infinite repair loop. On timeout, missing model, unsupported capability, oversized/invalid output, or semantic failure, return a useful error/clarification and allow user-triggered retry or manual editing. Exact time/size budgets await hardware measurements. Preserve accepted plans and saved context; never auto-apply a partial result. Late results based on changed/deleted context must be discarded or regenerated.

## G. Persistent Context and Retrieval

Structured records are authoritative for current goals, tasks, availability, actual work, confirmed preferences, and detours. Approved summaries are derived, editable context with references to underlying decisions. Historical notes are optional supplementary evidence, never automatically current commitments.

**Initial recommendation:** Select context by explicit goal/task relationships, current priority, active detour, and bounded relevant decision history using repository queries. Include source IDs, current version/status, and an inspectable explanation of selected records. Store only context that the product needs and the user has approved; do not default to full chat retention. Resource links do not imply automatic fetching or external-content ingestion.

On conflicting records, use confirmed current state and ask about unresolved conflicts. Do not resolve changes of direction solely through an AI-generated summary. Natural-language advice cites relevant saved records where practical; a valid reference proves that the record exists, not that every model interpretation is correct. Retrieval and schema checks reduce some errors without guaranteeing truth.

**Future retrieval path:** If approved and justified, add a notes retrieval implementation behind the context interface. Start with metadata/text search if adequate; evaluate embeddings or a vector index only after measured retrieval needs. Retrieved content is untrusted data, not instructions. Expose supporting excerpts and distinguish historical statements from current facts.

**Correction/deletion:** Coordinate source updates, dependent summaries, saved drafts, and any future search index. Invalidate affected context; block new advice from pending-deletion records. Before returning or accepting an in-flight response, recheck source versions/deletion state. Once correction/deletion completes, stale information must cease influencing advice. Show pending/completed status; if cleanup fails, report pending failure rather than falsely claiming completion. Backup retention and deletion timing remain OPEN DECISION; logs should not become a second personal memory archive.

## H. Database and Module Boundaries

Services access repository methods rather than SQL. Repositories receive a connection/unit of work; the coordinating service defines the transaction for a complete action. Keep constraints and parameterized queries in persistence and domain rules in services/domain modules. Enable referential integrity and design uniqueness/version checks where needed.

Database.md describes proposed schema, indexes, deletion relationships, migrations and progress units, distinguishing Phase 1 requirements from later-phase catalogues. Expected record groups are work/commitments, draft and accepted plans, actual work, trajectory preferences, confirmed decisions/detours, and approved summaries. These are conceptual responsibilities, not a final table list.

Use short transactions, explicit commit/rollback, and no inference calls inside transactions. Database contention must produce a recoverable error, not lost updates. Keep local database files outside static assets and source control. Do not place a SQLite file on shared network storage as an assumed scaling strategy. Server-database migration requires reviewed migrations and tests; a repository boundary does not make it automatic.

## I. Error Handling and Security

- Validate requests on the server even if the browser validates them. Return field-level errors for bad input; missing context yields clarification, and concurrency conflicts yield review prompts.
- Keep AI failures distinct from persistence failures. Retry controls must not duplicate saved mutations. Roll back incomplete writes and return a request identifier for unexpected failures.
- Treat model text, resource titles, and retrieved notes as untrusted. Escape rendered text; do not render arbitrary model HTML, execute generated code/SQL, or permit model-selected filesystem/network access. Do not fetch arbitrary user-provided URLs in the initial scope.
- Keep inference endpoint/model selection in server-controlled configuration. Bound request size and inference duration; avoid exposing a local inference endpoint directly to the public browser.
- Store secrets in environment/deployment configuration, excluded from Git; examples contain placeholders only. Validate configuration at startup and show actionable setup errors without revealing credentials. Disable debug mode for demonstrations exposed to others.
- Protect browser mutations against cross-site request forgery; use appropriate cookie settings if sessions are used. Same-origin browser requests are the initial recommendation, with no permissive cross-origin policy by default.
- A local single-user demo should bind to loopback. Before a hosted multi-user release, approve authentication, per-user authorization for every record/retrieval query, transport security, storage protection, retention, and abuse limits. Do not publicly expose a personal-data application without that boundary.
- Send only needed personal context to inference. Hosted processing requires an explicit data-handling decision and disclosure of the destination. No claim of private-by-design or offline capability follows from choosing a local runtime.

## J. Testing and Observability

Test scheduling and forecasting as pure functions with fixed time/capacity inputs. Cover overlaps, reserved intervals, impossible deadlines, insufficient history, zero capacity, distinct progress/time units, and timezone boundary cases after semantics are approved.

Service tests use fake repositories/adapters for approval rejection, invalid model fields, unknown references, invented preferences, detour review dates, timeout, stale drafts, and correction/deletion during an in-flight request. Repository integration tests use temporary databases for transaction rollback, restart persistence, version conflicts, duplicate acceptance prevention, and deletion effects.

Verify all five Section E flows through routes and persistence. Check that browser edits are revalidated, previous plans survive failures, saved progress updates estimates, and confirmed detours influence subsequent context selection. Evaluate real-model quality separately from deterministic tests, using representative multi-interest and intentional-exploration cases. Fake inference tests do not prove that open-weight integration works.

Record request IDs, operation/failure category, duration, validation outcomes, context record counts, and model/runtime identifiers where appropriate. Avoid raw prompts, personal notes, full outputs, and secrets in ordinary logs. Inspect actual timings and failure rates without inventing metrics. Testing.md will define detailed checks and evidence; no tests or inference benchmarks were run during this documentation task.

## K. Deployment and Demo Constraints

| Environment       | Proposed setup                                                                             | Required verification                                                                                                                                 |
| ----------------- | ------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Local development | Web app and SQLite on the developer machine; optional local runtime as a separate process. | Python/runtime versions, database path, model availability, context/output validation, and actual device compatibility.                               |
| Local live demo   | Loopback application with a verified local model and non-sensitive sample records.         | Full workflow rehearsal, cold/warm inference duration, memory use, restart persistence, and failure recovery.                                         |
| Public demo       | Production web server, persistent storage, and an explicitly reachable inference service.  | Host budget/storage/concurrency; security boundary; model license/eligibility; privacy and inference routing. This is a separate deployment decision. |

A remote web host's localhost refers to that host, not the developer's laptop. Local inference will not automatically become reachable or fit the hosted server. Do not expose the laptop runtime casually to solve this. Consider verified hosted open-weight inference or a local/recorded demo only if challenge rules allow; disclose which mode is actually shown. A recording or mock does not by itself satisfy real-model integration requirements.

Ollama's [hardware support](https://docs.ollama.com/gpu) and [FAQ](https://docs.ollama.com/faq) inform compatibility checks; hardware details, model size/quantization, memory, operating system, context length, and measured behavior must be checked together. Existing local hardware/runtime observations are recorded in Running.md and Model_Verification.json; no new measurements are made here. A working runtime is not evidence of a model's license or challenge eligibility.

Flask's [deployment guidance](https://flask.palletsprojects.com/en/stable/deploying/) requires a suitable production WSGI server rather than the development server for deployment. Choose a Windows-compatible or host-appropriate server only after deployment approval. Persist SQLite on a supported durable volume; ephemeral hosting storage cannot establish restart durability.

## L. Architectural Decisions and Open Questions

**Confirmed boundaries:** Product.md governs scope; deterministic code owns constraints and forecasts; important goal/commitment changes require confirmation; context is inspectable/correctable/deletable; Design.md is outside this alignment scope. No implementation is authorized here.

| OPEN DECISION            | Recommendation / input needed before implementation                                                                                                                                           |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Phase details            | Follow Product.md's confirmed four-phase allocation. Review milestone completion/roll-up, dependency and daily-plan policies before their dependent implementation.                                |
| Stack details            | Approved direction is Flask/Jinja/browser modules/Pydantic/SQLite/sqlite3/pytest; version/runtime evidence belongs to requirements.txt and Running.md. Any stack change needs separate approval.                                              |
| Challenge constraints    | Supply official rules/link, deadline, required artifacts, and definition of eligible open-weight AI use. Compliance remains unverified.                                                       |
| Time and budget          | Supply available build time, hosting/inference budget, and team familiarity. No delivery estimate can be validated yet.                                                                       |
| Model/runtime review     | Existing Qwen3 4B/Ollama smoke evidence is in Running.md and Model_Verification.json. Broader quality, future model changes and hosted routes require separate evaluation/approval. |
| Later hosting            | Local single-user Phase 1 is confirmed; hosted access/accounts require separate scope, security and deployment decisions.                                               |
| Scheduling and forecasts | Approve timezone, recurrence/deadline semantics, planning horizon, progress units, forecast assumptions, minimum history, and uncertainty behavior.                                           |
| Context policy           | Define important-change boundaries, detour review behavior, retained history, deletion completion/backup policy, and hosted data handling.                                                    |
| Inference execution      | Start with bounded synchronous requests if measured latency permits. If not, revisit a minimal job/status mechanism and stale-result handling before adding a queue dependency.               |

For model selection or replacement, retain the exact model/version, source model card and license, inference route, compatibility evidence, and a small planning/alignment evaluation. Keep approval records in DECISIONS.md and measured implementation evidence in Running.md and verification artifacts.

Related existing documents: `setup/Database.md`, `setup/AI_Integration.md`, `setup/Rules.md`, `setup/Testing.md`, `setup/DECISIONS.md`, and `setup/submission.md`. Visual direction remains with `setup/Design.md`, which is untouched.

Official technical references were consulted on 2026-10-18. Their capabilities may change; recheck versions and provider support before implementation. The original architecture inspection preceded implementation. Running.md and implementation reports now describe the current slice; this alignment changes documentation only.
