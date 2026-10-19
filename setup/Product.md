# Trajectory — Product Requirements

Status: Draft for review. Creation approval does not approve every proposal below.

## 1. Purpose and audience

Trajectory is a personal goal-to-action and progress system for students, independent learners, and freelancers managing competing priorities.

It aims to help people build realistic plans, record what actually happened, and adjust expectations using recorded progress. It also supports learners exploring multiple related or emerging career interests, such as machine learning, software development, and quantum computing, without requiring a single fixed career path. These are intended outcomes, not validated results.

## 2. Requirement labels

- **CONFIRMED REQUIREMENT:** Explicitly required by the project brief.
- **PROPOSED MVP:** Recommended first-release scope; requires product approval.
- **FUTURE IDEA:** Excluded from the initial MVP unless explicitly approved.
- **OPEN DECISION:** Unresolved; must not be treated as an implementation commitment.

## 3. Confirmed requirements

The product retains these capabilities across the four phases in Section 4; they are not all Phase 1 requirements.

| Capability | Required behavior |
| --- | --- |
| Organize work | Connect monthly, semester-based and longer-term goals to milestone checklists and persistent tasks. Represent courses, playlists, college subjects, assignments, projects, research papers and other commitments, with deadlines, dependencies, effort and progress where applicable. |
| Plan daily work | Generate realistic, editable daily plans using available time and priorities. |
| Record actual work | Track planned work against actual progress and time spent. |
| Forecast completion | Estimate completion dates using recorded progress and remaining workload. |
| Detect overload | Identify schedules that exceed available capacity and help users adjust them. |
| Personal Career Navigator | Let users describe ambitions, learning activities, and changing priorities in natural language and maintain an editable, persistent personal trajectory across multiple interests. |
| Use open-weight AI meaningfully | Use a genuine open-weight model in the planning workflow, subject to verified challenge eligibility and license requirements. |

AI-generated suggestions must remain separate from deterministic application logic. Scheduling constraints, validation, persistence, and forecasting must be testable without relying on unsupported model claims.

Do not claim completed features, performance, user validation, offline operation, or privacy guarantees without evidence.

### 3.1 Personal trajectory and persistent context

**CONFIRMED REQUIREMENTS:** The navigator complements daily planning, progress tracking, overload detection, adaptive replanning, and data-grounded forecasts. Its navigator depth belongs to Phase 3; daily planning and forecasting belong to Phase 2.

The editable trajectory must represent long-term interests and goals; current learning priorities and commitments; courses, playlists, projects, and resources; relevant progress history and preferences; decisions and their reasons; and intentional detours or experiments with duration or review date where applicable.

Distinguish three kinds of context in the product:

- Structured records: goals, tasks, deadlines, commitments, and progress.
- Persistent summaries: user-confirmed preferences and decisions, including reasons for changes in direction.
- Historical context: relevant notes or conversation excerpts retrieved when needed, if this capability is included in the approved release.

Users must be able to inspect and correct stored context and request its deletion. Important changes to long-term goals or stored commitments require user confirmation. AI interpretations must remain distinguishable from saved facts; an unconfirmed inference must not silently become a stored preference or commitment.

When comparing a new activity or proposed plan with current priorities, explain a possible mismatch using available context and ask whether it is intentional exploration. Do not label unfamiliar interests as distractions, shame users, or silently change priorities. A confirmed detour must be recorded with its agreed scope and respected until changed, removed, or due for review. Reaching a review date prompts review; it does not authorize changing goals or commitments.

Advice must use available records, identify supporting context where practical, and ask for clarification when evidence is insufficient. Retrieval-augmented generation (RAG) may help find relevant records, but does not guarantee factual advice or eliminate hallucinations. Complete chat-history storage, embeddings, vector databases, and memory frameworks are not product requirements.

## 4. Phased release scope

**CONFIRMED SCOPE ALLOCATION:** Follow [Tasks.md](Tasks.md). This supersedes the earlier broad proposed MVP without removing its later capabilities.

1. **Phase 1 — Core MVP: Goal-to-Plan Assistant.** Capture a goal and clarify missing information; generate real, bounded open-weight task/milestone proposals; review, edit and explicitly approve; track task completion and actual work; persist and reopen goals, accepted plans and progress after restart. Include basic validation, correction/deletion and essential failure handling. An accepted goal work plan does not require a calendar date or daily time slots.
2. **Phase 2 — Planning.** Organize competing goals, projects and commitments; build realistic daily schedules from availability, priorities, deadlines and dependencies; compare planned and actual work, detect overload, adapt plans and calculate evidence-based forecasts.
3. **Phase 3 — Personal Career Navigator.** Connect planning to multiple interests, learning resources and longer-term ambitions using editable, user-confirmed context, decisions and intentional detours. Provide grounded guidance without forcing one career path.
4. **Phase 4 — Advanced Capabilities.** Retain relevant historical-context retrieval, richer roadmap suggestions, exploration reviews and the Sketch Journal/artistic development module. Each extension needs separate scope approval.

