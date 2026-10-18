# Trajectory — Coding and Project Rules

> **Status: Rules draft for review.** Based on `Product.md`, `Architecture.md`, `Database.md`, and `AI_Integration.md` in this directory. Their approved boundaries apply; choices still labeled proposed or OPEN DECISION remain unresolved. These rules authorize no implementation or additional files.

**MUST / MUST NOT** are requirements. A **soft guideline** allows a justified exception, explained in the change report.

## 1. Approval and scope: one reviewable step

```mermaid
flowchart LR
    A[Read current requirements] --> B[Confirm authorized scope]
    B --> C[Make only that change]
    C --> D[Verify and explain]
    D --> E[Stop for review]
    E -- Explicit approval --> B
```

- MUST work on one explicitly authorized file or change scope at a time. During setup, create/edit only the named document; no helper files, code, configurations, generated assets, dependency installations, or directory scaffolding.
- MUST finish the authorized scope, report the result, then stop. Approval of one document does not authorize another. A revision request authorizes changes only within that document/scope; do not advance until explicit approval such as “Approved. Create the next file.”
- MUST inspect current files before editing and preserve unrelated/user changes. Do not rename, delete, overwrite, reorganize, or reformat other files as incidental cleanup.
- MUST ask before expanding scope. If a necessary fix crosses the boundary, explain the dependency and leave it untouched until authorized. For later coding work, a multi-file scope must be explicitly approved; do not infer it from a one-file request.
- MUST stop for a precedence decision if a new requirement contradicts an approved requirement. Preserve proposal/future/OPEN DECISION labels; document approval does not silently resolve every open choice inside it.
- MUST keep the creative journal, broad historical RAG, advanced roadmaps, collaboration and other future features outside initial implementation unless separately approved. Keep `Design.md` deferred; do not invent visual layouts, pages, animations or detailed interactions now.

## 2. Small changes and modular structure

- MUST make each change understandable as one purpose. Avoid unrelated refactors, opportunistic rewrites, duplicated implementations and speculative abstractions. Read the surrounding execution flow before replacing it.
- MUST use the approved architecture's responsibility boundaries. Its directory tree is illustrative; create only modules required by an authorized implementation task.
- MUST NOT build the whole application in one `app.py`, `index.html`, stylesheet or JavaScript file. Equally, do not split cohesive code into tiny files to meet a file-count target.
- **Soft guideline:** Aim for implementation files around 300 lines or fewer and functions around 40 lines or fewer. Review larger units for mixed responsibilities; split only at a meaningful boundary. Explain cohesive exceptions, such as declarative schemas, without padding or arbitrary splitting. These are review prompts, not automatic failures or instructions to refactor unrelated files.

| Layer | Responsibility | Keep out |
| --- | --- | --- |
| Routes | Parse requests, apply access scope, call services, return HTML/JSON. | SQL and business calculations. |
| Services | Coordinate workflows, confirmations, versions and transaction boundaries. | UI rendering and runtime-specific inference details. |
| Domain logic | Pure scheduling, capacity and forecasting calculations with explicit inputs. | HTTP, database writes, model calls and hidden clock/global-state dependencies. |
| Persistence | Connections, parameterized queries, record mapping and integrity constraints. | Prompts, templates and unrelated domain policy. |
| AI integration | Task prompts, contracts, adapter calls and validated proposals. | Direct database authority or autonomous goal changes. |
| Frontend | Reusable templates/components, feedback and draft editing. | Secrets, direct inference access and authoritative constraint checks. |

MUST pass dependencies and state through clear interfaces. Do not access another module's private state or scatter mutable global state. Centralize shared design tokens/components; separate page-specific styles/behavior when justified by the later design.

## 3. Naming and code clarity

| Area | Rule |
| --- | --- |
| Python, if retained | `snake_case` files/functions/variables; `PascalCase` classes; `UPPER_SNAKE_CASE` constants. |
| SQL | Descriptive `snake_case` names matching Database.md; singular `_id` references and explicit units such as `_minutes`. |
| JavaScript | `camelCase` functions/variables; meaningful module exports. Follow existing conventions for filenames. |
| CSS | Descriptive `kebab-case` classes and centralized custom properties; avoid page-wide overrides for a local component. |
| Shared vocabulary | Use consistent names for task, commitment, draft, accepted plan, actual progress, decision and detour across layers. |

- MUST prefer explicit names over abbreviations and catch-all names such as `misc`, `stuff` or a growing `utils` module.
- MUST make public service/adapter inputs and results explicit, with type annotations/contracts where applicable. Document non-obvious assumptions, units and failure cases; comments should explain reasons rather than restate syntax.
- MUST preserve domain distinctions: unknown is not zero; time spent is not completed work; a proposal is not confirmation; archiving is not deletion. Avoid implicit conversion between incompatible progress units.

