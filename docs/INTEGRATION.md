# Scope and integration with agentic development

Design case study, inspected 2026-10-28. The requested `~/Coding/langlearn-anki/WORKFLOW.md` is located at `docs/ENG-WORKFLOW.md`; there is no root `WORKFLOW.md` in that checkout. Also inspected the relevant workflow/issue-management sections of `CLAUDE.md` and `docs/ENG-DEVELOPMENT-GUIDE.md`. These are local observations, not verified remote repository state. No files in langlearn-anki were changed.

## Product boundary

GitHub XP supplies **an XPlanner-like workspace built from native GitHub features, plus XP planning and coordination around an existing engineering loop**. It answers what outcome matters, which work is next, how much to commit to, what is blocked, whether a Story is accepted, and what was delivered in an iteration or release.

The existing loop answers how to implement, test, review, demonstrate, merge, and clean up a change. Agents can perform both kinds of work, but one coordinator should own execution. This skill provides the planning context and consumes evidence; it does not install a second agent supervisor.

| In scope | Out of scope |
|---|---|
| Stories, useful Task decomposition, Spikes, priority, estimates and iteration planning | A new coding methodology framework, mandatory PRDs/epics, or ceremonies for every change |
| Fully configured native Project views, totals, hierarchy, dependencies, roadmap, Insights charts, milestones and planning history | A separate tracker/web dashboard, local task database, or compulsory migration of every existing issue |
| XP guidance at decision points: small slices, feedback, sustainable pace and customer acceptance | Replacing repository-specific test commands, coding conventions or authoritative specifications |
| Focused planning/acceptance sub-agents and work briefs for existing engineering agents | Model routing, provider setup, mandatory agent rosters, background daemons, bot polling or orchestration infrastructure |
| Linking PRs, verifying completion, consuming test/review/demo evidence | A parallel review loop, extra diff-review approval, new merge gate, or branch cleanup engine |
| Story acceptance and iteration/release reporting | Assuming CI/agent approval proves the product works; performing domain-specific human checks |
| Release scope validation and draft notes | Automatic publication, deployment, version policy or operational monitoring |

A small standalone recipe can fill a genuinely missing responsibility. It must not replace a responsibility already owned by the target workflow. Optional helpers remain callable independently; no workflow engine or custom adapter code is required to integrate them.

## What langlearn already provides

`docs/ENG-WORKFLOW.md` is more developed in GitHub use than the initial characterization suggests:

- Lines 12–22: the operator owns direction and Anki verification, agents own engineering/review, and GitHub issues are the tracker. Findings within an open PR's scope stay in that PR.
- Lines 29–54: branch-based work, test-first bug fixes, small verified commits, local review, an Anki demo where applicable, and PR creation.
- Lines 65–82: a precise merge gate covering latest-revision CI and remote review, resolved threads, conflict status, and a still-valid operator demo.
- Lines 84–91 and 112–118: authorized merge and cleanup already have an owner and tool choice.
- Lines 126–132: the project explicitly avoids a heavier worker/evaluator mission framework and other orchestration machinery.

The missing layer is not basic GitHub usage. It is the planning and feedback model connecting customer outcomes to ordered work, timeboxes, estimates, acceptance history, and release scope. Existing test-first work, small commits, agent review and product demonstrations already support parts of XP; preserve them.

`CLAUDE.md` lines 254–330 make specifications authoritative and issues brief references to misalignment. The integration must not turn Story bodies into competing specification documents or require issues for every incidental correction.

## Minimal handoff contract

Use a short issue/PR reference or ordinary structured message. This is an information contract, not a new network API or mandatory persistent artifact.

**Work brief supplied to the existing coordinator:**

- Story/Task identity and intended customer outcome.
- Inline criteria or authoritative document sections, with the revision being used.
- Scope boundaries, blockers/dependencies, and selected iteration when scheduled.
- Expected evidence and the person or explicit policy authorized to accept it.
- Relevant local workflow instructions; existing branch/worktree if work already started.

**Result returned by the existing coordinator:**

- Work identity, PR URL and reviewed/tested revision; merge revision/state when applicable.
- Actual test/review results and links, plus known gaps or blockers.
- Demo artifact/revision, operator decision, and which criteria it establishes where relevant.
- New scope discovered, distinct from findings already fixed within the Task.