Phase 1 is a local, single-user app using the approved Python, Flask/Jinja, modular browser assets, SQLite/sqlite3, Pydantic and pytest direction. Daily calendar scheduling, automatic external calendar synchronization, hosted accounts and advanced career navigation are not Phase 1 requirements.

**Retained simplifications:** Categorize courses, projects and goals as work with actionable tasks; reserve recurring commitment time in Phase 2. Specialized course management, recurring-task automation, collaboration, external calendar synchronization and notifications need separate scope decisions.

### 4.1 Phase 3 navigator slice

**PHASE 3:** Use a compact, persistent trajectory profile containing multiple interests, current priorities, linked learning resources, preferences, and user-confirmed decisions. Allow short natural-language input to propose updates, with a visible review step before saving. Include simple detour records with a reason, scope, and optional duration or review date.

Use this profile and relevant existing work/progress records for planning and activity-alignment explanations. Keep records and summaries inspectable and editable, with a deletion request action. Broad historical conversation retrieval and an autonomous long-term roadmap are not needed for this slice. This is a scope recommendation, not a technical storage or retrieval design; detailed storage, retention and retrieval choices remain open.

### 4.2 Persistent work and daily contributions

Goals, milestone checklists and unfinished master tasks persist across days. For example, maintaining an 8+ GPA, finishing JavaScript and Computer Networking playlists, building two substantial projects, completing research papers and developing white papers should connect to appropriate milestones and tasks rather than form a flat list.

In Phase 2, the user can describe tomorrow's intentions in natural language. AI uses goals, milestones, deadlines, available hours and unfinished work to propose priorities, adjustable time estimates, a useful minimum work session and an explanation of each task's contribution. The user edits and approves. Application logic enforces deadlines, dependencies and available time, reporting conflicts instead of promising impossible work.

Record completion, partial progress, blockers, actual time and optional accomplishment/learning notes against persistent tasks. Recorded work informs task and milestone progress under reviewed update rules; time alone does not prove completion. Each day has its own plan and record of planned work; actual contributions and historical plans remain available. Next-day proposals account for missed work, changed deadlines, remaining capacity and actual progress, referencing existing tasks rather than blindly duplicating them. A new day creates a new plan, not a progress reset. Estimates stay editable and improve only where recorded evidence supports adjustment.

## 5. Acceptance criteria by phase

The four-phase allocation is confirmed; detailed fields, policies and algorithms remain subject to review. Phase 1 applies goal/task/milestone proposals, exact approval, task completion, actual-work recording, persistence, validation, correction/deletion and failures below. Daily scheduling, overload, forecasting and replanning apply in Phase 2; trajectory, alignment and detour checks apply in Phase 3.

| Area | Observable acceptance criterion |
| --- | --- |
| Natural-language entry | A user can describe multiple career interests, learning activities, and goals; inspect extracted details; correct them; and confirm before they become saved goals, commitments, or trajectory updates. Missing required details trigger clarification. |
| Trajectory persistence and control | Confirmed interests, priorities, resource links, preferences, and decisions survive restart. The user can inspect and correct them and request deletion; the interface reports whether deletion is pending or completed. |
| Alignment and detours | For a potentially inconsistent activity, the AI explains the possible mismatch with supporting saved context and asks whether it is intentional. A new field alone is not grounds to call it a distraction. Confirming exploration saves its reason and agreed scope, including a duration or review date when supplied. The user can change or remove the record. Later advice respects active detours. |
| Grounding and confirmation | Advice distinguishes saved information from interpretation and identifies supporting records where practical. A scenario with insufficient or conflicting context produces a clarifying question rather than an invented preference. Important goal or commitment changes are shown for confirmation and do not take effect if declined. |
| Adaptive replanning | Changed priorities, progress, or confirmed detours can produce an editable revised plan. Existing constraint checks still apply, and accepting a new plan requires user action. Forecasts continue to use validated progress and remaining workload, not language-model completion predictions. |
| Work organization | A user can create, view, edit, and remove work items; invalid deadlines, effort values, and required fields receive clear validation feedback. |
| Availability | A user can enter available time and recurring commitments for the selected period; planning uses the resulting usable capacity. |
| Draft planning | Given work and availability, the user can request a plan, inspect suggestions, edit them, and explicitly accept the result. Generating a draft does not silently replace an accepted plan. |
| Constraint enforcement | Before acceptance, the application checks for overlapping planned work, conflicts with reserved commitments, and capacity overruns. Unresolved violations are shown and cannot be accepted as a valid schedule. |
| Overload | If requested work cannot fit, the application identifies unscheduled work and the capacity shortfall instead of silently dropping work or promising that it will fit. |
| Actual progress | A user can record and correct time spent and completed work, and compare planned work with actual records. Time spent alone does not imply an equal amount of completed work. |
| Forecasting | An estimate uses recorded progress, remaining workload, and an explicit future-capacity assumption. The user can inspect its basis. Insufficient data produces an explanation rather than an invented completion date. |
| AI failure | An unavailable model or invalid response produces a clear error or retry path while preserving saved work. Users can still inspect and edit their data and plans. |
| Persistence | Saved work, accepted plans, and progress records survive an application restart through the approved persistence mechanism. |

