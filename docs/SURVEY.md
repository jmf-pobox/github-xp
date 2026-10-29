# Source survey

Inspected 2026-10-28. All four requested repositories resolved without URL correction and were shallow-cloned under ignored `_sources/`. Line references below refer to the pinned commits, not moving default branches. “Reuse” means a design candidate, not code already incorporated.

## A. github/awesome-copilot

- Source: https://github.com/github/awesome-copilot
- Commit: `7c3417cf9446ababff13d2d4956ce923e8c140a8`
- Root license: MIT, copyright GitHub, Inc. No code copied.
- [Projects reference](https://github.com/github/awesome-copilot/blob/7c3417cf9446ababff13d2d4956ce923e8c140a8/skills/github-issues/references/projects.md), lines 27–82: ID discovery and exact-match pitfalls. Lines 85–107: paginate before reporting. Retain those concepts, but do not copy examples with fixed first-page limits into production code.
- [Sub-issues reference](https://github.com/github/awesome-copilot/blob/7c3417cf9446ababff13d2d4956ce923e8c140a8/skills/github-issues/references/sub-issues.md), lines 5–24 and 34–64: create then link, numeric issue ID versus issue number. Useful for recovery design.
- [Issue types](https://github.com/github/awesome-copilot/blob/7c3417cf9446ababff13d2d4956ce923e8c140a8/skills/github-issues/references/issue-types.md), lines 11–68; [dependencies](https://github.com/github/awesome-copilot/blob/7c3417cf9446ababff13d2d4956ce923e8c140a8/skills/github-issues/references/dependencies.md), lines 5–65: useful API recipes, subject to official-schema validation.
- Reject required MCP tool names and generic triage. Do not infer token scopes for every authentication type from an OAuth example. This source does not supply the full XP workflow, historical velocity, or customer-acceptance rule.

## B. bodangren/git-workflow

- Source: https://github.com/bodangren/git-workflow
- Commit: `7ad2d44082c36d3e29144378098b83f570566afa`
- Root license: MIT, copyright 2025 Daniel Bo. No code copied.
- [Sprint planner](https://github.com/bodangren/git-workflow/blob/7ad2d44082c36d3e29144378098b83f570566afa/skills/sprint-planner/SKILL.md), lines 31–71: discuss scope, decompose, verify created issues. Preserve the conversational shape; propose and approve the actual tasks before creation.
- [Issue executor](https://github.com/bodangren/git-workflow/blob/7ad2d44082c36d3e29144378098b83f570566afa/skills/issue-executor/SKILL.md), lines 30–48 and 64–88: context, isolated branch, atomic work. Retain these principles without requiring main checkout, Gemini, or a pre-existing spec tree.
- [Sprint manager](https://github.com/bodangren/git-workflow/blob/7ad2d44082c36d3e29144378098b83f570566afa/skills/sprint-manager/SKILL.md), lines 20–64: milestone-driven, Gemini/Codex-MCP/subagent orchestration conflicts with the target. Do not reuse the orchestration.
- Reject “sprint milestone,” priority labels, autonomous merges, and a mandatory specification hierarchy. Project Iteration is scheduling; milestone is release scope.

## C. 8-bit-sheep/code-harness-skills

- Source: https://github.com/8-bit-sheep/code-harness-skills
- Commit: `ecda7fbbd43a37f58f69cc4a47574834d2549260`
- Root license: MIT, copyright 2026 Sunholo LLMOps. No code copied.
- [Velocity script](https://github.com/8-bit-sheep/code-harness-skills/blob/ecda7fbbd43a37f58f69cc4a47574834d2549260/skills/sprint-planner/scripts/analyze_velocity.sh), lines 17–44: extracts LOC/changelog/commit observations and asks the reader to infer pace. It does **not** implement completed-story velocity. Reject the calculation entirely.
- [Planner](https://github.com/8-bit-sheep/code-harness-skills/blob/ecda7fbbd43a37f58f69cc4a47574834d2549260/skills/sprint-planner/SKILL.md), lines 128–162: useful capacity discussion, dependencies, explicit assumptions, and feedback. Retain ideas only; remove LOC estimates and prescribed day-by-day planning.
- [Executor](https://github.com/8-bit-sheep/code-harness-skills/blob/ecda7fbbd43a37f58f69cc4a47574834d2549260/skills/sprint-executor/SKILL.md), lines 74–97 and 160–205: local sprint state and agent orchestration conflict with GitHub-only operational state and host portability.
- Do not copy its frontmatter name (`Sprint Planner`); portable names must match a lowercase hyphenated folder name.

## D. andybaran/skill-gitflow

- Source: https://github.com/andybaran/skill-gitflow
- Commit: `65b7764f7b1e6bec91edb4814e17254dc1327219`
- Root license: MIT, copyright 2026 andybaran. No code copied.
- [Skill](https://github.com/andybaran/skill-gitflow/blob/65b7764f7b1e6bec91edb4814e17254dc1327219/skills/issue-driven-github-flow/SKILL.md), lines 128–147: issue traceability and literal-safe body handling; lines 216–259: branch/PR lifecycle; lines 314–327: evidence-backed checkbox changes. Preserve the intent, not its compulsory orchestrator.
- [Projects reference](https://github.com/andybaran/skill-gitflow/blob/65b7764f7b1e6bec91edb4814e17254dc1327219/skills/issue-driven-github-flow/references/projects.md), lines 27–91: field/option/item ID resolution is useful after API verification.
- Reject mandatory agent loops (149–207, 261–312), the >3-issues Project threshold (400–413), host-specific permission/frontmatter structures (16–25), and unconditional Copilot attribution in helper usage (233–234).
- Adapt the default-branch safety concept to the actual repository default branch, not a universal `main`. Favor small branches and frequent integration over heavyweight review bureaucracy.

## Reuse and license conclusion

All four inspected root licenses are MIT. That supports considering reuse under an MIT project, provided required notices and any file-specific terms are retained. It is not blanket permission for every embedded image or third-party asset. The current deliverables use original prose and source links, with no copied implementation. The eventual builder should favor small fresh deterministic helpers over transplanting incompatible orchestration.

The XPlanner research is evaluated separately in [RESEARCH.md](RESEARCH.md). Its historical software license does not license the supplied article or screenshots for redistribution.
