# Trajectory — Decision Log

> **Review draft.** This log records explicit user requirements and approvals; it does not approve implementation or resolve proposals merely by listing them.
> Compiled: **2026-10-18** (Asia/Calcutta). This is the log's compilation date, not an inferred decision date.

## 1. How to read this log

| Status | Meaning |
| --- | --- |
| **CONFIRMED** | Explicitly required or approved by the user. Evidence is identified below. |
| **OPEN · proposed** | A recommendation exists, but approval of that specific choice is not recorded. |
| **OPEN · unresolved** | User input or a choice is still needed. |
| **OPEN · unverified** | Evidence is missing; do not treat the assumption as fact. |

**Date convention:** “Not recorded” means an exact decision/approval date was not established. Document modification times and reference-check dates are not approval dates. All open entries have **no decision date**. The 2026-10-19 alignment request confirmed the earlier four-phase allocation. The explicit 2026-10-20 request supersedes its initial-release boundary through C18; technical proposals stay open and implementation remains unauthorized.

The user has referred to the existing setup documents as approved references. Several document headers still say draft/proposed, and their open-decision sections remain explicit. Document-level approval is not evidence that each proposed technology, schema detail, or numerical guideline was individually settled. Individual choices remain open unless explicit approval is identified. This alignment records the stack/local-user approvals already in Tasks.md; technical detail is not approved by association.

## 2. Confirmed decisions and requirements

The alternatives column describes what a requirement rules out or leaves available; it does not claim those alternatives were evaluated or rejected in a separate historical discussion. Reasons summarize the user's stated intent, not invented validation results.

