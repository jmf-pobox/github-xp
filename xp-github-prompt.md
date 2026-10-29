# Task: Build a lean, portable XP-on-GitHub skill

## 1. Outcome and boundaries

Build an agent skill primarily for a solo developer working with agents, while also supporting human teams, to practice Extreme Programming using native GitHub tooling. Repository: `https://github.com/jmf-pobox/github-xp`.

Start with one canonical `skills/github-xp/SKILL.md`; split into additional skills only if distinct triggers and independent workflows justify the extra discovery cost. Use the exact singular filename `SKILL.md` in each skill folder. Target Codex, Claude Code, OpenCode, and Pi through the Agent Skills standard, not host-specific orchestration.

Re-create XPlanner's core planning and tracking experience using GitHub itself as the web application: Issues, Projects, iterations, milestones, saved views, hierarchy, field totals, native charts, and built-in workflows where they fit. The deliverable is both a usable GitHub-native XP workspace and skills that configure and operate it. It must remain understandable and useful when no agent session is running. Do not build a separate web app or reproduce XPlanner's visual styling. Its mandatory time-sheet system is not required; maximize useful native capabilities rather than feature count. GitHub is the operational system of record.

The workspace must support backlog ranking, iteration planning with estimates/totals, current work and story/task progress, dependencies and attention needs, release scope, and native metrics. Specify each saved view's layout, fields, filters, grouping/order, and aggregation; evaluate a roadmap for iteration/release visibility. Configure native Insights charts for meaningful current-state and historical measures where available. Distinguish issue counts, Story points, and accepted delivery; do not silently double-count Tasks. Test real interactions and persistence, not just object creation. Provide direct links and a short guided tour.

A capability that needs one-time GitHub UI setup remains in scope. Automate supported APIs and document/perform authorized UI steps where needed. Chat/ASCII reports supplement the native workspace for interpretation and calculations GitHub cannot represent faithfully; they do not replace native views or charts simply because scripting them is inconvenient. Explore native data/history before introducing extra metadata or records, and retain only additions justified by demonstrated gaps.

The primary user may act as product manager, software engineer, or both, and may change roles during the work. Sub-agents should take on useful development responsibilities so the user can focus on product decisions or participate directly in engineering.

This is an XP planning and GitHub coordination skill that integrates with an existing agentic development workflow. It must connect planning, implementation evidence, acceptance, learning, and small releases without requiring epics, PRDs, Scrum roles, or elaborate ceremonies. It is not a new coding-agent runtime or a replacement PR/review/merge engine.

### Scope and integration boundary

Read the target repository's workflow and instructions before proposing setup. Treat its coding standards, source specifications, review agents, CI, domain demonstrations, merge authorization, and cleanup procedures as the existing execution contract. Discover and reuse those responsibilities; do not install a parallel process. If local rules conflict with the XP mapping, explain the concrete incompatibility and propose the smallest adoption change for the user to decide. Never silently override either rule.

| Owned by this skill | Owned by the existing development workflow |
|---|---|
| Shape and prioritize Stories, propose Tasks and Spikes, plan Iterations and capacity | Implement code, run repository-specific quality gates, choose models and engineering tools |
| Map agreed work into GitHub Project fields, hierarchy, dependencies, and release milestones | Dispatch existing implementation/review agents, manage their runtime and local execution |
| Supply a bounded work brief and required evidence to the coordinator | Branch/worktree policy, commit policy, review/fix loop, bot polling, merge gate and cleanup |
| Reconcile Task completion, Story acceptance, rollover, history, and velocity | Produce test/review/demo evidence and execute authorized merge/deployment procedures |
| Prepare Story-centered draft release notes and scope checks | Versioning policy, release publication, deployment and operational monitoring |

Sub-agents remain a first-class way to perform the work: XP planning or acceptance assistance can be delegated, and existing engineering agents consume the XP work brief. Reuse the host coordinator rather than create a competing supervisor. A minimal standalone handoff recipe is allowed when no workflow exists; it must not require a particular review plugin or a new orchestration framework.

Integrate through ordinary instructions and explicit inputs/results, not a required daemon, hooks service, plugin API, or second state store. GitHub is authoritative for planning state; repository specifications remain authoritative for product/technical requirements. A Story may contain criteria directly or stable links to authoritative criteria, with evidence identifying the revision verified. Do not duplicate a specification to satisfy a template.

