# Design and implementation rationale

Status: design approved and initial implementation built, 2026-10-28/29. Read [VERIFY.md](VERIFY.md) for actual results and limitations. The complete contract is [the revised prompt](../xp-github-prompt.md).

## Package and responsibilities

One skill, `github-xp`, supplies coherent XP planning and GitHub coordination from Story to release. Separate skills would currently fragment shared rules and duplicate discovery. Its entrypoint stays under 200 lines and routes to six references:

- `xp.md`: planning game, examples, developer/customer responsibilities, implementation feedback, and scope decisions.
- `agents.md`: host-neutral delegation, role boundaries, handoff contract, isolated work, review evidence, and sequential fallback.
- `integration.md`: workflow ownership discovery, work-brief/result contract, adoption conflicts, and integration examples.
- `github.md`: command contracts, IDs, pagination, API capability handling, and permissions.
- `history.md`: records, velocity, carryover, corrections, and retry invariants.
- `setup.md`: installation for the four hosts, setup inspection, and exact manual GitHub steps.

`assets/` contains Story/Task/Spike forms and the PR template. `scripts/xp.py` contains the command dispatcher and domain decisions; `scripts/github.py` contains constants, gh/git subprocess calls, reads, mutation previews, and reconciliation helpers. Tests and contributor documentation stay at repository root; runtime must not depend on them. The prompt contains the proposed full tree.

Runtime dependencies are Python 3 stdlib, GitHub CLI, and Git. No Python package installation, model CLI, hosted service, or MCP dependency. Development lint tooling may be separate from runtime requirements.

## Native GitHub workspace is a primary deliverable

The aim is to re-create XPlanner's core experience inside GitHub, not only provide an agent planning/reporting layer. A human should be able to open the Project, browse Stories and Tasks, plan an iteration, inspect progress and dependencies, and understand release scope without invoking an agent. Skills configure, explain and maintain this workspace and integrate it with engineering agents.

Target surfaces: Backlog table; Iteration Planning table with Story Points totals; Current Iteration board/table with native hierarchy/progress; release view and iteration roadmap; attention view; and native Insights charts. For each, validate actual filters, fields, grouping, sorting and aggregation. Native capability requiring UI setup is still in scope; scriptability determines setup method, not whether the experience is delivered.

Prioritize native capabilities over bespoke metadata. Reports supplement gaps in accepted-delivery history and provide interpretation, rather than substitute for usable views. The authorized dataset spike in this repository will resolve the exact layout, automation and historical-metric limits before the final build. All sample delivery is explicitly synthetic.

## Integration boundary

The skill owns XP planning and its GitHub representation. It feeds bounded work into an existing engineering workflow and reconciles the returned evidence; it does not replace that workflow's coding agents, local review, bot polling, CI, merge gate, or cleanup. Existing specifications retain authority over requirements. Inline criteria and linked authoritative criteria are both supported.

Read [INTEGRATION.md](INTEGRATION.md) for the concrete langlearn-anki case study, responsibility map, unresolved adoption conflicts, and work-brief/result contract. Default to integration with the discovered workflow. Provide a small standalone recipe only for responsibilities no existing workflow owns; do not build two engines or a general-purpose adapter framework.

## Primary workflow: solo owner with agents

The default user is one developer who may serve as product manager, software engineer, or both. Team use shares the same data model and respects the team's existing responsibilities. Personal-account Projects are a first-class path; no extra human, organization, or artificial agent account is required.

A typical workflow is: the owner describes an outcome → the coordinator and planning agent propose a Story and slices → the owner approves scope → implementation agents work on bounded Tasks → a reviewer/test agent checks the resulting changes → the existing workflow integrates verified work → the skill reconciles the owner's valid acceptance evidence. Acceptance can already have occurred in a required pre-merge demo; do not demand it again. The owner may implement any Task personally or take over at a handoff. An explicit acceptance delegation can be honored; an implementation agent cannot manufacture it.