| ID / status | Decision | Reason | Alternatives / boundary | Decision date |
| --- | --- | --- | --- | --- |
| C01 · CONFIRMED | Keep setup documentation in `setup/`; work on one explicitly authorized file/change scope, report, then wait for approval. | User requested a controlled, reviewable workflow. | Batch creation and incidental edits are not authorized. | Not recorded |
| C02 · CONFIRMED | Documentation only at this stage; no code, dependencies, framework initialization or application scaffolding. | User explicitly limited this phase to setup. | Implementation needs separate authorization. | Not recorded |
| C03 · CONFIRMED | Defer Design.md while other specifically requested setup documents proceed. | User wants to plan visual direction, journeys and interactions separately. | Do not infer layouts, animations or detailed UI behavior from the technical documents. | Not recorded |
| C04 · CONFIRMED | Use a genuine open-weight model meaningfully in planning; verify the exact model, license and challenge fit before claiming eligibility. | Explicit challenge-related product requirement. | Existing local model/runtime evidence is referenced under O03–O04; replacements and eligibility remain separate decisions. Mocks alone do not establish real integration. | Not recorded |
| C05 · CONFIRMED | Separate AI suggestions from deterministic scheduling constraints, validation, persistence and numerical forecasts. | User requires testable application logic grounded in recorded data. | The model may propose work/orderings; it cannot authorize writes or establish completion forecasts. Exact scheduling/forecast policies remain open. | Not recorded |
| C06 · CONFIRMED | Support a flexible, multi-interest career trajectory with inspectable, editable persistent context. | User's Career Navigator update explicitly requested continuity across changing interests. | Navigator is Phase 3; storage/retrieval details remain open; full chat storage is not required. | Not recorded |
| C07 · CONFIRMED | Require confirmation for important goal/commitment changes; explain possible mismatches respectfully and honor confirmed intentional detours. | User explicitly preserves control over direction and exploration. | No automatic distraction labels, shaming or silent priority changes. Review dates do not authorize goal changes. | Not recorded |
| C08 · CONFIRMED | Let users inspect/correct stored context and request deletion; distinguish structured facts, approved summaries and historical context. | Explicit persistent-context requirements. | RAG does not guarantee truth; deletion timing, retention and implementation remain open. | Not recorded |
| C09 · CONFIRMED | Use cohesive modules with separate routing, services, persistence, AI, frontend assets/components and tests where appropriate. | User explicitly requires understandable responsibilities and maintainability. | No giant catch-all application; no arbitrary file-count splitting. Final structure depends on approved stack/requirements. | Not recorded |
| C10 · CONFIRMED | For small learning-focused code edits, keep the smallest prior implementation as a temporary comment above its replacement; explain the change. Use a diff/before-and-after for large changes. | User's mandatory learning-oriented reporting policy. | User removes temporary comments after understanding; this does not authorize coding during setup. | Not recorded |
| C11 · CONFIRMED | Report every file operation, purpose, verified final line ranges, execution-flow changes and actual test results; never invent evidence. | User's explicit completion-report requirements. | No fabricated features, metrics, user feedback, verification or line numbers. | Not recorded |
| C12 · CONFIRMED | Retain the dedicated Sketch Journal/artistic development module in Phase 4: dated sketches, practice/time/notes, skill/exercise/goal links, comparisons over time and eventual vision-assisted feedback/practice suggestions. | User's clarified artistic vision preserves reflection and gradual practice. | Product.md Section 6 holds the full behavior. No objective artistic score without evidence; storage/privacy/architecture/vision-model decisions remain open. No MVP dependency. | Reaffirmed 2026-10-19 |
| C13 · CONFIRMED | Avoid unnecessary dependencies/infrastructure, keep changes small, and never silently expand scope or settle major choices. | User's original constraints and Rules.md request explicitly require this. | A justified addition still needs authorization within the relevant change scope. | Not recorded |
| C14 · HISTORICAL; scope allocation superseded by C18 | Four phases: Goal-to-Plan Assistant; Planning; Personal Career Navigator; separately selected Advanced Capabilities. | The 2026-10-19 alignment request reiterated Tasks.md's earlier scope allocation. | Daily calendar scheduling is Phase 2; full navigator is Phase 3; historical retrieval, richer roadmaps and Sketch Journal are Phase 4. No implementation authorization. | Reaffirmed 2026-10-19 |
| C15 · CONFIRMED | Python, Flask/Jinja, modular browser assets, SQLite/sqlite3, Pydantic and pytest; local single-user Phase 1. | Explicit approval recorded in Tasks.md's P1.01 review, reaffirmed by the current request. | This does not approve hosted accounts, every schema proposal or future stack changes. Existing pinned versions are in requirements.txt; no versions change here. | Original date not recorded; reaffirmed 2026-10-19 |
| C16 · HISTORICAL; current subset clarified by C18 | Goals/milestones/master tasks persist; daily plans and actual contributions remain distinct with historical review and thoughtful next-day carry-forward. | User requires continuity from long-term goals to actual work. | Completion, partial work, blockers, time and optional learning notes inform progress; no midnight reset, blind duplication or completion inferred from time alone. Exact roll-up remains open. | 2026-10-19 |
| C17 · HISTORICAL; simple daily slice superseded by C18 | Phase 2 AI interprets daily intentions, proposes priorities, adjustable estimates, useful minimum sessions and goal-contribution explanations; user edits/approves. | User's clarified daily planning loop. | Application enforces deadlines, dependencies and available time. Estimate improvement requires actual evidence; exact policies remain open. | 2026-10-19 |
| C18 · CONFIRMED | Initial scope contains only Goal-to-Plan and the Daily To-do Planner, as specified in Product.md Section 4. | User explicitly requested a much simpler initial product on 2026-10-20. | Simple daily planning is current; earlier calendar/forecast coupling in C14/C17 is superseded. Persistent to-dos, recorded completion, unfinished-work continuity and fresh proposals are current. Rich progress/milestone automation from C16 is deferred. Preserve the long-term vision without designing it now. Technical choices remain open; no task-status change or implementation is authorized. | 2026-10-20 |
| C19 · CONFIRMED | Task Master deadline durations start on the local calendar day the task is added. The four choices remain 2 days, 4 days, 1 week or no deadline. | The user explicitly specified the creation-day anchor while simplifying Task Master. | Replanning and ordinary task edits must not renew deadlines. Timezone source, due-day boundary, overdue handling and explicit deadline edits remain open; this does not authorize Part 2 implementation. | 2026-10-21 |

### Part 2 implementation defaults for review - October 21, 2026

The user authorized Task Master Part 2: status and deadlines, including relevant checks and review. The implementation uses the computer's local timezone for this local single-user app, saves the local creation day once, treats due dates as inclusive and labels only unfinished tasks overdue on the following day. Explicit deadline edits count from the original creation day. Migration 4 preserves old task fields and derives missing local dates from their UTC creation timestamps using the timezone at upgrade. These are implementation choices for review, not claims that a separate timezone preference was explicitly supplied. No new daily planner or analytics is included; Parts 3 and 4 remain pending.

### Confirmation evidence

