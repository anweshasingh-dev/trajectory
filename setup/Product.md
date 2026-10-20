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

The product retains these capabilities as its long-term vision. Only the two features in Section 4 are in the current initial scope; this catalogue is not an initial-release checklist.

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

**DEFERRED VISION - not current scope:** The navigator complements daily planning, progress tracking, overload detection, adaptive replanning, and data-grounded forecasts. Its navigator depth belongs to Phase 3; advanced scheduling and forecasting remain later work. The simple Daily To-do Planner in Section 4 is current scope.

The editable trajectory must represent long-term interests and goals; current learning priorities and commitments; courses, playlists, projects, and resources; relevant progress history and preferences; decisions and their reasons; and intentional detours or experiments with duration or review date where applicable.

Distinguish three kinds of context in the product:

- Structured records: goals, tasks, deadlines, commitments, and progress.
- Persistent summaries: user-confirmed preferences and decisions, including reasons for changes in direction.
- Historical context: relevant notes or conversation excerpts retrieved when needed, if this capability is included in the approved release.

Users must be able to inspect and correct stored context and request its deletion. Important changes to long-term goals or stored commitments require user confirmation. AI interpretations must remain distinguishable from saved facts; an unconfirmed inference must not silently become a stored preference or commitment.

When comparing a new activity or proposed plan with current priorities, explain a possible mismatch using available context and ask whether it is intentional exploration. Do not label unfamiliar interests as distractions, shame users, or silently change priorities. A confirmed detour must be recorded with its agreed scope and respected until changed, removed, or due for review. Reaching a review date prompts review; it does not authorize changing goals or commitments.

Advice must use available records, identify supporting context where practical, and ask for clarification when evidence is insufficient. Retrieval-augmented generation (RAG) may help find relevant records, but does not guarantee factual advice or eliminate hallucinations. Complete chat-history storage, embeddings, vector databases, and memory frameworks are not product requirements.

## 4. Phased release scope

**CURRENT SCOPE - confirmed 2026-10-20:** Only two features are included. This supersedes the earlier allocation that placed all daily planning in Phase 2; the broader roadmap remains a deferred vision.

1. **Goal-to-Plan.** The user describes a big goal and what they want to achieve. AI proposes a structured plan with checkpoints or milestones. The user can review, edit and approve the proposal. Checkpoints structure the plan; automatic management of every milestone is deferred.
2. **Daily To-do Planner.** The user enters tasks they want to work on tomorrow and provides their available time. Each to-do has exactly one deadline option: **2 days, 4 days, 1 week, or no deadline**. AI suggests priorities, reasonable time allocations and brief explanations using current to-dos, deadlines, available time and recorded progress.

To-dos persist between days. Completed tasks are recorded; unfinished tasks remain available for future planning. Every daily plan is a fresh, reviewable proposal using current inputs, not an automatic replay of yesterday's plan. Generating or declining a proposal must not erase saved to-dos or progress. A daily allocation does not require calendar time slots, a course record or a goal/milestone link.

**Excluded now:** Calendar integration; importing all course schedules or deadlines; complex course management; automatic management of every milestone; advanced forecasting; autonomous agents; Sketch AI/Sketch Journal; and other advanced features. Basic validation of available time and suggested totals does not authorize a scheduling or forecasting engine.

The existing later-phase vision is retained: **Phase 2** advanced scheduling, recurring commitments, overload analysis and evidence-based forecasting; **Phase 3** Personal Career Navigator; **Phase 4** separately selected advanced capabilities including historical retrieval, richer roadmaps and Sketch Journal. None is an initial-release dependency.

The approved local single-user Python, Flask/Jinja, modular browser assets, SQLite/sqlite3, Pydantic and pytest direction is unchanged. This scope adjustment authorizes documentation only.

### 4.1 Phase 3 navigator slice

**PHASE 3:** Use a compact, persistent trajectory profile containing multiple interests, current priorities, linked learning resources, preferences, and user-confirmed decisions. Allow short natural-language input to propose updates, with a visible review step before saving. Include simple detour records with a reason, scope, and optional duration or review date.

Use this profile and relevant existing work/progress records for planning and activity-alignment explanations. Keep records and summaries inspectable and editable, with a deletion request action. Broad historical conversation retrieval and an autonomous long-term roadmap are not needed for this slice. This is a scope recommendation, not a technical storage or retrieval design; detailed storage, retention and retrieval choices remain open.