Delegation is a core capability, not a mandatory ceremony. The coordinator selects useful roles rather than always launching planner, implementer, tester, and reviewer. Reuse existing implementation and review agents for substantive coding rather than add a second review pipeline; tiny work can stay in one agent when repository policy allows. Hosts without sub-agent support use sequential execution and disclose that review was not independent. Dispatch uses the host's available mechanism, not calls to another model CLI from Python.

### Ownership and handoffs

- Each dispatch carries issue references, criteria, scope, repository guidance, branch/worktree, dependencies, authorized actions, and the required result format.
- Give each concurrent implementation agent its own branch/worktree and bounded Task. Do not let multiple agents write the same worktree. The coordinator serializes shared planning/history mutations and integrates in dependency order.
- Return changed files, commit/branch, actual test results, acceptance coverage, blockers, and remaining work. A review names the inspected revision; changes after review require appropriate re-verification.
- Persist useful outcomes and current responsibility in GitHub rather than relying on a sub-agent session. Assignees remain real GitHub identities; agent role is context, not a claimed independent account or human approval.
- The existing workflow owns review-loop policy. Bound this skill's own planning/reconciliation retries to two unsuccessful attempts, stopping earlier without progress; preserve work and report blockers. Human takeover uses the same handoff contract.

The owner is the product acceptance authority by default, even if they also implemented the change. Do not require a second human reviewer or create branch rules requiring one for solo use. Respect existing repository rules and surface conflicts rather than bypassing them. Agent review is useful evidence, not a substitute GitHub approval from a separate person.

Capacity includes the human's product decisions, review, and integration availability. More agents do not automatically increase planned Story points. Prefer few active Tasks and parallelize only independent work that can be integrated promptly.

Tiny Stories need not acquire a dummy Task. `xp-start` and `xp-finish` accept a Task or an explicitly unsplit Story; the latter's PR references the Story without closing it, preserving the separate acceptance step.

## Interfaces

Common options: `--owner`, `--project <number>`, `--repo <owner/repo>`, `--history-issue <issue-url>`, `--dry-run`, and optional structured `--json` output. Commands needing local Git accept `--workdir`; it is independent of the installed skill path. Structured plans/bodies arrive as JSON or literal text on stdin, avoiding shell quoting and persistent local state.

Creation and bulk writes accept a stable `--operation-id` carried from preview to execution. `--apply` selects mutation mode; it is not itself proof of user authorization. The agent must verify existing session authorization for the displayed scope. Explicit issue/Project identifiers avoid title ambiguity. Repeated operations discover existing objects through markers and identity checks.

Defaults are defined once: Points, Iteration, Story/Task/Spike, fallback labels, seven-day duration, and six displayed velocity periods. Semantic status roles map to existing options, normally Todo/In Progress/Done. Preserve custom status options. Multiple plausible Projects or duplicate field names require explicit selection rather than automatic creation.

## Proposed GitHub-only history

Use one designated planning-log issue in a user-selected repository, excluded from velocity and release milestones. Setup may create it only as part of its approved scope. A supplied issue URL avoids automatic discovery ambiguity. This is ordinary GitHub content, not a new local database.

Each record is a human-readable issue comment with a versioned machine-readable JSON block and stable marker. Proposed fields:

| Record | Identity and contents |
|---|---|
| Plan | `schema_version`, `project_id`, `iteration_id`, `operation_id`, `recorded_at`, ordered Story node IDs/URLs, Points snapshots, linked open Tasks, availability assumptions |
| Acceptance | Stable Story credit key, Story node ID/URL, acceptance iteration ID, Points snapshot, product-decision timestamp, completion/credit timestamp after required integration, evidence URLs and revision, decision reference, operation ID |
| Close | Project + iteration key, start/end dates, planned/added/removed/accepted/carried Story snapshots, total accepted Points, next iteration ID, operation ID, reflection |
| Correction | Prior record ID, reason, explicit authorizing decision, replacement values or reversal; never silently overwrite a published total |

Comments are editable/deletable in GitHub, so this is auditable application history, not tamper-proof storage. Detect malformed, missing, or conflicting records and report incomplete history. Do not fabricate exact historical totals from current mutable fields.