- **C01–C02, C04–C05, C09–C13:** Original controlled-setup request; reflected in [Product.md](Product.md), [Architecture.md](Architecture.md) and [Rules.md](Rules.md). The later Rules.md request explicitly reiterates scope control, small changes and dependency restraint.
- **C03 (historical setup boundary):** The Architecture Documentation request postponed design. Design.md now exists with a later design request recorded in its header; this alignment does not infer its approval status, revise its content or choose a new UI direction.
- **C06–C08, C12:** User's Personal Career Navigator update; reflected in Product.md Section 3.1 and future-scope section. Later architecture/AI requests reiterate deterministic logic and initial-versus-future scope.

- **C12, C14–C17:** Historical 2026-10-19 documentation-alignment request; C15 also cites the explicit approvals already recorded in Tasks.md. This authorizes the named documentation alignment one saved/reviewed file at a time, preserving Rules.md and separate implementation gates.

- **C18:** Explicit 2026-10-20 two-feature documentation-only scope request. It authorizes relevant sections of the seven named documents, one file at a time, with audit and per-file reporting. Design.md, Rules.md and submission.md remain protected; C01 does not require a new product-scope approval between these already named edits.

**Protected-reference conflicts (unresolved):** Design.md Sections 7/8/10/12 and submission.md Section 6 retain the earlier goal-only initial boundary and later daily planning. Rules.md Sections 1/7 retain historical design-deferral wording although Design.md exists. These protected files are unchanged; aligning them requires the user's approval. C18 governs this named documentation adjustment without approving new visual design or implementation.

## 3. Open choices — proposals are not approvals

Open rows below have **decision date: not decided**. O02/O10 retain their IDs with explicit resolution references rather than being silently removed. Consult the source sections for detailed options; this log intentionally does not duplicate their contracts or schema.

| ID / status | Choice or proposal | Reason to resolve | Alternatives / input needed |
| --- | --- | --- | --- |
| O01 · OPEN · unresolved | Minimal current contracts/acceptance within C18; later navigator depth remains deferred. | The two-feature boundary is settled; technical detail is not. | Review lightweight checkpoints, to-do/progress representation and current daily behavior. Navigator, calendar scheduling and automatic milestone management are not initial gates. |
| O02 · RESOLVED → C15 | Stack direction approved in Tasks.md and reaffirmed by the current request. | Preserves the historical proposal ID. | Detailed schema/runtime policies and future stack changes still need their own review. |
| O03 · OPEN · unresolved | Model replacement approval, broader quality evidence and challenge eligibility. | Running.md/Model_Verification.json already record Qwen3 4B/Ollama identity, license references and local smoke evidence; no new model choice is made here. | Existing observations do not establish broad quality, challenge eligibility or approval of a hosted route. |
| O04 · OPEN · proposed | Future runtime/execution changes beyond the documented local Ollama implementation. | Existing synchronous/non-streamed configuration and limits are recorded in Running.md. | Revisit another provider/runtime or job mechanism only with evidence and separate authorization. |
| O05 · OPEN · proposed; deferred | AI suggests ordering/allocation; deterministic code places tasks in intervals. | AI_Integration.md Section 2 narrows scheduling responsibility to avoid model arithmetic. | Approve/revise the proposal within C05; scheduling policy, horizon and granularity still need selection. |
| O06 · OPEN · proposed | Database.md's phased 12-table catalogue, singleton profile, UUIDs, typed context, daily plan lifecycle and conservative revision invalidation. | Concrete schema recommendations are not proof of individual choice approval. | Review minimal current goal/checkpoint, to-do, daily-proposal and progress needs against existing storage without approving the catalogue, then later ownership and relationship/JSON provenance trade-offs, concurrent edits, plan history and migration approach; redesign for multi-user access if needed. |
| O07 · OPEN · unresolved; rich measurement/forecasts deferred | Progress units/precision, remaining-work corrections, forecast formula, evidence window, uncertainty and goal roll-up. | Comparable recorded progress is needed for honest forecasts. | Review task-specific quantities versus approved alternatives; never infer completion from time alone. |
| O08 · OPEN · proposed; interval scheduling deferred | One-off/weekly local-time windows, UTC stored instants, midnight splitting and earlier applicable parent/task deadline. | Database.md proposes manageable time semantics, but exceptions/DST and deadline precedence need approval. | Define timezone/DST, recurrence exceptions and deadline rules before implementation. |
| O09 · OPEN · unresolved | Important-change boundaries, detour review behavior, context retention, proposal expiry, deletion completion and backup/provider handling. | User control is confirmed; exact operational policy is not. | Specify what is stored, confirmed, purged and restored; choose timings and failure/retry behavior. |
| O10 · RESOLVED IN PART → C15 | Local single-user Phase 1 is confirmed; later hosted access/accounts/security and deployment remain OPEN. | Hosting is not a Phase 1 gate. | Separately approve any hosted inference or multi-user product/deployment boundary. |
| O11 · OPEN · proposed | 300-line file / 40-line function soft review guidelines. | Rules.md Section 2 introduces these numerical recommendations with exceptions. | Approve/revise thresholds; preserve cohesive modules without arbitrary splitting. |
| O12 · OPEN · proposed | AI evaluation starter set of 20 cases, three attempts per candidate/case, and proposed release gates. | AI_Integration.md Section 9 recommends an evaluation design, not completed tests. | Approve/revise test scope, quality thresholds, timeout/context/output budgets and response-time target. |
| O13 · OPEN · unresolved | Lightweight goal checkpoint representation; richer checklist identity, roll-up, dependencies, minimum sessions and learned estimates remain deferred. | Structured goal plans are current; automatic milestone management is excluded. | Review only the minimum checkpoint contract against existing snapshots/task membership. Do not resolve deferred policies as current prerequisites. |
| O14 · OPEN · unresolved | Sketch Journal architecture, media storage/privacy, suitable vision model and feedback evaluation. | Preserve the Phase 4 artistic vision without premature design. | Scope a selected slice separately; distinguish observations from subjective quality judgments and communicate uncertainty. |
| O15 · RESOLVED IN PART -> C19 | Task creation day and local calendar-day measurement are confirmed; timezone source, due-day boundary, overdue handling and explicit edits remain open. | C18 fixes the four choices; the user explicitly confirmed the creation-day anchor on October 21, 2026. | Preserve the original deadline across replanning. Resolve only the remaining date semantics before Part 2; no silent daily extension. |
| O16 · OPEN · unresolved | Minimal daily-proposal retention/replacement/acceptance, allocation units, completion/progress detail and compatible persistence/contracts. | Fresh proposals and durable tasks/progress are confirmed; implementation policies are not. | Review existing storage before choosing fields, tables or migrations. One accepted plan/date and the full catalogue remain proposals. |