Forecasts are estimates, not guarantees. Forecast assumptions, minimum data requirements, and deadline-risk rules remain open until architecture and testing review.

## 6. Future scope

**PHASE 4 — Sketch Journal / artistic development:** Retain a dedicated digital illustration journal: organize dated sketches; record practice sessions, time and personal notes; link sketches to exercises, skills or artistic goals; and compare selected sketches across time for reflection. Eventually, a suitable vision model may offer feedback and practice suggestions on gesture, proportions, perspective and values. Distinguish visual observations from subjective judgments, communicate uncertainty and never claim objective measurement of artistic ability without evidence. This is a long-term practice module, not a generic attachment feature or a Phase 1 dependency. Architecture, media storage, privacy, model choice and evaluation remain explicitly open; no tables or integration design are specified here.

**FUTURE IDEAS / PROPOSED EXTENSIONS:** Rich retrieval across historical notes or selected conversation context; longer-term learning-roadmap suggestions grounded in the trajectory; and richer exploration reviews across multiple detours. Each requires separate scope approval. If historical retrieval is added, retrieved context must remain inspectable, correctable, and subject to deletion controls; retrieval must not convert historical or outdated statements into current commitments without confirmation.
Other enhancements require a separate scope decision; their mention does not authorize implementation.

## 7. Open decisions and dependencies

| Open decision | Input needed and consequence |
| --- | --- |
| Challenge eligibility | Obtain the official challenge name and rules/link, deadline, required artifacts, and AI usage criteria. Model eligibility and submission compliance cannot yet be claimed. |
| Phase details | Four-phase allocation is confirmed; review detailed milestone/progress, dependency, minimum-session and acceptance policies before dependent implementation. |
| Navigator details | Review Section 4.1's Phase 3 depth; historical retrieval, richer roadmaps and Sketch Journal remain Phase 4 until separately scoped. |
| Trajectory review rules | Define which edits count as important goal or commitment changes, how current priorities supersede older decisions, and what the user sees when a detour reaches its review date. AI-proposed important changes always require confirmation. |
| Memory and deletion boundaries | Define stored context categories, retention, deletion completion expectations, and treatment of derived summaries or copies. Corrected or deleted information must cease influencing advice once the change completes; no complete chat archive is assumed. |
| Delivery constraints | Confirm development timeframe, budget, target platform, and available hardware or hosted inference access. These constrain feasible scope and architecture. |
| User and hosting model | Local single-user Phase 1 is confirmed. Hosted/multi-user access needs separate scope, security and deployment decisions. |
| Planning semantics | Decide planning horizon, time granularity, deadline interpretation, and how timezone and recurring commitments are handled. |
| Progress and forecasting | Decide progress units, remaining-effort updates, minimum history, capacity assumptions, and how uncertainty is communicated. |
| AI and stack | Python, Flask/Jinja, SQLite/sqlite3, Pydantic and pytest are approved. Running.md and Model_Verification.json record existing model/runtime evidence; challenge eligibility and broader quality require separate verification. |
| Data handling | Determine what information is sent to inference services and how it is stored and retained before making privacy claims. |

Challenge requirements must remain visible here and later in `setup/submission.md`. No official rules have been supplied or verified during this documentation step.

## 8. Documentation boundaries

Existing documents cover design (`setup/Design.md`), architecture (`setup/Architecture.md`), storage (`setup/Database.md`), AI integration (`setup/AI_Integration.md`) and verification (`setup/Testing.md`). Running.md and implementation reports describe current build evidence; specifications alone do not prove completion.

This document authorizes no framework initialization, dependency installation, application code, or deployment. This request authorizes documentation alignment one file at a time; implementation and later scope changes require separate authorization.