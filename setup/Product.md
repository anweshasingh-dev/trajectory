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

**DEFERRED VISION - not current scope:** The navigator complements daily planning, progress tracking, overload detection, adaptive replanning, and data-grounded forecasts. Its navigator depth belongs to Phase 3; advanced scheduling and forecasting remain later work. Task Master's simple daily planner in Section 4 is planned MVP work.

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

1. **Goal Planner.** The user describes a goal and what they want to achieve. AI proposes a structured plan with checkpoints or milestones. **Implemented:** goal capture, structured plan generation, editing, review, explicit approval and saving; preserve these workflows. Optional context is genuinely optional. Missing optional details, including weekly availability or a target date, must not block a useful plan or require explicit acknowledgement of unknowns. Unknowns remain unknown; suggestions must not become saved facts without confirmation. Checkpoints structure the plan; automatic management of every milestone is deferred.
2. **Task Master — Parts 1 and 2 implemented October 21, 2026; daily planning remains planned.** A separate page for ordinary to-dos, with no required goal or milestone link. Create, view, edit and confirm permanent deletion using a title and optional notes; saved tasks reopen after restart. Simple saved done/undone controls are implemented, without progress analytics. Its planned daily planner lets the user enter tasks for tomorrow and provide daily available time. The deadline control offers exactly one of: **2 days, 4 days, 1 week, or no deadline**, measured in local calendar days from the day the task is added. After the user has entered their tasks, AI will consider every unfinished task and suggest priorities, reasonable time allocations and brief explanations using deadlines, available time and done/undone status, for user review before acceptance.

**Planned Task Master continuity:** To-dos and their done/undone status must persist between days and restarts; unfinished tasks remain available for future planning. Every daily plan must be a fresh, reviewable proposal using current inputs. Generating or declining a proposal must not erase saved to-dos or their status. A daily allocation does not require calendar time slots, a course record or a goal/milestone link.

**Legacy progress — hidden from the MVP UI:** Progress-entry controls, detailed work logs, history and summaries are hidden by default; bookmarked legacy progress routes are unavailable in this mode. Existing code and stored data are preserved behind a server-controlled legacy UI switch. These legacy capabilities are not current MVP features. Progress analytics and detailed progress tracking remain excluded from the current user experience.

**Excluded now:** Calendar integration; importing all course schedules or deadlines; complex course management; automatic management of every milestone; advanced forecasting; autonomous agents; Sketch AI/Sketch Journal; and other advanced features. Basic validation of available time and suggested totals does not authorize a scheduling or forecasting engine.

The existing later-phase vision is retained: **Phase 2** advanced scheduling, recurring commitments, overload analysis and evidence-based forecasting; **Phase 3** Personal Career Navigator; **Phase 4** separately selected advanced capabilities including historical retrieval, richer roadmaps and Sketch Journal. None is an initial-release dependency.

The approved local single-user Python, Flask/Jinja, modular browser assets, SQLite/sqlite3, Pydantic and pytest direction is unchanged. This scope adjustment authorizes documentation only.

### 4.1 Phase 3 navigator slice

**PHASE 3:** Use a compact, persistent trajectory profile containing multiple interests, current priorities, linked learning resources, preferences, and user-confirmed decisions. Allow short natural-language input to propose updates, with a visible review step before saving. Include simple detour records with a reason, scope, and optional duration or review date.

Use this profile and relevant existing work/progress records for planning and activity-alignment explanations. Keep records and summaries inspectable and editable, with a deletion request action. Broad historical conversation retrieval and an autonomous long-term roadmap are not needed for this slice. This is a scope recommendation, not a technical storage or retrieval design; detailed storage, retention and retrieval choices remain open.

### 4.2 Persistent work and daily contributions

**PLANNED MVP WORK:** Persistent Task Master to-dos and their done/undone status must be separate from each day's proposed allocations. Reuse task identities across days; a new day must not reset status, duplicate unfinished tasks or discard completed tasks. Unfinished work remains available even when it receives no allocation in a particular plan.

