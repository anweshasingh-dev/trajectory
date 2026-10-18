# Trajectory — Product Requirements

Status: Draft for review. Creation approval does not approve every proposal below.

## 1. Purpose and audience

Trajectory is an AI-assisted personal planning and goal-forecasting application for students, independent learners, and freelancers managing competing priorities.

It aims to help people build realistic plans, record what actually happened, and adjust expectations using recorded progress. It also supports learners exploring multiple related or emerging career interests, such as machine learning, software development, and quantum computing, without requiring a single fixed career path. These are intended outcomes, not validated results.

## 2. Requirement labels

- **CONFIRMED REQUIREMENT:** Explicitly required by the project brief.
- **PROPOSED MVP:** Recommended first-release scope; requires product approval.
- **FUTURE IDEA:** Excluded from the initial MVP unless explicitly approved.
- **OPEN DECISION:** Unresolved; must not be treated as an implementation commitment.

## 3. Confirmed requirements

The product must support the following intended core capabilities. Their first-release depth remains subject to MVP approval.

| Capability | Required behavior |
| --- | --- |
| Organize work | Represent courses, projects, personal goals, deadlines, and recurring commitments. |
| Plan daily work | Generate realistic, editable daily plans using available time and priorities. |
| Record actual work | Track planned work against actual progress and time spent. |
| Forecast completion | Estimate completion dates using recorded progress and remaining workload. |
| Detect overload | Identify schedules that exceed available capacity and help users adjust them. |
| Personal Career Navigator | Let users describe ambitions, learning activities, and changing priorities in natural language and maintain an editable, persistent personal trajectory across multiple interests. |
| Use open-weight AI meaningfully | Use a genuine open-weight model in the planning workflow, subject to verified challenge eligibility and license requirements. |

AI-generated suggestions must remain separate from deterministic application logic. Scheduling constraints, validation, persistence, and forecasting must be testable without relying on unsupported model claims.

Do not claim completed features, performance, user validation, offline operation, or privacy guarantees without evidence.

### 3.1 Personal trajectory and persistent context

**CONFIRMED REQUIREMENTS:** The navigator complements daily planning, progress tracking, overload detection, adaptive replanning, and data-grounded forecasts. Its release depth is subject to MVP approval.

The editable trajectory must represent long-term interests and goals; current learning priorities and commitments; courses, playlists, projects, and resources; relevant progress history and preferences; decisions and their reasons; and intentional detours or experiments with duration or review date where applicable.

Distinguish three kinds of context in the product:

- Structured records: goals, tasks, deadlines, commitments, and progress.
- Persistent summaries: user-confirmed preferences and decisions, including reasons for changes in direction.
- Historical context: relevant notes or conversation excerpts retrieved when needed, if this capability is included in the approved release.

Users must be able to inspect and correct stored context and request its deletion. Important changes to long-term goals or stored commitments require user confirmation. AI interpretations must remain distinguishable from saved facts; an unconfirmed inference must not silently become a stored preference or commitment.

When comparing a new activity or proposed plan with current priorities, explain a possible mismatch using available context and ask whether it is intentional exploration. Do not label unfamiliar interests as distractions, shame users, or silently change priorities. A confirmed detour must be recorded with its agreed scope and respected until changed, removed, or due for review. Reaching a review date prompts review; it does not authorize changing goals or commitments.

Advice must use available records, identify supporting context where practical, and ask for clarification when evidence is insufficient. Retrieval-augmented generation (RAG) may help find relevant records, but does not guarantee factual advice or eliminate hallucinations. Complete chat-history storage, embeddings, vector databases, and memory frameworks are not product requirements.

## 4. Proposed MVP

**PROPOSED MVP:** Deliver one complete planning loop for an individual user:

1. Describe career interests, learning activities, or goals in natural language; review and confirm the proposed trajectory details and actionable work items, including deadlines, remaining effort, and priorities.
2. Enter available time and recurring commitments for the planning period.
3. Request a daily plan in which the open-weight model meaningfully suggests work selection, ordering, or workload breakdown using the saved trajectory and current priorities. If it flags a possible mismatch, review its explanation and confirm whether the activity is an intentional exploration.
4. Validate suggestions against application constraints and present a draft the user can edit and accept.
5. Record time spent and progress against planned work.
6. Recalculate completion estimates and highlight workload that cannot fit available capacity. Suggest revised plans for review without silently changing accepted plans or commitments.
7. Inspect and correct the saved trajectory; confirm important changes and record or remove intentional detours and their reasons.