## 4. Validation, persistence and deterministic calculations

1. MUST validate at the server boundary: allowed fields, types, required values, finite quantities, ranges, dates/timezones, record references and ownership. Browser validation is supplementary.
2. MUST apply service/domain checks for cross-record rules: schedule overlaps, usable capacity, task/block agreement, context status, exact proposal versions and source references. A row CHECK or valid JSON cannot establish these alone.
3. MUST re-read current versions and revalidate edited proposals immediately before acceptance. Use short atomic transactions, rollback on failure and duplicate-safe acceptance; never hold a write transaction open during inference.
4. MUST enable/verify foreign keys on each SQLite connection if SQLite is retained. Use constraints and parameterized queries; no string-built SQL from user/model content. Follow the approved schema through reviewed migrations; never silently recreate a real database.
5. MUST keep forecasts, placement and schedule constraints in deterministic code. Retain every task submitted for planning, explain unscheduled work and calculate capacity/shortfall without trusting model arithmetic. The exact placement policy remains open in AI_Integration.md.
6. MUST derive forecasts from validated progress, remaining workload and explicit capacity assumptions. Explain missing evidence instead of inventing a date; never sum incompatible units or let model text override calculated values.
7. MUST preserve the distinction between accepted schedule history and actual work. A replacement plan requires explicit acceptance. Deleting plan associations must not silently delete independently recorded progress.

## 5. AI and personal-context boundaries

- MUST keep the model/runtime behind the architecture's replaceable adapter. Use bounded task-specific prompts and versioned input/output schemas; do not introduce agent frameworks or model tools for the existing bounded workflows.
- MUST validate complete outputs before treating them as proposals: reject malformed/oversized responses, extra fields, unsupported actions, invalid references and stale context. Do not silently weaken validation when a runtime lacks a capability.
- MUST present interpretations separately from saved facts and identify supporting records where practical. A valid citation, structured response or retrieval result does not prove a claim true. Ask when evidence is missing or contradictory.
- MUST require confirmation of exact extracted details and important goal/commitment changes. Respect confirmed detours; a new interest is not automatically a distraction, and a review date is not permission to change goals.
- MUST select only relevant authorized context, exclude pending/failed-deletion targets, and recheck sources before displaying or accepting in-flight results. Apply Database.md's approved version/invalidation policy; do not implement a different dependency policy silently.
- MUST allow inspection/correction/deletion of saved context and clean up dependent summaries, drafts, caches and future indexes. Mark cleanup complete only after the defined live-data cleanup succeeds. Do not retain deleted content indefinitely under a soft-delete flag or in logs.
- MUST NOT assume full chat retention, embeddings, vector storage or historical RAG. Verify the exact model artifact, license, runtime/device fit and challenge eligibility before claiming them. Low temperature is not deterministic execution; local inference does not prove offline operation or privacy.

## 6. Errors, security and configuration

| Situation | Required behavior |
| --- | --- |
| Invalid input or missing evidence | Field-level feedback or a focused clarification; no invented defaults saved as facts. |
| Stale versions or conflicting edits | Reject the stale change and request review; no silent overwrite. |
| Inference unavailable/invalid | Bounded failure, actionable retry/manual-edit path, saved work preserved. No infinite repair loop or partial application. |
| Persistence failure | Roll back incomplete changes; distinguish unsaved work from a successful save followed by a calculation failure. Retry must not duplicate writes. |
| Unexpected error | Safe user message plus request ID and useful operational diagnostics; never swallow exceptions or report false success. |

- MUST treat model text, notes, titles, links and retrieved material as untrusted data. Escape rendered content; never execute generated code/SQL/HTML or permit model-selected filesystem/network actions. Do not automatically fetch stored resource URLs.
- MUST keep secrets in environment/deployment configuration outside Git and browser assets. Examples use placeholders. Validate configuration on startup and redact credentials from errors/logs.
- MUST keep endpoint/model selection, timeouts and input/output budgets server-controlled. Do not expose local inference directly to public clients or accept arbitrary user-provided inference endpoints.
- MUST protect browser mutations against CSRF, use suitable session-cookie settings if sessions exist, and avoid permissive cross-origin defaults. Keep a local single-user demo on loopback and disable debug mode when exposed to others.
- MUST resolve authentication, per-record authorization, transport/storage protection and abuse limits before public multi-user access. The proposed singleton profile is not an account/security system.
- MUST approve hosted inference data handling before sending personal context. Log operational IDs, durations, versions and error categories; avoid ordinary logging of raw prompts, personal notes, full outputs or hidden reasoning. Retention/backup/deletion promises require an approved policy and evidence.

