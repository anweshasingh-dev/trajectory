# Trajectory — Submission Brief

> **Status: Planning-stage draft, not a submission-ready product claim.** Updated 2026-10-19. Workspace inspection found setup documents and Git configuration, but no application implementation. No working model integration, customer validation, revenue or traction is evidenced.

## 1. Challenge and project overview

**Challenge:** Hacktoberfest Open-Source AI Challenge, Week 2: Side Hustle. User-supplied prompt: “Build something with open-weight models or open-source AI that someone would actually pay for.”

**Trajectory:** A planned Goal-to-Plan Assistant for people turning learning and project ambitions into editable work they can follow and track. Its longer-term vision combines realistic scheduling, progress-based forecasts and a user-controlled Personal Career Navigator.

**Submission timing needs attention:** The [official challenge page](https://dev.to/challenges/hacktoberfest-week2-2026-10-12) currently displays **Ended**. The [launch announcement](https://dev.to/devteam/join-the-hacktoberfest-open-source-ai-challenge-side-hustle-2550-in-prizes-across-18-winners-55ba) lists October 18, 2026 at 11:59 PM PDT, equivalent to **October 19, 2026 at 12:29 PM IST**. Do not assume a late-entry exception; confirm organizer guidance before claiming eligibility. The previously stated three-day build window is not an official extension.

## 2. Problem and target users

Students, independent learners and freelancers can have clear ambitions but struggle to break them into actionable work, keep plans updated and compare intentions with actual progress. This is the product's problem hypothesis, not a finding from completed customer research.

**Proposed initial customer focus:** Independent learners building portfolio projects alongside courses or work. They offer a specific first workflow to validate while preserving students and freelancers as the broader intended audience.

## 3. Proposed solution and value proposition

**Planned promise:** Describe a goal, review a useful starting plan, and keep approved work and progress together instead of repeatedly reconstructing a plan from disconnected notes or chat responses.

The intended distinction is continuity and user control: model-generated suggestions become editable structured work only after approval, with actual progress retained for later use. Later releases would use that evidence to adjust schedules and forecasts, and maintain a flexible career direction across multiple interests. This is a proposed differentiation, not a verified claim of superiority over competing tools.

## 4. AI component and why openness matters

| Area | Intended approach / current evidence |
| --- | --- |
| Meaningful Phase 1 role | An open-weight model interprets natural-language goals, suggests tasks/milestones and asks about missing dates or available hours. No integration is implemented or demonstrated yet. |
| Runtime | Isolated backend adapter; Ollama is a conditional local candidate. Hosted inference/Colab may be evaluated, but no route is selected or benchmarked. |
| Model and license | **TBD:** exact publisher/model revision, artifact/quantization, model card, license and commercial-use/redistribution conditions. Runtime availability is not license verification. |
| Reliability boundary | Validate structured outputs, references and current versions; preserve saved work on failure. Users review exact changes before acceptance. Scheduling constraints and numerical completion forecasts remain deterministic application logic, not model predictions. |
| Open-based value hypothesis | Inspectable/swappable model choices could reduce dependence on one closed provider and permit workflow-specific prompting. Cost, local execution and data-handling benefits require measurements and architecture evidence; none is claimed as achieved. |

The challenge allows open-source AI approaches, but Trajectory's existing plan specifically requires meaningful open-weight model use. Adding an open-source framework solely for a label would not fulfill that project requirement. No new agent framework, vector database or full-chat retention is assumed. See [AI_Integration.md](AI_Integration.md) for contracts, selection evidence and evaluation proposals.

## 5. Business potential — hypotheses to validate

| Potential paying customer | Possible paid value, not a committed feature | Why they might pay |
| --- | --- | --- |
| Independent learner / student building a portfolio | A dependable goal-to-plan workflow with saved approved plans and progress. | Less repeated planning/admin work and a clearer next action; value must exceed a free task list plus generic chat. |
| Freelancer balancing learning and delivery | Later capacity-aware planning, overload warnings and evidence-based replanning. | Help make workload trade-offs and revise expectations using actual work; no guarantee against missed deadlines. |
| Learner managing several career interests | Later persistent trajectory, decision history and intentional-exploration reviews. | Avoid repeatedly explaining context while retaining control over changing priorities. |

**Commercial options, still open:** A one-time local-app purchase or paid convenience features; a hosted subscription only if hosting, security and unit economics justify it. No price, payment flow or business model is approved. Correction/deletion and user control remain baseline requirements, not proposed premium restrictions.

**Next validation:** Let target users try the first workflow; observe whether they can approve and use the plan, what they return for, what they currently use instead, and whether they would pay for the specific benefit. Record actual feedback/payment only if obtained. Compare willingness to pay with inference, hosting, maintenance and support costs; local inference does not mean zero cost. No interviews, paid pilots, sales or retention evidence are currently recorded.

## 6. Current status and planned MVP

| State | Scope |
| --- | --- |
| Existing | Product, architecture, database, AI, design, rules, test-plan, roadmap and decision documentation. P1.01 prerequisite review is In Progress in Tasks.md; implementation tasks remain Not Started. |
| Approved direction, not implemented | Local single-user Phase 1 app; Python, Flask/Jinja, modular browser assets, SQLite/sqlite3 and Pydantic/pytest, as recorded in Tasks.md after explicit user approval. Versions are unselected; older architecture/decision text still labels these choices open and needs separately authorized alignment. |
| Phase 1 planned MVP | Capture a goal; generate real-model task/milestone proposals and clarification; review/edit/approve; mark tasks complete and record actual work; reopen saved records after restart. No full career navigator or calendar engine is required for this first release. |
| Phase 2 planned | Daily schedules, available time/recurring commitments, overload, planned-versus-actual comparison, deterministic forecasts and editable replanning. |
| Phase 3 planned | Multi-interest Personal Career Navigator, editable confirmed context, resource/decision history, respectful alignment advice and intentional detours. |
| Future possibilities | Historical-note RAG, richer roadmap/exploration reviews and creative-practice journal/sketches; other exploratory backlog remains subject to approval. |

**Before claiming MVP readiness:** Settle Phase 1 ordered-plan/milestone schema and AI contracts; select/verify a model and inference route; implement the approved slice; run relevant deterministic and real-model checks. Product.md's broader proposed MVP is staged by the later approved [Tasks.md](Tasks.md), not deleted. No performance, privacy, offline capability or customer outcome is established by these plans.

## 7. Links and demo evidence

| Item | Link / placeholder | Evidence status |
| --- | --- | --- |
| Repository | [anweshasingh-dev/trajectory](https://github.com/anweshasingh-dev/trajectory) | Configured Git remote; public accessibility, published code and reproduction instructions not verified. |
| Video demo | `[TODO: video URL]` | Not supplied; record the actual working build, not an implied completed product. |
| Live deployment | `[TODO: deployment URL, or state local-only]` | No deployment verified; local app is the approved Phase 1 direction. |
| Run instructions / demo commit | `[TODO: instructions path and tested commit]` | No runnable app or tested commit identified. |
| Model evidence | `[TODO: exact model card, revision, license and runtime evidence]` | Not selected/verified. |
| DEV submission post | `[TODO: published post URL]` | No submission made by this task. |

**Planned demo sequence:** Use synthetic data to capture a learning/project goal, clarify missing details, generate a real proposal, edit/approve it, record actual work, then restart/reopen. Include a failure/retry example if available and state exactly which parts work. The official template permits a deployed link or video; the challenge page links the template. Do not claim a recorded/mock response demonstrates live inference unless it actually did. [Submission template entry point](https://dev.to/challenges/hacktoberfest-week2-2026-10-12)

## 8. Submission checklist

Unchecked means pending verification/preparation, not completed.

- [ ] Resolve entry timing/eligibility with the organizer; read the challenge-specific and general official rules linked from the challenge page, including participant eligibility and original-project requirements.
- [ ] Use the official DEV submission template with `devchallenge` and `hf26challenge` tags; review the required sections and team-credit instructions if applicable. [Official participation guidance](https://dev.to/challenges/hacktoberfest-week2-2026-10-12)
- [ ] Show a working demo and accessible code/run instructions; verify links from a fresh browser/session. Distinguish local execution, deployment, video and simulation.
- [ ] Identify the exact model/open-source AI component and its meaningful contribution; verify model/runtime/code licenses, required attribution and suitability for the intended commercial use.
- [ ] Explain why open innovation matters using observed evidence; do not claim lower costs, privacy, offline operation or better quality without verification.
- [ ] Run current-phase approval/persistence/failure tests and real-model evaluation; record actual results, limitations, hardware/runtime and demo commit. Keep forecasts/scheduling deterministic.
- [ ] State the customer and paid-value hypothesis clearly. Report first-user feedback, payment or traction only if real; otherwise say validation is pending.
- [ ] Remove secrets/personal data from repository/demo; use synthetic records and disclose any hosted inference destination.
- [ ] Enter partner categories only for technology genuinely used and matching verified category rules. First-user and agent-session sections are optional, not fabricated requirements. [Official challenge guidance](https://dev.to/challenges/hacktoberfest-week2-2026-10-12)
- [ ] Replace placeholders, update current status, remove unsupported completed-feature wording and obtain user approval before publishing/submitting.

**Open questions:** Organizer confirmation of any valid entry route after the listed cutoff; full eligibility compliance; exact model/license/runtime and inference budget; real demo/repository accessibility; willingness to pay and commercial packaging. Recheck official rules before submission. External sources and workspace status were inspected on 2026-10-19; this draft does not certify compliance or publish an entry.