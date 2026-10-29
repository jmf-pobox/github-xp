# Start and finish work

Use [integration](integration.md) when first connecting to a repository's engineering workflow. Use [agents](agents.md) only when delegating or handing over work.

## Start

Read the selected issue, parent if present, criteria, native blockers, current assignee, existing branch/PR and iteration. An open blocker prevents starting dependent implementation; a cancelled blocker requires an explicit scope decision rather than pretending it completed.

For an unsplit Story, establish that direct implementation is intended. Supply the work brief and let the existing coordinator create or reuse the branch/worktree. Preserve dirty work. Reconcile In Progress when work actually starts; do not mark active merely because a plan was proposed. Respect existing assignment and avoid replacing another contributor without authorization.

## Finish

Consume the existing workflow's tested/reviewed revision, criterion evidence, PR result and integration state. Recheck GitHub and identify gaps. Do not start a second reviewer loop, open another PR, merge, or clean up from this skill.

For a Task PR, use a qualified closing reference such as `Closes owner/repo#123`, targeting the actual default branch, and a non-closing parent reference such as `Story: owner/repo#100`. For a directly implemented Story use only the non-closing reference. Check the existing PR body before proposing edits. Closing keywords aimed at another branch do not establish default-branch completion.

A code Task completes after required integration and verification. A non-code Task needs explicit completion evidence. Closed as not planned is cancellation, not completed work. Preserve and report scope changes instead of counting cancelled Tasks as evidence. The `finish` helper reconciles the concrete result; it does not substitute a supplied Boolean for inspection of tests, reviews or product evidence.

A Story stays open until [acceptance](acceptance.md), even if all children are complete. The existing authorized merge remains owned by the engineering workflow and does not require a second permission request from XP.

## Minimal standalone recipe

Use this only for responsibilities no existing workflow owns. Inspect Git status/default branch, agree a small scope, create or reuse a short-lived branch or isolated worktree, implement with short test-first/refactor cycles, and run the repository's checks. Obtain useful independent review when available. Show the concrete diff and evidence; create one traceable PR after required gates pass. Integrate only under existing user authorization and repository rules. Preserve work and report blockers when a bounded review attempt cannot make progress.

This recipe supplies guidance, not a new runtime supervisor. It does not mandate an agent roster or require a second human. If a helper lacks a standalone branch/PR operation, the host agent can use normal Git/GitHub tools under these rules; do not claim it is automated by the helper.