Planned daily proposals use current done/undone status and unfinished work. Time spent alone does not establish completion. Deadlines use local calendar days starting on the day the task is added, as confirmed October 21, 2026. Part 2 uses the computer's local calendar, saves the creation day and treats the due date as inclusive; unfinished tasks become overdue the next day. Explicit deadline changes keep the original creation-day anchor. Daily-plan retention/replacement remains open in Section 7. The app must not silently renew a deadline each day.

Long-term links from goals to learning commitments, richer partial-work/blocker logs, milestone roll-up, minimum-session policies and evidence-based estimate adjustment remain retained ideas, not additional initial-release requirements.

## 5. Acceptance criteria by phase

Acceptance for the approved MVP scope distinguishes existing functionality from work still to be delivered:

- **Goal Planner — preserve implemented functionality:** A goal becomes a structured, editable proposal with checkpoints that the user can review, explicitly approve and save. Saved goals and plans survive restart; generating or declining a draft preserves the approved plan.
- **Goal Planner — implemented optional context:** A user can generate a useful plan while optional context is blank, including weekly availability and target date, without acknowledging unknowns. Missing context must not become invented saved facts.
- **Task Master — partial implementation:** Ordinary to-dos can be created, viewed, edited and permanently deleted after confirmation on a separate page, without a goal or milestone. Task persistence, done/undone controls and creation-based deadlines are implemented, without progress analytics. The remaining planned daily planner will accept daily available time and only the four deadline options, measured in local calendar days; AI will propose priorities, allocations and brief reasons for user review and explicit acceptance. Suggestions exceeding available time must be flagged or revised rather than presented as fitting. To-dos and status survive day changes and restart, and fresh proposals use current inputs without losing unfinished work.
- **Legacy progress — implemented UI boundary:** Progress-tracking controls, history and summaries are hidden by default; existing code and stored data remain preserved. Hidden legacy functionality is not presented as an MVP feature.

Review/approval, applicable validation and AI failure handling apply to existing goal-plan workflows and the planned daily planner. Correction/deletion requirements remain applicable to their respective records; this does not claim all such controls are implemented.

The existing matrix below retains broader behavioral criteria for later releases. Draft review, applicable input validation, AI failure and goal/plan persistence apply to existing workflows. Daily availability and allocation validation are planned MVP work. Persistent done/undone status is implemented. Career context, recurring commitments, time-slot constraints, adaptive milestone management, detailed progress tracking, progress analytics, overload analysis and forecasts are deferred; detailed technical policies remain open.

