# Integrate with an existing workflow

Read the target repository's instructions, development workflow, relevant specifications, issue/PR templates and merge rules. Inspect only the portions needed to understand ownership and the requested work. Do not assume that a file named `WORKFLOW.md` exists or import a particular repository's conventions universally.

## Responsibility map

| GitHub XP owns | Existing engineering workflow owns |
|---|---|
| Story outcomes, task decomposition, priority, iteration planning and capacity | Coding conventions, implementation, test commands and tool/model selection |
| Project fields/views, native hierarchy/dependencies, release scope | Branches/worktrees, commits and PR creation |
| Work briefs and evidence requirements | Implementation/review agents, bot polling, CI and review/fix loops |
| Task reconciliation, Story acceptance, carryover and accepted-delivery history | Merge authorization, integration, cleanup, deployment and operations |

Report concrete overlaps before adoption. A workflow that automatically closes every issue from a PR conflicts with unaccepted aggregate Stories. A specification-first repository does not need duplicated Story prose. Propose the smallest change; do not rewrite its policy merely because the skill is installed. Read-only planning remains useful while adoption decisions are unresolved.

## Work brief

Pass an ordinary structured message or issue reference to the existing coordinator:

- Story/Task identity and customer outcome.
- Inline criteria or exact authoritative document sections and revision.
- Bounded scope, exclusions, dependencies and scheduled iteration.
- Existing instructions, branch/worktree and current owner, if any.
- Required evidence, acceptance authority and actions already authorized.

## Returned evidence

Consume issue/PR identity, tested/reviewed revision, actual test and review results, integration state/revision, criterion-to-evidence mapping, applicable demo and product decision, unresolved blockers and genuinely new scope. Recheck accessible GitHub state. A bare “done” message is not enough; full private agent transcripts are unnecessary.

Reconcile existing valid acceptance evidence without a second human gate. A pre-merge operator demonstration can satisfy criteria once integration completes. If later relevant changes invalidate it, follow the repository's evidence-refresh rule. Do not convert a domain demo into blanket approval of unrelated criteria.

## Example adoption

An existing loop already creates a branch, runs tests, gets agent review, asks the operator to demonstrate the result, opens a PR, verifies CI/bot review, merges under existing authorization, and cleans up. Keep that loop. Add planning before it and reconciliation after it. Findings within the PR stay there; new customer scope returns to Backlog.

Suggested addition, only after closure ownership is agreed:

> Select the next Story or Task with GitHub XP and pass its criteria and scope to the existing engineering loop. Reuse valid operator evidence. After integration, reconcile the Task and evaluate Story acceptance; keep unaccepted Stories open. At the iteration boundary, report delivery and propose the next plan.
