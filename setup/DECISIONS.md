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

**Date convention:** “Not recorded” means an exact decision/approval date was not established. Document modification times and reference-check dates are not approval dates. All open entries have **no decision date**. No superseded decisions are recorded because no explicit replacement decision has been established.

The user has referred to the existing setup documents as approved references. Several document headers still say draft/proposed, and their open-decision sections remain explicit. Document-level approval is not evidence that each proposed technology, schema detail, or numerical guideline was individually settled. Those choices stay open here; no source document is edited by this log.

## 2. Confirmed decisions and requirements

The alternatives column describes what a requirement rules out or leaves available; it does not claim those alternatives were evaluated or rejected in a separate historical discussion. Reasons summarize the user's stated intent, not invented validation results.

| ID / status | Decision | Reason | Alternatives / boundary | Decision date |
| --- | --- | --- | --- | --- |
| C01 · CONFIRMED | Keep setup documentation in `setup/`; work on one explicitly authorized file/change scope, report, then wait for approval. | User requested a controlled, reviewable workflow. | Batch creation and incidental edits are not authorized. | Not recorded |
| C02 · CONFIRMED | Documentation only at this stage; no code, dependencies, framework initialization or application scaffolding. | User explicitly limited this phase to setup. | Implementation needs separate authorization. | Not recorded |
| C03 · CONFIRMED | Defer Design.md while other specifically requested setup documents proceed. | User wants to plan visual direction, journeys and interactions separately. | Do not infer layouts, animations or detailed UI behavior from the technical documents. | Not recorded |
| C04 · CONFIRMED | Use a genuine open-weight model meaningfully in planning; verify the exact model, license and challenge fit before claiming eligibility. | Explicit challenge-related product requirement. | Model/runtime/provider selection remains open; mocks alone do not establish real integration. | Not recorded |
| C05 · CONFIRMED | Separate AI suggestions from deterministic scheduling constraints, validation, persistence and numerical forecasts. | User requires testable application logic grounded in recorded data. | The model may propose work/orderings; it cannot authorize writes or establish completion forecasts. Exact scheduling/forecast policies remain open. | Not recorded |
| C06 · CONFIRMED | Support a flexible, multi-interest career trajectory with inspectable, editable persistent context. | User's Career Navigator update explicitly requested continuity across changing interests. | Exact MVP depth and storage/retrieval mechanisms remain open; full chat storage is not required. | Not recorded |
| C07 · CONFIRMED | Require confirmation for important goal/commitment changes; explain possible mismatches respectfully and honor confirmed intentional detours. | User explicitly preserves control over direction and exploration. | No automatic distraction labels, shaming or silent priority changes. Review dates do not authorize goal changes. | Not recorded |
| C08 · CONFIRMED | Let users inspect/correct stored context and request deletion; distinguish structured facts, approved summaries and historical context. | Explicit persistent-context requirements. | RAG does not guarantee truth; deletion timing, retention and implementation remain open. | Not recorded |
| C09 · CONFIRMED | Use cohesive modules with separate routing, services, persistence, AI, frontend assets/components and tests where appropriate. | User explicitly requires understandable responsibilities and maintainability. | No giant catch-all application; no arbitrary file-count splitting. Final structure depends on approved stack/requirements. | Not recorded |
| C10 · CONFIRMED | For small learning-focused code edits, keep the smallest prior implementation as a temporary comment above its replacement; explain the change. Use a diff/before-and-after for large changes. | User's mandatory learning-oriented reporting policy. | User removes temporary comments after understanding; this does not authorize coding during setup. | Not recorded |
| C11 · CONFIRMED | Report every file operation, purpose, verified final line ranges, execution-flow changes and actual test results; never invent evidence. | User's explicit completion-report requirements. | No fabricated features, metrics, user feedback, verification or line numbers. | Not recorded |
| C12 · CONFIRMED | Keep the creative-practice journal in future scope unless explicitly approved for MVP. | User repeated this exclusion in the original brief and Navigator update. | No journal/sketch storage is required for the initial release. | Not recorded |
| C13 · CONFIRMED | Avoid unnecessary dependencies/infrastructure, keep changes small, and never silently expand scope or settle major choices. | User's original constraints and Rules.md request explicitly require this. | A justified addition still needs authorization within the relevant change scope. | Not recorded |

### Confirmation evidence

- **C01–C02, C04–C05, C09–C13:** Original controlled-setup request; reflected in [Product.md](Product.md), [Architecture.md](Architecture.md) and [Rules.md](Rules.md). The later Rules.md request explicitly reiterates scope control, small changes and dependency restraint.
- **C03:** User's Architecture Documentation request explicitly postpones Design.md; Architecture.md Sections A/L preserve this boundary.
- **C06–C08, C12:** User's Personal Career Navigator update; reflected in Product.md Section 3.1 and future-scope section. Later architecture/AI requests reiterate deterministic logic and initial-versus-future scope.

## 3. Open choices — proposals are not approvals

All rows below have **decision date: not decided**. Consult the source sections for detailed options; this log intentionally does not duplicate their contracts or schema.