| Area | Observable acceptance criterion |
| --- | --- |
| Natural-language entry | A user can describe multiple career interests, learning activities, and goals; inspect extracted details; correct them; and confirm before they become saved goals, commitments, or trajectory updates. Missing required details trigger clarification. |
| Trajectory persistence and control | Confirmed interests, priorities, resource links, preferences, and decisions survive restart. The user can inspect and correct them and request deletion; the interface reports whether deletion is pending or completed. |
| Alignment and detours | For a potentially inconsistent activity, the AI explains the possible mismatch with supporting saved context and asks whether it is intentional. A new field alone is not grounds to call it a distraction. Confirming exploration saves its reason and agreed scope, including a duration or review date when supplied. The user can change or remove the record. Later advice respects active detours. |
| Grounding and confirmation | Advice distinguishes saved information from interpretation and identifies supporting records where practical. A scenario with insufficient or conflicting context produces a clarifying question rather than an invented preference. Important goal or commitment changes are shown for confirmation and do not take effect if declined. |
| Adaptive replanning | Changed priorities, progress, or confirmed detours can produce an editable revised plan. Existing constraint checks still apply, and accepting a new plan requires user action. Forecasts continue to use validated progress and remaining workload, not language-model completion predictions. |
| Work organization | A user can create, view, edit, and remove work items; invalid deadlines, effort values, and required fields receive clear validation feedback. |
| Availability | Planned MVP work: enter daily available time for tomorrow's Task Master proposal. Goal Planner weekly availability remains optional. Deferred: recurring commitments and usable interval calculations. |
| Draft planning | Implemented Goal Planner: request, inspect, edit, explicitly approve and save a structured plan. Blank optional context does not block generation. Planned Task Master: review, edit and explicitly accept a daily proposal using to-dos and daily availability. Generating a draft does not silently replace an accepted plan. |
| Constraint enforcement | Before acceptance, the application checks for overlapping planned work, conflicts with reserved commitments, and capacity overruns. Unresolved violations are shown and cannot be accepted as a valid schedule. |
| Overload | If requested work cannot fit, the application identifies unscheduled work and the capacity shortfall instead of silently dropping work or promising that it will fit. |
| Actual progress | Deferred: detailed time/quantity tracking, work history and planned-versus-actual analysis. Existing legacy code and data are preserved, with progress features hidden by default from the current experience. Task Master uses only done/undone status. Time alone does not establish completion. |
| Forecasting | An estimate uses recorded progress, remaining workload, and an explicit future-capacity assumption. The user can inspect its basis. Insufficient data produces an explanation rather than an invented completion date. |
| AI failure | An unavailable model or invalid response produces a clear error or retry path while preserving saved work. Users can still inspect and edit their data and plans. |
| Persistence | Implemented: saved goals, approved plans and standalone Task Master to-dos survive restart. Implemented: done/undone controls and deadlines. Planned MVP work: accepted daily-plan persistence. Preserve legacy progress data; it is excluded from the current experience. |

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
| Current contracts | Review the smallest goal-plan/checkpoint and standalone persistent to-do/done-undone representation against existing records. Preserve legacy progress code and data while hiding its UI. Automatic milestone roll-up, dependencies and minimum-session policies are deferred. |
| Navigator details | Review Section 4.1's Phase 3 depth; historical retrieval, richer roadmaps and Sketch Journal remain Phase 4 until separately scoped. |
| Trajectory review rules | Define which edits count as important goal or commitment changes, how current priorities supersede older decisions, and what the user sees when a detour reaches its review date. AI-proposed important changes always require confirmation. |
| Memory and deletion boundaries | Define stored context categories, retention, deletion completion expectations, and treatment of derived summaries or copies. Corrected or deleted information must cease influencing advice once the change completes; no complete chat archive is assumed. |
| Delivery constraints | Confirm development timeframe, budget, target platform, and available hardware or hosted inference access. These constrain feasible scope and architecture. |
| User and hosting model | Local single-user Phase 1 is confirmed. Hosted/multi-user access needs separate scope, security and deployment decisions. |
| Deadline semantics | The four options, local calendar-day measurement and task-creation-day anchor are confirmed. Part 2 defaults for review: computer-local creation day saved once; due date inclusive; overdue label on unfinished tasks the following day; explicit edits keep the original anchor. No automatic daily deadline reset. |
| Daily-plan lifecycle | Decide proposal/history retention, replacement/acceptance rules and available-time/allocation units for the planned daily planner. Only done/undone status is in scope; detailed progress remains deferred. These decisions do not require time-slot scheduling or recurring commitments. |
| Deferred progress and forecasting | Rich units, remaining-effort updates, milestone roll-up, minimum history, capacity assumptions and uncertainty remain open for later scope, not current prerequisites. |
| AI and stack | Python, Flask/Jinja, SQLite/sqlite3, Pydantic and pytest are approved. Running.md and Model_Verification.json record existing model/runtime evidence; challenge eligibility and broader quality require separate verification. |
| Data handling | Determine what information is sent to inference services and how it is stored and retained before making privacy claims. |

Challenge requirements must remain visible here and later in `setup/submission.md`. No official rules have been supplied or verified during this documentation step.

## 8. Documentation boundaries

Existing documents cover design (`setup/Design.md`), architecture (`setup/Architecture.md`), storage (`setup/Database.md`), AI integration (`setup/AI_Integration.md`) and verification (`setup/Testing.md`). Running.md and implementation reports describe current build evidence; specifications alone do not prove completion.

This document authorizes no framework initialization, dependency installation, application code, or deployment. This request authorizes documentation alignment one file at a time; implementation and later scope changes require separate authorization.