### 4.2 Persistent work and daily contributions

Persistent to-dos and completion/progress records are separate from each day's proposed allocations. Reuse existing task identities across days; a new day must not reset progress, duplicate unfinished tasks or discard completed-task records. Unfinished work remains available even when it receives no allocation in a particular plan.

Daily proposals use the current state, including recorded completion and unfinished work. Time spent alone does not establish completion. Deadline anchor, calendar-day interpretation, timezone, overdue handling, progress detail and daily-plan retention/replacement remain open in Section 7; the app must not silently renew a deadline each day.

Long-term links from goals to learning commitments, richer partial-work/blocker logs, milestone roll-up, minimum-session policies and evidence-based estimate adjustment remain retained ideas, not additional initial-release requirements.

## 5. Acceptance criteria by phase

Current acceptance covers the two features in Section 4: a goal becomes a structured, editable proposal with checkpoints; tomorrow's to-dos accept only the four deadline options and available time; AI suggests priorities, allocations and brief reasons; completed records and unfinished tasks survive day changes and restart; a new proposal uses current progress. Suggestions exceeding available time must be flagged or revised rather than presented as fitting. Review/approval, validation, correction/deletion and failure handling apply to current records.

The existing matrix below retains broader behavioral criteria for later releases. Only draft review, applicable input/capacity validation, recorded completion/progress, AI failure and persistence apply now. Career context, recurring commitments, time-slot constraints, adaptive milestone management, overload analysis and forecasts are deferred; detailed technical policies remain open.

| Area | Observable acceptance criterion |
| --- | --- |
| Natural-language entry | A user can describe multiple career interests, learning activities, and goals; inspect extracted details; correct them; and confirm before they become saved goals, commitments, or trajectory updates. Missing required details trigger clarification. |
| Trajectory persistence and control | Confirmed interests, priorities, resource links, preferences, and decisions survive restart. The user can inspect and correct them and request deletion; the interface reports whether deletion is pending or completed. |
| Alignment and detours | For a potentially inconsistent activity, the AI explains the possible mismatch with supporting saved context and asks whether it is intentional. A new field alone is not grounds to call it a distraction. Confirming exploration saves its reason and agreed scope, including a duration or review date when supplied. The user can change or remove the record. Later advice respects active detours. |
| Grounding and confirmation | Advice distinguishes saved information from interpretation and identifies supporting records where practical. A scenario with insufficient or conflicting context produces a clarifying question rather than an invented preference. Important goal or commitment changes are shown for confirmation and do not take effect if declined. |
| Adaptive replanning | Changed priorities, progress, or confirmed detours can produce an editable revised plan. Existing constraint checks still apply, and accepting a new plan requires user action. Forecasts continue to use validated progress and remaining workload, not language-model completion predictions. |
| Work organization | A user can create, view, edit, and remove work items; invalid deadlines, effort values, and required fields receive clear validation feedback. |
| Availability | Current: enter available time for tomorrow. Deferred: recurring commitments and usable interval calculations. |
| Draft planning | Given work and availability, the user can request a plan, inspect suggestions, edit them, and explicitly accept the result. Generating a draft does not silently replace an accepted plan. |
| Constraint enforcement | Before acceptance, the application checks for overlapping planned work, conflicts with reserved commitments, and capacity overruns. Unresolved violations are shown and cannot be accepted as a valid schedule. |
| Overload | If requested work cannot fit, the application identifies unscheduled work and the capacity shortfall instead of silently dropping work or promising that it will fit. |
| Actual progress | Current: record completion/progress without losing unfinished tasks. Deferred: detailed time/quantity tracking and planned-versus-actual analysis. Time alone does not establish completion. |
| Forecasting | An estimate uses recorded progress, remaining workload, and an explicit future-capacity assumption. The user can inspect its basis. Insufficient data produces an explanation rather than an invented completion date. |
| AI failure | An unavailable model or invalid response produces a clear error or retry path while preserving saved work. Users can still inspect and edit their data and plans. |
| Persistence | Saved work, accepted plans, and progress records survive an application restart through the approved persistence mechanism. |