**Sources:** [Product.md §7](Product.md#7-open-decisions-and-dependencies), [Architecture.md §L](Architecture.md#l-architectural-decisions-and-open-questions), [Database.md §9](Database.md#9-decisions-needed-before-implementation), [AI_Integration.md §10](AI_Integration.md#10-open-decisions-and-next-review), and [Rules.md §10](Rules.md#10-review-checkpoint).

## 4. Unverified assumptions and missing evidence

These are **OPEN · unverified**, not decisions. This table retains verification needs rather than asserting all evidence is absent: Tasks.md, Running.md, Model_Verification.json and Part4_Report.md contain later hardware/implementation/smoke records. They are not reverified here; task statuses and prerequisites are not marked resolved by this alignment. No new verification date is established by this alignment. The 2026-10-18 technical-reference dates in other documents establish reference consultation only.

| ID | Claim that must not be assumed | Evidence still needed |
| --- | --- | --- |
| V01 | A candidate satisfies the challenge's open-weight AI/submission requirements. | Official challenge rules, deadline/artifacts and exact model/license comparison. |
| V02 | A local model fits the available machine and runs fast enough. | Actual device specifications, compatible runtime/model artifact and measured memory/cold/warm behavior. |
| V03 | A hosted endpoint serves the intended eligible model with required schema capabilities. | Provider/model identity, API behavior, cost, terms and integration checks; local and hosted capabilities may differ. |
| V04 | The complete app is offline-capable, private by design or ready for public access. | Verified end-to-end architecture, processing destinations, access protection and deployment checks. |
| V05 | Proposed implementation, database migrations, real inference or evaluation already works. | Actual authorized implementation and recorded test/results; specifications alone are not delivery evidence; consult the separate implementation records without treating their limited checks as complete Phase 1 verification. |
| V06 | Delivery timeframe, budget, team familiarity and hosting resources are sufficient. | User constraints and feasibility review; no build estimate is validated here. |

## 5. Maintaining the log

```text
Explicit user approval + known evidence
    -> update only the authorized log scope
    -> record exact approved choice, reason, alternatives and date if known
    -> preserve replaced decision with an explicit superseded reference
    -> report changes and wait for review
```

Keep IDs stable. Do not infer approval from silence, file existence or a request to write the next document. For an undated approval, keep “Not recorded.” If a new choice conflicts with an approved requirement, ask which takes precedence before changing either. Update related documents only when separately authorized; a log entry is not permission to modify them.