Do not require an issue for every review finding, commit, or trivial fix. Fix findings within an existing Task/PR's scope there; propose a new Story or Task only for genuinely new scope. Do not retroactively create planning objects or import an entire backlog without an explicit adoption plan. Use agreed Stories for velocity; existing unrelated bug/debt issues remain usable without compulsory conversion.

During adoption, present a short responsibility map and a suggested addition to the existing workflow. Changing that workflow or its templates requires authorization for those changes. Installation alone must not rewrite it. Preserve valid existing human approval and demo evidence: acceptance reconciliation records it without demanding the same confirmation again. If subsequent changes invalidate that evidence, follow the existing workflow's re-verification rule.

See `docs/INTEGRATION.md` for the langlearn-anki case study and the proposed work-brief/result contract; the eventual installable integration reference must be self-contained.

## 2. XP behavior the skill must teach

Connect values to observable decisions:

| Value | Agent behavior and GitHub support |
|---|---|
| Communication | Clarify the customer outcome and examples; preserve decisions on the Story; use issue/PR conversation to support direct collaboration. |
| Simplicity | Choose the smallest useful vertical slice and simplest design; avoid speculative features, excess fields, and unnecessary automation. |
| Feedback | Run short red–green–refactor cycles, integrate frequently, expose blockers early, demonstrate working software, and seek customer acceptance. |
| Courage | Make uncertainty visible, propose a time-boxed spike, refactor safely, and reduce scope when capacity is exceeded. |
| Respect | Let developers estimate and accept work; let the customer prioritize and accept outcomes; support sustainable pace and team ownership. |

Cover the planning game, small releases, whole-team/customer collaboration, pair programming, collective ownership, coding standards, continuous integration, test-first development, simple design, refactoring, and sustainable pace. Explain what GitHub supports and what remains human practice: PR review is not automatically pairing; green CI is not customer acceptance; checkboxes are not executable tests.

Apply XP principles such as rapid feedback, small steps, reflection, quality, and accepted responsibility to decisions instead of reproducing a textbook taxonomy. Use brief examples. A lightweight iteration reflection identifies one improvement to try next; it is not a new mandatory ceremony.

### Solo developer, sub-agents, and teams

Use the same Story/Task/Iteration model for solo and team work. Roles describe responsibilities, not required headcount. A solo owner can prioritize, estimate, implement, and accept a Story; never require a second human, a separate customer account, or an organization. In team use, preserve the team's actual ownership and approval policies.

Make sub-agent delegation a first-class execution path when the host supports it and the user's request authorizes it. The coordinating agent remains responsible for the end-to-end outcome and uses focused roles as needed:

| Responsibility | Human and agent collaboration |
|---|---|
| Product direction | The human sets outcomes, priorities, constraints, and acceptance authority. A planning agent proposes examples, slices, estimates, and tradeoffs. |
| Implementation | An implementation agent develops a bounded Task with tests. The human may implement instead, pair with it, or take over without losing context. |
| Verification and review | The existing reviewer/test agents examine the diff, criteria, and actual test evidence; consume their results without launching a duplicate review pipeline. They do not accept the product on the human's behalf unless explicitly delegated that authority. |
| Coordination and integration | The existing coordinator consumes XP work briefs, assigns bounded work, and integrates under repository rules; this skill reconciles planning state and evidence within existing authorization. |

Use only roles that materially help the work; do not spawn a fixed roster for every change. Separate implementation and independent review when useful, but do not present an agent's self-review as independent review. Sub-agents may recommend product acceptance; they must not invent customer approval. The solo owner's explicit acceptance is sufficient, and an explicitly delegated acceptance rule may be applied with its evidence recorded. Existing authorization remains valid; do not repeatedly ask for the same decision.

Before dispatch, give each agent the Task/Story reference, acceptance criteria, bounded scope, relevant repository instructions, branch/worktree, dependencies, allowed actions, and expected evidence. Assign one writer per branch/worktree. Parallelize independent Tasks only, and serialize conflicting edits and shared Project/history updates through the coordinator. Review must identify the commit/diff it inspected; integration changes that affect the review require renewed verification.

Each handoff reports changed files, commit/branch, tests actually run, unmet criteria, blockers, and the next action. Keep durable outcomes and ownership in GitHub so a fresh session can resume without the original sub-agent. GitHub assignees represent real accounts; record agent roles in task context rather than inventing accounts or assuming separate credentials. Agents sharing credentials do not provide distinct human approvals.