Forecasts are estimates, not guarantees. Forecast assumptions, minimum data requirements, and deadline-risk rules remain open until architecture and testing review.

## 6. Future scope

**PHASE 4 — Sketch Journal / artistic development:** Retain a dedicated digital illustration journal: organize dated sketches; record practice sessions, time and personal notes; link sketches to exercises, skills or artistic goals; and compare selected sketches across time for reflection. Eventually, a suitable vision model may offer feedback and practice suggestions on gesture, proportions, perspective and values. Distinguish visual observations from subjective judgments, communicate uncertainty and never claim objective measurement of artistic ability without evidence. This is a long-term practice module, not a generic attachment feature or a Phase 1 dependency. Architecture, media storage, privacy, model choice and evaluation remain explicitly open; no tables or integration design are specified here.

**Other retained ideas, excluded now:** Calendar integration; bulk course schedule/deadline imports; specialized course management; automatic milestone management; advanced forecasting; and autonomous agents. These are deferred possibilities, not commitments or implementation designs.

**FUTURE IDEAS / PROPOSED EXTENSIONS:** Rich retrieval across historical notes or selected conversation context; longer-term learning-roadmap suggestions grounded in the trajectory; and richer exploration reviews across multiple detours. Each requires separate scope approval. If historical retrieval is added, retrieved context must remain inspectable, correctable, and subject to deletion controls; retrieval must not convert historical or outdated statements into current commitments without confirmation.
Other enhancements require a separate scope decision; their mention does not authorize implementation.

## 7. Open decisions and dependencies

| Open decision | Input needed and consequence |
| --- | --- |
| Challenge eligibility | Obtain the official challenge name and rules/link, deadline, required artifacts, and AI usage criteria. Model eligibility and submission compliance cannot yet be claimed. |
| Current contracts | Review the smallest goal-plan/checkpoint, persistent to-do and completion/progress representation against existing records. Automatic milestone roll-up, dependencies and minimum-session policies are deferred. |
| Navigator details | Review Section 4.1's Phase 3 depth; historical retrieval, richer roadmaps and Sketch Journal remain Phase 4 until separately scoped. |
| Trajectory review rules | Define which edits count as important goal or commitment changes, how current priorities supersede older decisions, and what the user sees when a detour reaches its review date. AI-proposed important changes always require confirmation. |
| Memory and deletion boundaries | Define stored context categories, retention, deletion completion expectations, and treatment of derived summaries or copies. Corrected or deleted information must cease influencing advice once the change completes; no complete chat archive is assumed. |
| Delivery constraints | Confirm development timeframe, budget, target platform, and available hardware or hosted inference access. These constrain feasible scope and architecture. |
| User and hosting model | Local single-user Phase 1 is confirmed. Hosted/multi-user access needs separate scope, security and deployment decisions. |
| Deadline semantics | The four options are confirmed. Decide the duration anchor (entry or planning day), calendar-day versus elapsed-time interpretation, timezone/day boundary, due-time boundary, overdue behavior and explicit deadline edits. No automatic daily deadline reset. |
| Daily-plan lifecycle | Decide proposal/history retention, replacement/acceptance rules, progress detail and available-time/allocation units. These do not require time-slot scheduling or recurring commitments. |
| Deferred progress and forecasting | Rich units, remaining-effort updates, milestone roll-up, minimum history, capacity assumptions and uncertainty remain open for later scope, not current prerequisites. |
| AI and stack | Python, Flask/Jinja, SQLite/sqlite3, Pydantic and pytest are approved. Running.md and Model_Verification.json record existing model/runtime evidence; challenge eligibility and broader quality require separate verification. |
| Data handling | Determine what information is sent to inference services and how it is stored and retained before making privacy claims. |

Challenge requirements must remain visible here and later in `setup/submission.md`. No official rules have been supplied or verified during this documentation step.

## 8. Documentation boundaries

Existing documents cover design (`setup/Design.md`), architecture (`setup/Architecture.md`), storage (`setup/Database.md`), AI integration (`setup/AI_Integration.md`) and verification (`setup/Testing.md`). Running.md and implementation reports describe current build evidence; specifications alone do not prove completion.

This document authorizes no framework initialization, dependency installation, application code, or deployment. This request authorizes documentation alignment one file at a time; implementation and later scope changes require separate authorization.