**Proposed simplifications:** Treat courses, projects, and goals as categories of work with actionable tasks; support recurring commitments as reserved time. Specialized course management, recurring-task automation, collaboration, external calendar synchronization, and notifications are not required by this proposed MVP.

These simplifications are recommendations, not settled exclusions from the long-term product.

### 4.1 Minimal navigator slice

**PROPOSED MVP:** Use a compact, persistent trajectory profile containing multiple interests, current priorities, linked learning resources, preferences, and user-confirmed decisions. Allow short natural-language input to propose updates, with a visible review step before saving. Include simple detour records with a reason, scope, and optional duration or review date.

Use this profile and relevant existing work/progress records for planning and activity-alignment explanations. Keep records and summaries inspectable and editable, with a deletion request action. Broad historical conversation retrieval and an autonomous long-term roadmap are not needed for this slice. This is a scope recommendation, not a technical storage or retrieval design; feasibility still depends on the challenge deadline and available resources.

## 5. Proposed acceptance criteria

These criteria become release requirements only after the MVP is approved. Exact data fields and algorithms belong in later documents.

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

**FUTURE IDEA:** A creative-practice journal for saving sketches and tracking artistic development. It is excluded from the initial MVP unless explicitly approved.

**FUTURE IDEAS / PROPOSED EXTENSIONS:** Rich retrieval across historical notes or selected conversation context; longer-term learning-roadmap suggestions grounded in the trajectory; and richer exploration reviews across multiple detours. Each requires separate scope approval. If historical retrieval is added, retrieved context must remain inspectable, correctable, and subject to deletion controls; retrieval must not convert historical or outdated statements into current commitments without confirmation.
Other enhancements require a separate scope decision; their mention does not authorize implementation.

## 7. Open decisions and dependencies

| Open decision | Input needed and consequence |
| --- | --- |
| Challenge eligibility | Obtain the official challenge name and rules/link, deadline, required artifacts, and AI usage criteria. Model eligibility and submission compliance cannot yet be claimed. |
| MVP approval | Confirm or revise Section 4 and its acceptance criteria before treating them as release commitments. |
| Navigator release scope | Approve or revise the minimal slice in Section 4.1 and the associated acceptance criteria; confirm which historical retrieval and roadmap features remain future scope. |
| Trajectory review rules | Define which edits count as important goal or commitment changes, how current priorities supersede older decisions, and what the user sees when a detour reaches its review date. AI-proposed important changes always require confirmation. |
| Memory and deletion boundaries | Define stored context categories, retention, deletion completion expectations, and treatment of derived summaries or copies. Corrected or deleted information must cease influencing advice once the change completes; no complete chat archive is assumed. |
| Delivery constraints | Confirm development timeframe, budget, target platform, and available hardware or hosted inference access. These constrain feasible scope and architecture. |
| User and hosting model | Decide whether the initial release is a local single-user tool or a hosted application, and whether accounts are needed. This affects persistence, security, and deployment. |
| Planning semantics | Decide planning horizon, time granularity, deadline interpretation, and how timezone and recurring commitments are handled. |
| Progress and forecasting | Decide progress units, remaining-effort updates, minimum history, capacity assumptions, and how uncertainty is communicated. |
| AI and stack | Evaluate the model, license, inference method, framework, database, and deployment together. No particular technology is selected here. |
| Data handling | Determine what information is sent to inference services and how it is stored and retained before making privacy claims. |

Challenge requirements must remain visible here and later in `setup/Submission.md`. No official rules have been supplied or verified during this documentation step.

## 8. Documentation boundaries

Later documents will cover design (`setup/Design.md`), architecture (`setup/Architecture.md`), storage (`setup/Database.md`), AI integration (`setup/AI_Integration.md`), and verification (`setup/Testing.md`). These are planned documents, not existing artifacts.

This document authorizes no framework initialization, dependency installation, application code, or deployment. Each subsequent setup document requires explicit approval under the one-file workflow.