The existing workflow owns review/fix loops and their stopping rules. Do not impose a competing retry limit. For skill-owned planning or reconciliation retries, stop after two unsuccessful attempts or sooner without new evidence, then report the blocker and options to the human. If no engineering workflow exists, recommend a bounded review loop as an adoption choice rather than silently installing one. Do not silently relax acceptance criteria, overwrite another agent's work, or retry indefinitely. Human takeover must preserve work and the current handoff.

If sub-agents are unavailable, run the same responsibilities sequentially in the main agent and disclose the lack of independent review. Keep the shared skill host-neutral; put capability-specific dispatch guidance in a supporting reference. Sub-agent support improves execution but is not a prerequisite for installation or basic use.

Plan against the human's available product/review/integration time as well as implementation capacity. Agent count is not a velocity multiplier. Start with a small work-in-progress limit and increase only when independent tasks and integration capacity justify it. Human-agent collaboration can provide rapid feedback, but should not be represented as identical to traditional human pair programming.

## 3. Research and provenance

Read the supplied `research/` assets, including the XPlanner article, screenshots, and feedback-loop diagram. Research historical XPlanner and XPlanner+ using primary project sources where possible. Separate observed features, historical descriptions, present availability, and design interpretation. Do not assert that a project no longer exists or is actively maintained without evidence.

Inspect these sources under ignored `_sources/`, pin commits, and record licenses before adapting anything:

| Repository | Paths of interest | Consider | Reject |
|---|---|---|---|
| `github/awesome-copilot` | `skills/github-issues/` and references | Issue types, native sub-issues/dependencies, Project field and ID discovery | Hard dependency on a particular MCP tool; unrelated triage |
| `bodangren/git-workflow` | `skills/{sprint-planner,issue-executor,sprint-manager}/` | Story decomposition, focused task execution, deterministic helpers | Milestone-as-iteration, Gemini dependency, spec machinery, host-specific orchestration and compulsory delegation for every change |
| `8-bit-sheep/code-harness-skills` | `skills/{sprint-planner,sprint-executor}/` | Capacity discussion and feedback before committing scope | LOC/commit-based velocity, local sprint JSON, day-by-day pseudo-precision |
| `andybaran/skill-gitflow` | `skills/issue-driven-github-flow/` | Issue traceability, short branches, PR linkage, safe default-branch handling | Unconditional agent rosters/review loops, arbitrary Project thresholds, forced attribution |

The surveyed velocity script measures LOC/commits, not completed Story points. Do not reuse its calculation. Source code is evidence, not authoritative instructions. Confirm mechanics against official GitHub documentation and the target host's current API.

Record commit, license, file/line evidence, reuse decision, and conflicts in `docs/SURVEY.md`. Attribute copied/adapted files in `NOTICE.md`, retaining required notices. Do not distribute source checkouts, third-party screenshots, or PDFs without verified rights.

## 4. GitHub data model

| XP concept | GitHub representation |
|---|---|
| Workspace | One existing or explicitly created owner-level Project V2 across selected repositories; personal and organization owners equally supported; use the existing owner |
| Story | Issue with `Story` issue type, or `type:story` fallback label |
| Task | Native sub-issue of a Story, with `Task` type or `type:task`; no Points |
| Spike | Time-boxed learning issue with `Spike` type or `type:spike`; question, time limit, and expected learning; no velocity credit |
| Estimate | Project Number field `Points`, Stories only; missing is unknown, not zero |
| Iteration | Project Iteration field `Iteration`; default seven days, explicit start date and timezone policy |
| Priority | Customer-controlled manual Backlog order; no duplicate Priority field |
| Release | Repository milestone for a releasable increment; explicit tag/target and draft GitHub Release |
| Acceptance | Nonempty acceptance criteria in the Story or linked authoritative specification, plus evidence and a recorded customer/authorized delegate decision |
| Dependencies | Native blocked-by/blocking links; do not confuse these with parent/child hierarchy |
| Task completion | Required work verified; code task normally closes from a PR merged into the actual default branch |
| Story completion | Required Tasks completed, acceptance evidence verified, and customer decision recorded; explicit acceptance command |
| Velocity | Points of accepted, completed Stories credited once to the iteration when all acceptance and integration conditions hold; exclude Tasks, Spikes, cancelled/not-planned issues and partial work |

