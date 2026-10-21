# Trajectory — Coding and Project Rules

**Status:** Simplified rules for review.

These rules govern how Trajectory is implemented and maintained. `Product.md`, `Architecture.md`, `Database.md`, and `AI_Integration.md` define their respective requirements and boundaries. Proposed features and unresolved decisions are not automatically approved.

**MUST / MUST NOT** indicate requirements. Recommendations allow reasonable exceptions.

## 1. Scope and Approval

- MUST read the relevant requirements and inspect existing code before making changes.
- MUST work on one clearly defined task or feature at a time.
- For documentation tasks, edit only the requested document unless additional scope is approved.
- For coding tasks, modify the related files necessary to complete the authorized task. Do not restrict changes to one file when a feature reasonably requires multiple files.
- MUST preserve existing functionality, user data, and unrelated changes.
- MUST ask before expanding scope, adding dependencies, changing the database schema, or introducing new features.
- MUST stop and ask when requirements conflict or an unresolved decision blocks implementation.
- MUST NOT implement future features merely because they appear in the roadmap.

The current MVP prioritizes the Goal Planner and Task Master. Advanced progress analytics, forecasting, calendar integration, historical context retrieval, and other future features remain out of scope unless explicitly approved.

## 2. Code Structure and Readability

- MUST follow the approved architecture and keep responsibilities separated.
- Routes handle requests and responses; services coordinate workflows; domain logic performs calculations; persistence handles database operations; AI integration handles model interactions and output validation; frontend components handle presentation and user interaction.
- MUST NOT put the entire application in one large file or split cohesive code into unnecessarily small files.
- MUST use clear names, explicit interfaces, and consistent conventions across modules.
- MUST avoid unnecessary abstractions, duplicated implementations, unrelated refactoring, and speculative infrastructure.
- MUST pass dependencies and state through clear interfaces rather than relying on scattered mutable global state.
- MUST keep configuration, reusable components, styles, templates, and application logic organized in appropriate locations.

Keep changes understandable and proportionate to the task. Refactor when it meaningfully improves maintainability, not simply to meet arbitrary file or function length targets.

## 3. AI Behavior and Data Integrity

- MUST keep model interactions behind the approved AI adapter. Do not introduce agent frameworks, tools, or autonomous workflows without approval.
- MUST treat model output as an untrusted proposal. Validate its structure, values, references, and permitted actions before using it.
- MUST NOT allow model output to bypass application validation, modify the database directly, or silently change a user's goals or commitments.
- MUST preserve user control over generated plans. Users must be able to review and edit proposals before accepting them.
- MUST distinguish suggestions from confirmed facts, accepted plans from drafts, and recorded progress from estimates.
- MUST keep deterministic calculations, scheduling constraints, and validation in application code rather than trusting model-generated arithmetic.
- MUST handle invalid output, unavailable inference, stale edits, and failed saves without silently losing existing work.
- MUST preserve relevant data when changing or hiding features. Do not silently delete records or recreate an existing database.
- MUST respect the approved data-correction and deletion requirements for features being implemented.

Use only the context necessary for an AI task. Do not assume that local inference guarantees privacy, offline operation, or deterministic output.

## 4. Security and Configuration

- MUST validate user input on the server, including types, ranges, dates, references, and record ownership where applicable.
- MUST use parameterized SQL queries and appropriate database constraints.
- MUST treat model output, user notes, links, and retrieved content as untrusted data. Escape rendered content and never execute generated code, SQL, or HTML.
- MUST keep secrets out of source code, browser assets, logs, and version control. Use appropriate environment or deployment configuration.
- MUST keep inference endpoints, timeouts, and input/output limits under application control.
- MUST handle errors without exposing credentials, sensitive information, or internal implementation details to users.
- MUST NOT claim that authentication, authorization, privacy, deletion, or offline guarantees exist unless they are actually implemented and verified.

Before public multi-user deployment, address the authentication, authorization, transport security, storage protection, and abuse controls appropriate to that deployment.

Implement security requirements proportionately to the current environment, without treating future deployment features as completed work.

## 5. Dependencies, Documentation, and Decisions

- MUST prefer existing modules and the standard library when they adequately meet requirements.
- MUST obtain approval before adding dependencies, infrastructure, or services that are not necessary for the authorized task.
- MUST keep setup documentation in `setup/` and application code separate.
- MUST maintain clear distinctions between confirmed requirements, proposed features, future scope, and unresolved decisions.
- MUST update documentation when an authorized change makes an existing requirement or description inaccurate. Ask before modifying documentation outside the authorized scope.
- MUST NOT fabricate implementation status, test results, performance figures, model capabilities, licensing claims, or user feedback.

Use each document for its intended purpose:

- `Product.md` — product behavior, MVP scope, and future features.
- `Architecture.md` — application structure and module responsibilities.
- `Database.md` — data models, relationships, integrity, and data lifecycle.
- `AI_Integration.md` — model selection, prompts, output contracts, and evaluation.
- `Rules.md` — coding workflow, implementation boundaries, and verification.

Do not duplicate entire specifications across documents. Refer to the document that owns the relevant requirement.

## 6. Testing, Reporting, and Review

- MUST run checks appropriate to the authorized change.
- MUST test relevant behavior and regressions, including failure cases when applicable.
- MUST keep deterministic calculation tests independent of real model inference or network access where practical.
- MUST use temporary or test databases for persistence and data-integrity tests.
- MUST report only checks that were actually run. Clearly identify failures, skipped tests, blocked checks, and limitations.
- MUST inspect the final changes for accidental edits, contradictions, and unrelated modifications.

### Completion report

When finishing a task, provide:

1. **Files changed:** Paths and a brief explanation of each change.
2. **What changed:** Important behavior or structural changes and their rationale.
3. **Verification:** Commands or checks actually run and their results.
4. **Remaining work:** Known issues, unresolved decisions, or incomplete checks.
5. **Review checkpoint:** What needs review before proceeding.

Include exact line ranges when useful or requested. Do not invent line numbers or claim completion when required work remains.

For small learning-oriented edits, explain the key concept and the relevant before-and-after behavior when requested. Do not preserve large amounts of obsolete code as comments; use a diff or concise explanation instead.

**Working principle:** Make the smallest complete, verifiable change that satisfies the approved task. Preserve user control, keep the implementation understandable, and stop at meaningful review checkpoints.