| ID / status | Choice or proposal | Reason to resolve | Alternatives / input needed |
| --- | --- | --- | --- |
| O01 · OPEN · unresolved | Exact initial planning loop, navigator depth and acceptance criteria. | Product.md Sections 4–5 still label these proposed. | Approve/revise the minimal slice versus a reduced release; advanced history/roadmap features need separate approval. |
| O02 · OPEN · proposed | Python + Flask/Jinja + modular browser JavaScript/CSS + Pydantic + SQLite/sqlite3 + pytest. | Architecture.md B/L recommends this for a small project but leaves stack approval open. | FastAPI if API needs dominate; Django if account/admin needs dominate; richer frontend or server database only if justified. |
| O03 · OPEN · unresolved | Exact model artifact, license and inference route. | Meaningful eligible open-weight use is required, but no selected model/license has verification evidence. | Evaluate exact candidates and local/hosted inference after official rules and hardware/budget inputs are available. |
| O04 · OPEN · proposed | Ollama as a conditional local candidate; bounded synchronous calls and complete non-streamed structured responses. | Simplifies initial integration if compatibility and latency permit; Architecture.md and AI_Integration.md keep it conditional. | Compatible alternative runtime/provider; minimal job/status workflow only if measurements justify it. |
| O05 · OPEN · proposed | AI suggests ordering/allocation; deterministic code places tasks in intervals. | AI_Integration.md Section 2 narrows scheduling responsibility to avoid model arithmetic. | Approve/revise the proposal within C05; scheduling policy, horizon and granularity still need selection. |
| O06 · OPEN · proposed | Database.md's 12-table schema, singleton profile, UUIDs, typed context, daily plan lifecycle and conservative revision invalidation. | Concrete schema recommendations are not proof of individual choice approval. | Review ownership, relationship/JSON provenance trade-offs, concurrent edits, plan history and migration approach; redesign for multi-user access if needed. |
| O07 · OPEN · unresolved | Progress units/precision, remaining-work corrections, forecast formula, evidence window, uncertainty and goal roll-up. | Comparable recorded progress is needed for honest forecasts. | Review task-specific quantities versus approved alternatives; never infer completion from time alone. |
| O08 · OPEN · proposed | One-off/weekly local-time windows, UTC stored instants, midnight splitting and earlier applicable parent/task deadline. | Database.md proposes manageable time semantics, but exceptions/DST and deadline precedence need approval. | Define timezone/DST, recurrence exceptions and deadline rules before implementation. |
| O09 · OPEN · unresolved | Important-change boundaries, detour review behavior, context retention, proposal expiry, deletion completion and backup/provider handling. | User control is confirmed; exact operational policy is not. | Specify what is stored, confirmed, purged and restored; choose timings and failure/retry behavior. |
| O10 · OPEN · unresolved | Local single-user versus hosted demo, accounts/security boundary and durable deployment storage. | Determines access protection, model reachability and database suitability. | Choose demo format after official challenge rules, host constraints and budget are known. |
| O11 · OPEN · proposed | 300-line file / 40-line function soft review guidelines. | Rules.md Section 2 introduces these numerical recommendations with exceptions. | Approve/revise thresholds; preserve cohesive modules without arbitrary splitting. |
| O12 · OPEN · proposed | AI evaluation starter set of 20 cases, three attempts per candidate/case, and proposed release gates. | AI_Integration.md Section 9 recommends an evaluation design, not completed tests. | Approve/revise test scope, quality thresholds, timeout/context/output budgets and response-time target. |

**Sources:** [Product.md §7](Product.md#7-open-decisions-and-dependencies), [Architecture.md §L](Architecture.md#l-architectural-decisions-and-open-questions), [Database.md §9](Database.md#9-decisions-needed-before-implementation), [AI_Integration.md §10](AI_Integration.md#10-open-decisions-and-next-review), and [Rules.md §10](Rules.md#10-review-checkpoint).

## 4. Unverified assumptions and missing evidence

These are **OPEN · unverified**, not decisions. Their verification date is **not established**. The 2026-10-18 technical-reference dates in other documents establish reference consultation only.

| ID | Claim that must not be assumed | Evidence still needed |
| --- | --- | --- |
| V01 | A candidate satisfies the challenge's open-weight AI/submission requirements. | Official challenge rules, deadline/artifacts and exact model/license comparison. |
| V02 | A local model fits the available machine and runs fast enough. | Actual device specifications, compatible runtime/model artifact and measured memory/cold/warm behavior. |
| V03 | A hosted endpoint serves the intended eligible model with required schema capabilities. | Provider/model identity, API behavior, cost, terms and integration checks; local and hosted capabilities may differ. |
| V04 | The complete app is offline-capable, private by design or ready for public access. | Verified end-to-end architecture, processing destinations, access protection and deployment checks. |
| V05 | Proposed implementation, database migrations, real inference or evaluation already works. | Actual authorized implementation and recorded test/results; current documents are specifications, not evidence of delivered features. |
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