Credit is once per Story across the selected Project history. A reopen preserves the original published period report; accepting it again does not award points twice. If the original acceptance was invalid, record an explicit correction and label restated reports. Newly discovered scope should normally become a new Story. A legacy closed Story without acceptance history is unverified, not automatically velocity credit.

The planning average includes the last three completed recorded periods, including zero totals. A missing period is shown as missing and makes the result incomplete; do not silently replace it with an older period. Dates use an explicit project calendar policy; choose UTC as the documented baseline and display it. Acceptance in a break or overlapping/ambiguous iteration requires explicit resolution.

Iteration close first captures the scope and completion report, then performs approved moves. On retry, the stable close record identifies the original source and target; already-moved items are skipped. This prevents a second close invocation from advancing work another week. An accepted Story retains its acceptance-iteration assignment; open Tasks move with unfinished parents, while completed Tasks remain in their completed period.

An acceptance write can fail between recording intent and closing the issue. Implementation must distinguish a pending record from finalized credit: reconcile the issue's completed closure, evidence revision, and record before finalizing. Velocity ignores pending acceptance. Do not use latest `closedAt` alone to infer acceptance history.

## Commands and API families

The live spike exercised setup, issue hierarchy, dependencies, scheduling, views and rollover primitives; it did not implement the commands below. See [SPIKE.md](SPIKE.md) for observed behavior. Validate input types and target-host support before implementation.

| Command | Read / write mechanics |
|---|---|
| setup | Owner/repository/default-branch queries; Project/field/view inspection; `createProjectV2`, `createProjectV2Field`, `createProjectV2View` where supported; organization issue-type REST or repo-label REST; templates via Git branch and PR |
| story | REST create issue with explicit rendered body/type or labels; `addProjectV2ItemById`; optional Points via `updateProjectV2ItemFieldValue` |
| split | Read parent, existing children, dependencies and operation markers; REST create issue then `/issues/{number}/sub_issues` and dependency endpoints; add Project items |
| plan | Read ranked view/items and history; create plan comment; `updateProjectV2ItemFieldValue` for Iteration on selected Stories/open Tasks |
| start | Read parent and blockers; hand off the work brief to the existing workflow; reuse its branch/worktree; issue assignee/status updates once work starts. Local Git helper only where no workflow owns branching |
| finish | Consume returned revision/test/review/demo/PR evidence; verify links and reconcile completion; no competing merge/poll/cleanup loop. PR helper only where no workflow owns creation |
| accept | Read criteria, Tasks, evidence and acceptance decision; history comment protocol; REST issue update with completed reason; reconcile/finalize credit |
| close-iteration | Read complete current scope/history; write close record; update unfinished assignments; resume against fixed source/target record |
| velocity | Read and validate paginated history comments; calculate accepted totals and sample counts; no mutation |
| release | Read milestone issues and acceptance records; inspect tag/target and existing draft; milestone REST update; `gh release create --draft` or reuse draft |

Source-code Tasks require integration and verification; a closed-not-planned Task is a scope change requiring a customer decision, not proof of completion. Non-code Tasks can complete with documented evidence. A missing or malformed acceptance section must fail closed. For acceptance parsing, support inline criteria or references to identified sections of authoritative documents. Record the criteria revision and criterion-to-evidence mapping; do not treat a link alone as proof. Ignore unrelated checklists and fenced examples. Reuse an existing operator decision only while its evidence remains valid under repository rules.

## Capability matrix

