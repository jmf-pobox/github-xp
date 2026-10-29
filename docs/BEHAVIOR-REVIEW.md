# Independent behavior review

Date: 2026-10-29 UTC. An independent reviewing agent read the installed skill entrypoint and the integration, execution, delegation and acceptance references, then walked through the six scenarios below. This is an instruction-level review of intended agent decisions, not execution in Codex, Claude Code, OpenCode or Pi. It makes no claims about live tool dispatch, independent human approval, or real product acceptance.

## Existing engineering loop and prior demo

**Request:** Finish a Task whose existing branch and PR have passed the repository's reviews. The operator demonstrated revision A before merge. Merge was already authorized and the existing workflow reports it complete.

**Result:** Route through execution, then acceptance/history if the aggregate Story is ready. Reuse the existing PR, reviews and operator decision. Check the PR's actual default-branch merge, inspected revision and coverage of the Story criteria. Reconcile Task completion; accept the Story only if all conditions hold. Do not launch another reviewer, create another PR, request the same demonstration again, or add a new merge gate.

**Assessment:** The instructions preserve execution ownership and distinguish product decision time from integrated delivery credit.

## Solo product owner without sub-agents

**Request:** The owner wants to concentrate on product decisions, but the host cannot spawn sub-agents.

**Result:** Use the existing workflow sequentially, or the small standalone recipe for unowned responsibilities. Preserve the same bounded work brief and evidence requirements. Explain that review was not independent. Do not require an artificial agent account, a second human, or a separate model CLI.

**Assessment:** Delegation is useful but not a prerequisite for using the skill.

## Human takeover with uncommitted work

**Request:** The owner wants to take over a Task while the agent's worktree contains uncommitted changes and one failing test.

**Result:** Route execution to the delegation/takeover reference. Preserve the existing branch/worktree and edits. Hand over scope, current state, tests actually run, the failing test, blockers, and next action. Do not reset, start a duplicate branch, or claim completion.

**Assessment:** The handoff supports changing between product and engineering roles without losing work.

## Conflicting adoption policy

**Request:** Adopt GitHub XP into a repository whose workflow closes every referenced issue automatically when its PR merges.

**Result:** Identify the concrete conflict for aggregate Stories that still need acceptance. Propose the smallest closure-ownership change for the user to decide. Do not silently rewrite workflow files or override repository policy. Read-only planning can proceed while the adoption choice is unresolved.

**Assessment:** The skill remains an integration layer, rather than imposing a competing workflow.

## In-scope review finding

**Request:** A reviewer finds a defect within the Task's existing acceptance scope.

**Result:** Fix and verify it within the existing Task/PR and the repository's review loop. Create another issue only if the finding introduces genuinely new scope. Do not turn every review comment into planning overhead.

**Assessment:** The instructions preserve small feedback loops and avoid compulsory issue proliferation.

## Overlapping concurrent agents

**Request:** Two implementation agents are proposed for Tasks that both edit the same files in a shared checkout.

**Result:** Repartition the work or serialize it. Give each concurrent writer an isolated branch/worktree and bounded scope. Serialize shared Project/history mutations through the coordinator. Review must identify its inspected revision; relevant integration changes require renewed verification.

**Assessment:** Agent names alone are not treated as isolation or independent approval.

## Limits and follow-through

All six walkthroughs produced the intended decisions from the written guidance. They do not establish that every host will discover the skill, select the right reference, or execute the workflow correctly. Host discovery and execution results belong in [VERIFY.md](VERIFY.md), separately from this review.

The independent runtime suite in `tests/test_runtime.py` exercises deterministic invariants using fake transport and synthetic snapshots. It includes recovery after partial plan/acceptance/rollover writes, missing versus zero history, cancellation boundaries, stale evidence, actual default-branch checks, pagination, dry-run isolation and per-action Project field conflict checks. Per-action reads narrow the concurrent-edit window; GitHub does not provide an atomic compare-and-swap transaction for these multi-step operations.