The XP skill verifies accessible GitHub state and reconciles Project Status, Task/Story completion, and history. It does not treat a worker's bare “done” message as verification. Durable evidence belongs in existing GitHub artifacts; do not require uploading full internal agent transcripts or duplicating test logs.

## Integration points in langlearn

| Existing point | XP/GitHub addition | Preserve |
|---|---|---|
| Operator requests a change | Shape/reuse a Story; reference specs and decide priority | Operator's product/design authority |
| Before `pr_loop(change)` | Select work from the agreed plan; supply Task/Story brief; mark In Progress once started | Existing branch, small-commit and quality-gate rules |
| During local/remote review | Keep fixes inside current scope; capture genuinely new scope for later planning | Existing reviewers, polling, thread handling and merge gate |
| Operator checks a deck | Link the existing confirmation to the criteria and artifact revision it covers | Actual Anki verification; no new human diff-review requirement |
| Existing loop opens a PR | Verify Task-closing and parent-reference links on that PR | Local review before opening; no duplicate PR |
| Existing merge/close-out | Reconcile Task status, then evaluate Story acceptance from all required evidence | Authorized merge method and cleanup; no new merge permission prompt |
| Iteration boundary | Report accepted/carried work, reflect, and replan | No change to engineering loop execution |
| Release preparation | Check scope and produce Story-centered draft notes | Existing versioning/publication process |

Operator acceptance can precede merge, as in the existing demo. Store that evidence then; finalize Story completion and velocity credit only when all acceptance and integration conditions hold. Record the product decision time separately from the completion/credit time so a pre-merge demo cannot award delivery credit before integration. A subsequent relevant change invalidates evidence according to the existing workflow's rules.

An Anki confirmation only establishes the criteria it actually demonstrates; it is not a blanket approval of every Story. Reuse it when sufficient, and report specific missing evidence otherwise.

## Adoption choices that must remain explicit

These are proposed integration changes, not changes already made to langlearn:

1. **Issue formats.** Its current issue template describes misalignment. Proposed Story/Task/Spike support should retain concise references to authoritative specifications and add only planning/acceptance metadata needed for the chosen work. Do not overwrite existing issue forms or retype the backlog automatically.
2. **Closure ownership.** Its close-out closes resolved issues generally. Once a Story aggregates Tasks, close-out should close completed Tasks and pass the Story to acceptance reconciliation. An unsplit Story's PR references it without automatic closure. This is an adoption change to the existing closure rule, not something installation silently rewrites.
3. **Acceptance representation.** Allow criteria linked from specifications, and persist a concise evidence/decision reference on GitHub. Neither unchecked form boxes nor a specification link alone proves acceptance.
4. **Review policy.** Reuse its review-until-clean gate. The earlier proposal's universal two-cycle engineering review limit is withdrawn; limits on this skill's own reconciliation retries do not change the engineering gate. Unresolved work remains unresolved.
5. **Tool ownership.** The deterministic XP helpers use `gh` for their own GitHub operations. The host workflow may continue using its required GitHub MCP merge tool. “gh only” is not a restriction on the caller's existing workflow.

If these choices are not adopted, the skill can still provide read-only XP planning advice and previews. It must report the boundary and not claim full lifecycle automation is configured.

## Suggested workflow addition

This is a proposed instruction snippet for adoption, not an executed command or a replacement workflow:

> Use GitHub XP to shape and select the next Story or Task and supply its criteria/specification references. Execute the existing PR loop unchanged for engineering, reviews, demos, and merge. Reuse valid operator demo evidence. After close-out, reconcile the completed Task and evaluate its Story against all acceptance criteria; leave unaccepted Stories open. Feed new scope and blockers back into planning. At iteration boundaries, use GitHub XP to report delivery and propose the next plan.

The snippet requires the closure and issue-format decisions above to be adopted first. The final skill should offer a similarly small project-specific addition after inspecting a target workflow, with no automatic edit merely from installation.

## Validation cases added to the build contract

Verify integration without duplicate branches, PRs, reviewers, or human gates; linked-spec criteria; pre-merge demos and later evidence invalidation; in-scope review fixes without new issues; an already-authorized merge; mixed legacy and XP issues; and explicit reporting of incompatible closure/issue policies. Test the plain handoff with a fixture workflow modeled on these behaviors, without requiring langlearn's private assets, Anki, or live bot services.