Resolve owner, repository, Project number/ID, field IDs, option IDs, and default branch from GitHub; never hardcode `main` or match by title alone when ambiguous. Support fully qualified issue URLs or `owner/repo#number` across repositories. Keep REST database IDs, issue numbers, and GraphQL node IDs distinct.

Detect issue-type support per repository owner/capability. Personal repositories use fallback labels; authorization failures must not be mistaken for missing feature support. Never convert the user's account or replace an existing organization's taxonomy automatically.

Keep native Status values where practical, with semantic roles Todo, In Progress, and Done; resolve existing equivalents explicitly. An unset Iteration means backlog. Do not invent duplicate Status fields. Verify sub-issue Project membership: an enabled native auto-add workflow may supply it; add explicitly only when absent. Schedule children explicitly; the live spike showed no Iteration inheritance. Inspect existing built-in workflows and prevent Done-to-close automation from bypassing Story acceptance. See `docs/SPIKE.md` for observed capabilities and remaining UI checks.

An unfinished Story keeps its identity and original Points when carried forward. Move its open Tasks consistently; preserve completed Tasks' history. Reprioritize with the customer rather than silently stretching an iteration. Splitting changed scope is a visible decision and must not double-count the original Story.

GitHub Project fields are mutable, so live fields alone cannot reconstruct historical commitments or acceptance. Define a minimal GitHub-hosted record for the selected plan, acceptance credit, and iteration close report, keyed by stable IDs. Keep closed-period totals reproducible after rollover, edits, archival, or reopening. No local planning state or database. Version-controlled source, fixtures, configuration defaults, and temporary request payloads are allowed.

Use the last three completed, recorded iterations for the planning average, including genuine zero-completion periods. With fewer periods, show sample size; with no history, say unknown and use a small scope chosen by the solo owner or team. Exclude the current partial iteration. Velocity forecasts delivery for the solo developer with agents or the team; it is never a productivity target, individual ranking, or estimate derived from agent count.

## 5. Workflow commands

These are logical command names, not a claim that every host registers slash commands. Prefer one Python stdlib dispatcher `scripts/xp.py` with shared helpers; invoke as `python3 <skill-path>/scripts/xp.py <command>`. Thin wrappers are optional only if useful. Dependencies: Python 3, `gh`, and `git`. All GitHub calls made by these helpers go through `gh`; local branching legitimately uses `git`. This does not constrain the existing workflow's tools, such as an MCP merge operation.

| Command | Required behavior |
|---|---|
| `xp-setup <owner> [repos…]` | Inspect first. Create/verify selected Project, fields, types or labels, views, templates, and the minimal history location. Preserve unrelated settings. Show manual gaps explicitly. Propose template changes only where needed; preserve existing formats and use the repository's branch/PR workflow for approved changes. |
| `xp-story` | Shape a customer outcome and testable examples; create an estimated or explicitly unestimated Story in Backlog. Offer `--kind spike` for a time-boxed investigation without Points. Respect existing issue formats and reference authoritative specifications without duplication. CLI creation must render the body explicitly; it does not automatically apply an issue form. |
| `xp-split <story>` | Propose small verifiable Tasks with dependencies only where needed; after scope approval create/reuse native sub-issues and add to Project. Do not require arbitrary task counts or horizontal layers. A small Story may be implemented directly without creating a token Task. |
| `xp-plan [iteration]` | Show ranked Stories, Points/unknowns, blockers, recent velocity and availability assumptions; propose a cut line. Preserve order. After scope approval record the plan and assign Stories and open Tasks. No silent priority sorting if API order differs from Backlog view order. |
| `xp-start <task-or-small-story>` | Check scope, blockers, and parent when present; respect existing assignees. Support human implementation or a bounded sub-agent handoff. Produce the work brief and let the existing workflow create/reuse its branch/worktree; reconcile In Progress after work starts. A standalone branch helper is a fallback only when no workflow owns this step. Preserve dirty work and refuse destructive resets. Guide test-first work and frequent integration without replacing local engineering gates. |
| `xp-finish <task-or-small-story>` | Consume the existing workflow's diff, test/review/demo evidence, and PR result. Add or verify Task-closing and parent-reference links without bypassing its pre-PR gates or opening a duplicate PR. If no workflow owns PR creation, offer a standalone helper after required gates pass. For a directly implemented Story, reference it without a closing keyword and leave closure to `xp-accept`. Do not close Story, merge, or mark acceptance merely because a PR exists; leave merge and cleanup to the existing workflow and its authorization. Reconcile completion only after that workflow reports and GitHub confirms completion. Non-code Tasks need explicit completion evidence. |
| `xp-accept <story>` | Re-read Tasks, criteria, evidence, and acceptance decision. Resolve inline or referenced criteria and reject missing/empty criteria or unsupported claims. Reuse an existing valid acceptance decision and evidence; do not add a second human gate. Record the product decision time separately from completion/credit time; a pre-merge acceptance decision earns no velocity until required integration is complete. Record credit and close as completed only when all gates pass. Report unmet conditions. A tiny Story may have no Tasks if explicitly intended. |
| `xp-close-iteration` | Report planned/added/removed/accepted/carried scope and a brief reflection. Persist the report before rollover; after scope approval move unfinished work to the next explicit iteration without changing Points. Resume partial failures without advancing twice. |
| `xp-velocity [n]` | Read authoritative GitHub history; print the last n completed periods (default 6), totals, sample size, and missing-history warnings. No manufactured zeros or silent truncation. |
| `xp-release <milestone>` | Require explicit repository, tag, and target commit. Verify no open milestone issues and required Stories accepted; reconcile cancellations. Close milestone and create/reuse a draft Release with Story-centered notes and links. No automatic publication or deployment. |