## 7. Dependencies, documentation and decisions

- MUST add a dependency only for a concrete approved requirement. First consider existing modules and the standard library; explain the benefit, maintenance cost and simpler alternative. No extra framework, queue, service or infrastructure merely because it is available.
- MUST obtain authorization before dependency/configuration changes outside the current scope. Pin compatible versions when implementation is approved; do not install tools during setup or change lockfiles incidentally.
- MUST keep setup documentation in `setup/` and application code separate. Reference the owning document instead of duplicating schemas, prompt contracts or complete test plans here.
- MUST keep confirmed requirements, proposals, future scope and OPEN DECISION visibly distinct. If an authorized code change requires a documentation change outside its scope, report the needed update and request authorization; do not leave a contradictory claim presented as current.
- MUST record approved architectural decisions in DECISIONS.md only when that file/change is authorized. Do not fabricate features, test results, performance, user feedback, license verification or submission compliance.

| Document | Governs |
| --- | --- |
| Product.md | Product behavior, MVP boundaries and future scope. |
| Architecture.md | Layers, module communication and deployment boundaries. |
| Database.md | Data meaning, integrity, corrections and deletion. |
| AI_Integration.md | Model selection evidence, prompts/contracts, validation and evaluation. |
| Rules.md | How authorized work is changed, verified and reported. |
| Design.md / Testing.md | Deferred design / later detailed test plan; do not create them implicitly. |

## 8. Testing and honest verification

- MUST run checks appropriate to the authorized change. Test changed business rules and regressions with meaningful cases; do not add tests solely for a file count or tests that merely mirror implementation. For a documentation-only change, inspect consistency, links/paths, diagrams and final line ranges; application tests are normally unnecessary.
- MUST keep scheduling/forecasting unit tests independent of model/network access with explicit time/capacity inputs. Use temporary databases for integrity, rollback, correction/deletion, restart persistence and duplicate-acceptance checks; never use personal production data for tests.
- MUST test approval rejection, malformed outputs, unknown sources, stale drafts, detour handling and in-flight correction/deletion when those behaviors change. Use fake adapters for deterministic checks; evaluate exact real-model behavior separately as specified in AI_Integration.md.
- MUST report commands actually run and their results. State failures, skipped/blocked checks and limitations plainly. Fake adapters do not prove real inference works; a small passing evaluation does not prove universal reliability.
- MUST keep verification within the authorized file/change scope. If writing a test or artifact requires another file, request the expanded scope first; do not bypass the workflow to achieve coverage. A necessary unrun check means verification is incomplete, not passed.

## 9. Learning-oriented edits and completion reports

### Preserve a small comparison when requested

For small, localized code edits the user wants to learn from, MUST preserve the smallest relevant previous implementation as a clearly labeled temporary comment immediately above the replacement, using valid comment syntax. Explain what changed, why and the concept involved. Do not copy secrets or sensitive personal data into comments.

MUST NOT preserve old code as comments for large refactors, full-file rewrites or multi-module changes. Use a Git diff or a concise before-and-after explanation instead. Temporary comments must not become permanent alternate implementations: the user will remove them manually after understanding. Do not silently remove them in unrelated work; flag remaining temporary comments during relevant review. This policy does not authorize application-code generation during setup.

### Required final report

| Report item | What to include |
| --- | --- |
| Every file operation | Exact path of each created, modified, renamed or deleted file and its purpose. |
| Verified line ranges | Final saved line ranges for changed sections; for renames use the final path. For deletions, state that no final-file range exists. Never invent line numbers. |
| Behavior and learning | What changed, why, the concept involved, and important execution-flow changes; for documentation, identify decisions and remaining questions. |
| Verification | Actual checks/tests and results, including incomplete verification and material limitations. |
| Review boundary | What needs review; stop and wait for explicit approval before the next scope. |

Before reporting completion, MUST inspect the saved result for contradictions, unnecessary repetition, accidental scope changes and unintended file edits. Do not claim full completion when required authorized work remains undone.

## 10. Review checkpoint

- [ ] Only the authorized file/change scope was touched.
- [ ] Responsibilities, data meaning and AI boundaries remain intact.
- [ ] No proposal/open choice was silently treated as settled.
- [ ] Relevant checks and final line ranges were verified honestly.
- [ ] The completion report explains the result and stops for review.

**Still open:** Existing choices about stack/model, deployment, scheduling/forecasting semantics and retention remain with their owning documents. The new 300-line file / 40-line function soft guidelines in Section 2 are recommendations for approval with this rules draft, not reasons to restructure existing work now.