---
name: github-xp
description: "Practice Extreme Programming through GitHub Issues and Projects: shape Stories, plan iterations, coordinate agent work, reconcile acceptance, and report delivery. Use for XP planning and its GitHub workspace; integrate with the existing coding and PR workflow."
license: MIT
---

# GitHub XP

Help a solo developer working with agents, or a team, deliver small accepted outcomes through a native GitHub workspace. The human may act as product manager, engineer, or both. Use one coherent planning model and reuse the repository's engineering workflow.

Requirements: Python 3, authenticated GitHub CLI, and Git for repository inspection. Helpers target GitHub.com; no model CLI or MCP server is required.

## Select the workflow

Read only the references required by the request. Relative paths resolve from this skill's directory, not the target repository.

| Request | Read next |
|---|---|
| Install, adopt, configure or repair the workspace | [setup](references/setup.md); [integration](references/integration.md) when adopting into a repository |
| Shape a Story, split Tasks, investigate uncertainty, plan an iteration | [planning](references/planning.md) |
| Start or finish work, delegate, hand over to a human | [execution](references/execution.md); [agents](references/agents.md) when delegating |
| Accept a Story or reconcile an existing product decision | [acceptance](references/acceptance.md) |
| Close an iteration, inspect velocity, prepare release scope | [reporting](references/reporting.md) |
| Explain XP choices or resolve a process tradeoff | [XP decisions](references/xp.md) |
| Invoke a helper or troubleshoot GitHub capabilities | [GitHub contract](references/github.md) |
| Record or reconcile plans, acceptance, carryover or corrections | [history](references/history.md) |

For “plan my next iteration,” load planning; load history only when calculating delivery or recording the plan. Do not load setup, execution, or release guidance unless needed. For ordinary coding without a planning request, leave execution to the existing workflow.

## Establish context

Read repository instructions and the relevant existing workflow before changing planning or handing off implementation. Discover the selected owner, repositories, Project and current fields; do not infer a Project from a similar title. Ask only for unresolved choices that materially affect the work.

Keep specifications authoritative. A Story can link to exact specification sections and revisions instead of copying them. GitHub owns planning state; the repository owns product and engineering specifications. Do not introduce a second local tracker.

Use native Projects views as the working interface: ordered Backlog, Iteration Planning with Story Points totals, Current Iteration board, attention, release scope, roadmap and useful native Insights. Reports explain delivery/history gaps; they do not replace those surfaces.

## Preserve the model

- A **Story** describes customer value and testable acceptance criteria. Only Stories receive Points; missing Points mean unknown.
- A **Task** is a native child issue for useful execution work. No Points. A tiny Story may be implemented without artificial Tasks.
- A **Spike** answers a question within a timebox. Record learning; no velocity credit.
- An **Iteration** is the Project Iteration field; unset means backlog. A release is a repository milestone, not an iteration.
- Priority belongs to the customer's Backlog order. Do not invent a second priority field or silently substitute API enumeration order.
- Native dependencies describe blockers; hierarchy describes decomposition. Verify child Project membership and schedule it explicitly.
- Completed Tasks and green checks are evidence, not product acceptance. The owner or an explicitly authorized delegate accepts the Story.
- Credit accepted, integrated Stories once. Preserve Points on carryover, completed Tasks' periods, and closed-period history.

The helpers use a UTC calendar; make that policy visible. A different project calendar needs an explicit adaptation before automated credit. Agent count does not multiply capacity. Include the human's available decision, demonstration and integration time when planning.

## Work through the existing engineering loop

Supply bounded scope, criteria, dependencies and required evidence to the existing coordinator. Reuse its branches, implementation agents, reviewers, CI, demos, merge authorization and cleanup. Do not create a duplicate PR or a new review/merge gate. Fix in-scope findings in the existing work; create new planning objects only for genuinely new scope.

A valid existing operator demo or acceptance decision can be reused while its evidence remains applicable. Record the decision separately from completion: a pre-merge demo does not earn delivery credit until required integration is complete. An implementation agent cannot invent a customer decision.

Where no engineering workflow exists, use the small standalone recipe in execution. Hosts without delegation use the same handoff sequentially and disclose that review was not independent. Never require a second human or artificial GitHub agent identities.

## Execute and recover

Use `python3 <installed-skill-path>/scripts/xp.py --help` for the helper contract. The logical workflows are setup, story, split, plan, start, finish, accept, close-iteration, velocity and release. They are not automatically separate slash commands on every host.

Inspect and preview before writes. Apply only the scope already authorized by the user; skill activation and `--apply` do not grant new authority. Preserve authorization across turns instead of requesting it again. Installation does not authorize rewriting workflow files, migrating a backlog, or publishing a release.

For helper writes, use a stable operation ID and structured JSON, never shell interpolation of user text. A dry run may read GitHub but must not mutate GitHub, local branches/files, or credentials. Keep temporary inputs separate from durable planning state.

After partial failure, report completed steps and remaining work, reread GitHub, and resume the same operation. Do not retry uncertain creates blindly. Stop skill-owned reconciliation after two unsuccessful attempts or sooner without progress; do not replace the engineering workflow's review policy with this limit.

Return direct GitHub links and a concise account of what changed, evidence checked, and any unresolved conditions. Distinguish inspected capability, offline tests, and live execution. Never present synthetic fixtures, issue closure, or a current-scope chart as verified accepted delivery.