Honor existing explicit authorization. Before creating multiple issues or changing Iteration assignments in bulk, show the concrete affected objects and obtain approval if that exact scope is not already approved. Proposal/read modes never mutate. Do not require repeated permission for the same reviewed plan. Setup, merge, publication, and organization-wide configuration have distinct scopes; skill activation alone authorizes none of them.

## 6. Reliability and capability rules

- Every command supports `--dry-run`: queries may run, but no GitHub mutation, local branch/file change, push, or auth refresh occurs. Print ordered calls and sanitized variables; label unresolved IDs symbolically. Offline fixtures must permit dry-run testing without credentials.
- Commands must be safe to rerun. Use stable operation identifiers recorded on GitHub and exact resource identity, not duplicate-title heuristics. `clientMutationId` is not a server-side deduplication guarantee. After a timeout, reconcile before retrying a create.
- GitHub operations are not atomic transactions. Report completed steps and remaining work; resume from GitHub state. Detect conflicting concurrent changes and stop for a fresh plan rather than overwrite them. Document that marker-based deduplication does not guarantee exactly-once creation across concurrent clients.
- Paginate all relevant connections, including nested Tasks, fields, comments, and iteration history. Account for archived/redacted items and inaccessible repositories. Never report partial data as complete.
- Check HTTP failures and GraphQL `errors` even on HTTP 200. Distinguish auth/permissions, unavailable capabilities, rate limits, and validation errors. Bound retries and honor rate-limit delays.
- Pass GraphQL variables/JSON as structured data and subprocess argument arrays; do not evaluate user text in a shell or embed it into queries. Do not print credentials.
- At build time, date a capability matrix with official sources and observed probes. At runtime, discover capabilities without mutation. Separate documented, schema-observed, and live-tested support.
- Verify API support for Iteration creation/configuration, saved views and ordering, issue types, sub-issues, dependencies, workflows, and Insights. Use supported APIs when available; otherwise document exact UI steps. A documented mutation does not establish the caller's permission or the target GHES version's support.
- Built-in closed→Done automation is bookkeeping, not evidence of acceptance. Do not enable a Done→close workflow that bypasses Story acceptance. Do not auto-archive until history remains readable and reports have been verified.
- Native charts are part of the workspace scope: configure and verify supported useful measures. Do not label a chart as accepted-story velocity unless it matches that measure. Use a clearly labeled GitHub-hosted report for unsupported historical calculations; an ASCII report alone does not satisfy the native-workspace deliverable.
- Prefer explicit `xp-accept` for v1. Do not add automatic parent closure merely because all Tasks close. An optional Action requires a proven acceptance-safe rule, bounded permissions, cross-repository access analysis, and specific approval.

## 7. Packaging and lean constraints

