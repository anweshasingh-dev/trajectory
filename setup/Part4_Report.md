# Part 4 implementation report

Draft edits remain proposals until the exact saved revision is explicitly approved. Approval creates an immutable snapshot and stable task membership in one transaction; replacement preserves prior snapshots and archives removed tasks. Rejection never changes the current approved plan.

Validation: 50 automated tests passed (`python -m pytest -q` in the project virtual environment). Headless Chrome passed synthetic add/remove/reorder, nested input-name, size-limit and entered-data-retention checks. A real Qwen3 4B request completed in 20.23 seconds, was edited to revision 2, approved exactly, duplicate-approved safely and reopened after a fresh app instance; see Review_Verification.json. JavaScript syntax and git diff whitespace checks passed.

Limits: actual-work logging and completion controls are next; deletion is still pending. AI content needs review, and assumptions never become confirmed goal facts. This is not a broad visual accessibility audit. Changed task wording or effort creates a new task identity; exact unchanged task content is reused from the immediately preceding current plan.

No files were renamed or deleted. Existing goals/drafts are preserved by additive tables. Earlier draft revisions are overwritten while editing, but approved snapshots are immutable.

## Files and verified saved line ranges

| File | Operation | Lines | Purpose |
| --- | --- | --- | --- |
| README.md | Modified | 1-129 | Current implementation status. |
| setup/Running.md | Modified | 1-72 | Review workflow, storage and replacement rules. |
| setup/Review_Verification.json | Added | 1-92 | Real-model edit/approve/restart evidence on synthetic data. |
| trajectory/__init__.py | Modified | 1-30 | Register review routes. |
| trajectory/storage.py | Modified | 1-103 | Initialize additive review tables. |
| trajectory/routes.py | Modified | 1-105 | Protect all POST forms and load review/approved state. |
| trajectory/review_storage.py | Added | 1-130 | Review transactions, immutable snapshots, stable task membership. |
| trajectory/review_service.py | Added | 1-59 | Revision/freshness checks and explicit approval/rejection policy. |
| trajectory/review_routes.py | Added | 1-65 | Edit/review HTTP endpoints and unsaved error feedback. |
| trajectory/draft_editor.py | Added | 1-37 | Bounded HTML form parsing and effort conversion. |
| trajectory/templates/_draft.html | Modified | 1-47 | Approved-plan display and explicit review actions. |
| trajectory/templates/_plan_content.html | Added | 1-7 | Shared read-only plan rendering. |
| trajectory/templates/_editor_fields.html | Added | 1-23 | Reusable labeled milestone/task inputs. |
| trajectory/templates/draft_form.html | Added | 1-23 | Draft editor and separate save-for-review action. |
| trajectory/static/draft_editor.js | Added | 1-81 | Add/remove/reorder, field naming, focus and unsaved warnings. |
| trajectory/static/workspace.css | Modified | 1-77 | Review/editor layout and control styling. |
| tests/test_review.py | Added | 1-230 | Exact revision, replacement, rollback and concurrent approval checks. |
| setup/Part4_Report.md | Added | 1-32 | This change and verification report. |