| Capability | Evidence on 2026-10-28 | Build consequence |
|---|---|---|
| Issue types | [Official organization REST endpoints](https://docs.github.com/en/rest/orgs/issue-types) | Probe support and permissions per owner; personal-repo labels; do not silently mask authorization failures |
| Native sub-issues | [Official REST endpoints](https://docs.github.com/en/rest/issues/sub-issues) | Resolve numeric IDs and page children; verify native auto-add membership; add only if absent and assign Iteration explicitly |
| Native dependencies | [Official REST endpoints](https://docs.github.com/en/rest/issues/issue-dependencies) | Use blocked-by semantics; detect self-links/cycles before proposing changes |
| Project field/iteration/view mutations | [Official Projects GraphQL reference](https://docs.github.com/en/graphql/reference/projects) lists field and view create/update operations | Verify input shapes and actual target support; do not assume gh field-create covers Iteration |
| Iteration filters | [Official iteration field documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects/understanding-fields/about-iteration-fields) | Current view may use `@current`; read current/completed iteration definitions, including gaps |
| Built-in status workflows | [Official workflow documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-built-in-automations) | Closed/merged status updates exist; auto-add and closed→Done verified live; Done→close disabled through UI. Document UI configuration where needed |
| Closing keywords | [Official linking documentation](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue) | Target default branch; qualify cross-repo Task references; do not close the parent from its Task PR |
| Views / Insights | Eight native views created; iteration/milestone grouping verified; scope chart saved through UI | REST supports grouping; chart filter and roadmap mapping still need UI checks. Manual priority order remains unverified; scope totals are not accepted velocity |

The initial 401 was resolved by removing an invalid GH_TOKEN override from CLI subprocesses and using the existing valid keyring login. The authorized live spike now provides API and partial UI evidence; see [SPIKE.md](SPIKE.md).

## Setup/manual decisions

Setup must report which capabilities are automated, need a UI action, or are blocked. In particular:

1. Select Project, repositories, and planning-log issue/repository explicitly. Match existing fields before creating anything.
2. Create views by supported API, or provide steps to make Backlog (open Stories, unset Iteration, manual order), Current (`Iteration:@current`, hierarchy visible), and Planning (future/unassigned work). Exact filters depend on types versus fallback labels.
3. Verify workflow semantics. Allow closed→Done bookkeeping; do not let Done→close bypass acceptance. Keep auto-archive off until historical reporting is verified. Discover and reuse native auto-add; verify membership before any explicit add. Children still require explicit scheduling.
4. Preserve existing issue/PR templates. Propose only needed mapping changes through repository review. If new forms are needed, support Markdown criteria or authoritative criteria references, not required checkboxes that falsely imply acceptance at issue creation.
5. No custom parent-closing Action in v1. Explicit acceptance satisfies the workflow without additional credentials or asynchronous races.

## Deliberate revisions to the original prompt

- One portable package and dispatcher instead of ten compulsory scripts and Claude-only scope.
- Practical XP behavior alongside GitHub mechanics, with solo development and delegated agent work as the primary use case.
- XP planning and GitHub reconciliation integrate with existing engineering workflows instead of owning another review/merge engine.
- Owner-level Project with personal-owner fallback, not an org-only contradiction.
- Points only on Stories, eliminating the optional-Spike-Points inconsistency.
- Default branch discovery and permitted local Git commands, resolving “gh only” versus branch creation.
- Evidence and customer acceptance replace “all boxes checked” as sufficient completion.
- Minimal GitHub history prevents rollover and reopened issues from rewriting velocity.
- Explicit acceptance replaces an unnecessary automatic parent-closing Action.
- Native APIs are verified, not assumed from dated claims; API failures do not become fake capability findings.
- A line-count target yields to readable correctness, with overruns explained.

These choices formed the approved implementation contract. The user-authorized spike created a demonstration Project and dataset and configured its views/workflows. The final skill package now exists locally; no external engineering workflow was changed.

## Initial implementation details

The skill has one short entrypoint with task-specific workflow references in addition to the shared XP, integration, agent, API and history references. The stdlib helpers use `--context`, structured `--input`, stable operation IDs and preview-by-default execution; the exact installed contract is [github.md](../skills/github-xp/references/github.md). Source examples above describe semantic commands rather than literal flags.

Setup is staged, reuses explicit Project/field identities, and configures selected view filters/columns. Grouping, sums, workflows and Insights retain documented UI setup paths. The helper validates live PR merge/default-branch/head facts and required evidence structure; the agent adjudicates specifications and product decisions. Corrections support explicit acceptance revocation and separate published-total restatement. Runtime size exceeds the approximate line target to retain readable recovery and complete pagination; see VERIFY.