Use standard YAML frontmatter with matching lowercase `name` and a concise, discriminating `description`; keep optional standard fields valid. Avoid host-specific tool names, `allowed-tools` permissions, dynamic shell substitutions, mandatory host-specific sub-agent tools, or model/CLI dependencies in the shared skill. Use paths relative to the installed skill and pass the target repository separately; never assume the working directory is the skill directory.

Keep `SKILL.md` at most 200 lines. Put nontrivial mechanics in linked `references/` and installable templates in `assets/`. The skill must work when copied alone, without reaching outside its directory to repository documentation or source checkouts. Root docs serve maintainers, not runtime dependencies.

Target about 600 runtime Python lines, excluding fixtures/tests/templates. Correctness and readable recovery paths take precedence over code golf; explain material overruns. Do not force a framework or ten duplicate scripts to satisfy a file layout. Keep field/type/default names in one module. No LLM calls from scripts; the agent handles decomposition and judgment.

Document current installation/discovery and explicit invocation for all four hosts from their official documentation. A shared format is not proof of tested discovery or execution. Keep one canonical skill source; document per-host copy/install paths without overwriting existing installations.

## 8. Deliverables and staged execution

Expected eventual layout:

```text
github-xp/
  README.md  LICENSE  NOTICE.md  CONTRIBUTING.md  AGENTS.md  .gitignore
  xp-github-prompt.md
  docs/                     SURVEY.md  RESEARCH.md  DESIGN.md  INTEGRATION.md  VERIFY.md
  skills/github-xp/
    SKILL.md
    references/             xp.md  agents.md  integration.md  github.md  history.md  setup.md
    scripts/                xp.py  github.py
    assets/                 ISSUE_TEMPLATE/{story,task,spike}.yml
                            pull_request_template.md
  tests/                    fixtures/ and behavior tests
  .github/workflows/        ci.yml (validation, not live GitHub mutations)
  research/                 README.md (supplied assets stay local)
  _sources/                 ignored pinned research checkouts
```

1. **Survey and revise.** Inspect sources and local research; improve this prompt; write research, survey, design, and honest verification status. Initialize local Git and set the requested remote if needed. Do not overwrite existing history or push research assets.
2. **Review checkpoint.** Present the revised prompt, SURVEY, and DESIGN. Stop before writing the final skill or runtime code unless the user explicitly approves or waives this checkpoint. This is the requested opportunity to settle the contract before the one-shot build.
3. **Build.** After approval, produce the complete skill, helpers, references, assets, and tests as one coherent implementation. One shot means prepare carefully and deliver a complete build, not skip validation or conceal failures. Do not silently reduce scope or declare untested automation complete.
4. **Verify.** Validate frontmatter, relative links, installation isolation, and script behavior. Run Python lint and all offline scenarios below. Use only user-authorized spike/sandbox targets. The user has now explicitly authorized creating an XP-like dataset and demonstration Project in `jmf-pobox/github-xp`; this permits the isolated native-workspace spike before the final skill build. It does not authorize changing langlearn-anki or creating unrelated test environments.

Required behavioral scenarios: existing agentic PR loop reused without duplicate agents/branches/PRs; local-spec-linked acceptance without specification duplication; existing valid operator demo reused without a new approval; changed evidence revision requiring re-verification; in-scope review finding fixed without another issue; authorized automatic merge left to the host workflow; adoption conflict reported without rewriting local policy; solo owner acting as product manager with delegated engineering; solo owner participating in implementation; human takeover from an agent; team roles and existing approval rules; host without sub-agents; independent Task delegation and overlapping-write refusal; stale review after integration changes; bounded review-loop failure; small Story implemented without Tasks and accepted explicitly; shared credentials without fabricated independent approval; organization and personal owners; no history and zero-velocity periods; more than one page of results; missing Points; archived/inaccessible items; cross-repository Tasks and closing references; non-`main` default branch; dirty working tree; open blockers; duplicate run and failure between create/link/Project-add; concurrent edit; empty/unchecked criteria; cancelled Task; customer decision absent; PR targeting a nondefault branch; completed versus not-planned Story; carryover followed by acceptance; reopened Story and correction without duplicate credit; no next iteration; release retry after partial failure; malicious quoting in a title/body; dry-run proving zero mutations.

Document observed results and limitations in `docs/VERIFY.md`. Track format validation, host discovery, host execution, and live GitHub end-to-end tests separately. Never invent results or claim an API feature is UI-only merely because credentials were unavailable.
