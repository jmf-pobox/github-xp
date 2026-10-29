# Verification status

Date: 2026-10-28 Pacific / 2026-10-29 UTC. The user approved the design checkpoint and the initial skill implementation is present in `skills/github-xp/`.

## Results

| Layer | Observed result |
|---|---|
| Source/research | Original prompt and supplied research inspected; four upstream repositories pinned and licenses recorded in SURVEY |
| Skill format | Bundled skill-creator validator passed; optional compatibility metadata moved into prose for its older accepted-field set |
| Package | Metadata, issue-form YAML, internal links, isolation and <=200-line entrypoint checks passed |
| Python | Ruff passed; 57 offline behavioral tests passed on local Python 3.13 |
| Live read | Installed `xp.py setup` inspected Project #3, 15 fields and eight views with zero writes and no scope warnings |
| Live writes/retry | Installed setup created history issue #16; story helper created synthetic Spike #17 and one Project item; identical repeat preview returned #17 with zero actions |
| Native workspace | Original spike verified fields, iterations, views, hierarchy, dependencies, native auto-add, closed→Done, acceptance boundary and rollover |
| UI follow-up | Planning grouping and post-rollover sums verified: current 2, next 8, backlog 3. Chart filter and roadmap mapping remain unverified because Safari repeatedly became unavailable |
| Independent review | Six instruction walkthroughs and independent runtime tests; defects found were fixed and regression-tested |
| CI | Offline-only workflow added for Python 3.10 and 3.13. Local checks passed; current remote results are available in GitHub Actions |
| Publication | Initial source publication on `main` authorized by the user. No release publication or installation into the user's real projects was performed |

[Live helper evidence](spike/helper-verification.json) identifies the created objects. Spike #17 was closed after its investigation passed, with a comment documenting the result and no Points or acceptance credit. History issue #16 is outside delivery scope. The original 15-item fixture remains described in [SPIKE.md](SPIKE.md); the helper test adds one Project item and one non-Project history issue.

## Client discovery and read-only execution

Used isolated copies under `/tmp/github-xp-host-check`, preserving the user's real project installations and workflows. Installed client defaults were used; no model selection/configuration was changed.

| Client | Observed check | Limit |
|---|---|---|
| Codex | Discovered `.agents/skills/github-xp`; `$github-xp` loaded the skill and read execution/acceptance references; correctly withheld credit before merge and reused existing demo/workflow | Read-only scenario, not full GitHub command execution |
| Claude Code | `/github-xp` used the `.claude/skills/github-xp` copy; answered the pre-merge acceptance case correctly and reported reading acceptance/history | Read-only tools; text output reports references, not a complete tool trace. Reported an auto-surfaced AGENTS reference not supplied by this package; not counted as package evidence |
| OpenCode | Trace showed Skill `github-xp` and selective reference reads from `.agents/skills/github-xp`; correctly withheld credit and preserved workflow ownership | Plan-mode scenario; not a live mutation test |
| Pi | Explicit `--skill` loaded the portable package; read planning/history and treated velocity as unknown, with scope constrained by owner availability | Explicit-path loading verified; automatic `.agents` discovery was documented, not separately exercised |

Codex/OpenCode needed access to their normal local runtime files outside the workspace sandbox. Claude emitted a configured-model retirement warning but the corrected CLI invocation completed. These environment observations are not skill portability failures or proof that every client version works.

The client answers are also evidence for testing, not authority: one answer simplified credit time to merge time. The actual rule is when **all required acceptance and integration conditions hold**, which may be later than merge. Tests enforce decision/completion chronology and prohibit credit before required PR merges.

## Behavioral coverage

Offline tests cover partial creation/plan/acceptance/rollover recovery; stable operation identity; missing Points; incomplete versus zero history; completed/cancelled/reopened work; explicit acceptance authority; stale decision/review/PR evidence; non-main default branches; completed Task history preservation; unknown next iteration; unsafe auto-close workflows; release retry; cross-repository marker collisions; history metadata tampering; revoked credit and explicit report restatement; pagination; subprocess quoting; HTTP-successful GraphQL errors; mutation timeouts; per-action field conflict checks; and fixture dry-run with zero subprocess/filesystem mutations; an isolated copied-package CLI run that creates no bytecode or other files; and intentional empty-scope planning.

[Independent walkthroughs](BEHAVIOR-REVIEW.md) cover reuse of the existing engineering loop/demo, solo ownership without subagents, human takeover with dirty work, conflicting adoption policy, in-scope findings and concurrent writers. They are instruction reviews, not executed implementations of those projects.

## Practical limits

- Helpers operate on GitHub.com. Organization issue types have a configured read-probe path and offline coverage where applicable, but no organization or GHES end-to-end test was performed.
- The agent must inspect real criteria, tests, review revisions and customer decisions. JSON assertions record reviewed facts; the helper does not adjudicate arbitrary documents or prove their truth.
- Setup is staged and reports UI steps. Field sums, grouping, manual rank, workflow settings and native Insights are not automatically configured by the Python dispatcher. Existing Project iteration calendars are preserved rather than rewritten.
- Requests are serialized by the coordinator. Global preflight and per-action reads detect many concurrent edits; they cannot create an atomic GitHub transaction or guarantee exactly-once creation across concurrent clients.
- Historical comments can be edited/deleted. Malformed/duplicate records fail closed, but a deleted record with no remaining trace cannot be proven absent. Removed iteration definitions cannot be reconstructed reliably; retain calendar/history and investigate gaps.
- Original commitment, acceptance and close history are required for authoritative reporting. The synthetic historical fixture has no real delivery credit. Native scope charts are not accepted velocity.
- Live helper tests covered inspection, setup/history creation, issue creation, membership and retry. Acceptance, release, fault injection and large pagination behavior were tested offline; they were not all exercised as live writes.

The runtime totals roughly 900 lines across two modules, exceeding the prompt's approximate 600-line target. Complete pagination, preflight/per-action guards, recoverable history, explicit corrections and readable command validation account for the overrun. The entrypoint remains small, and Python runtime dependencies remain stdlib-only.
