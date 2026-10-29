# GitHub XP

Practice Extreme Programming through native GitHub Issues and Projects, primarily as a solo developer working with agents, with the same model supporting teams.

One portable skill supplies XP planning, GitHub workspace setup, iteration management, acceptance and delivery reporting. It hands bounded work to your existing coding/review/merge workflow. GitHub provides the XPlanner-like interface: Stories, native child Tasks, iterations, milestones, saved views, progress and charts. No separate web application or local planning database.

**Status: initial implementation, with offline tests, live GitHub checks and read-only client smoke tests.** See [verification and limits](docs/VERIFY.md). The helpers target GitHub.com and use Python 3.10+, GitHub CLI and Git. No Python packages are required at runtime.

## Install

Copy the entire [`skills/github-xp`](skills/github-xp) directory into one appropriate project-local discovery directory, preserving its name:

| Client | Destination inside your target repository | Invocation |
|---|---|---|
| Codex | `.agents/skills/github-xp/` | `$github-xp` or a matching XP planning request |
| Claude Code | `.claude/skills/github-xp/` | `/github-xp` or a matching request |
| OpenCode | `.agents/skills/github-xp/` | Ask to use the `github-xp` skill |
| Pi | `.agents/skills/github-xp/` | `/skill:github-xp`, or explicit `--skill /path/to/github-xp` |

Check for an existing installation before copying; do not overwrite local customization silently. See [setup and official client sources](skills/github-xp/references/setup.md) for discovery details. There is one canonical source, not four divergent implementations. Installation does not authorize changing a repository's workflow or GitHub configuration.

## Use

Start with: “Use github-xp to inspect this repository's workflow and propose an XP workspace in my existing GitHub Project.” Then try:

- “Shape this outcome into a small Story with examples.”
- “Plan next week's iteration; I have two hours for decisions and demonstrations.”
- “Hand this Task to our existing engineering agents.”
- “Reconcile this Story with the operator demo and merged PR.”
- “Close the iteration, carry unfinished work, and explain accepted velocity.”

The skill loads only the relevant workflow references. The human may act as product manager, engineer, or both. No second human, organization account or artificial agent identity is required. Owner acceptance can reuse valid evidence from your current workflow; green CI and completed Tasks alone do not count as product acceptance.

Helpers preview by default. Run `python3 /path/to/github-xp/scripts/xp.py --help`, then consult the [exact JSON contract](skills/github-xp/references/github.md). They accept structured reviewed inputs, not raw natural-language commands. Judgment and evidence inspection stay with the agent; deterministic reads, validation and writes stay in the helpers. Stable operation IDs and GitHub history support recovery after partial writes.

## Explore the working example

[Open Iteration Planning](https://github.com/users/jmf-pobox/projects/3/views/2) or read the [spike tour](docs/SPIKE.md). The Project is private to its owner; the repository's synthetic sample issues are public. The fixture demonstrates planning and acceptance boundaries, not delivered vocabulary software.

## Develop and verify

```sh
python3 -m unittest discover -s tests -v
ruff check skills/github-xp/scripts tests
python3 tests/validate_package.py
```

The package validator needs PyYAML as a development dependency; CI installs pinned lint/YAML tooling. Tests use fake GitHub responses and never mutate GitHub. See [behavior review](docs/BEHAVIOR-REVIEW.md) for independent workflow walkthroughs and [verification](docs/VERIFY.md) for the exact limits of live and cross-client checks.

Design rationale and provenance: [build prompt](xp-github-prompt.md), [source survey](docs/SURVEY.md), [XPlanner research](docs/RESEARCH.md), [design](docs/DESIGN.md), and [integration case study](docs/INTEGRATION.md).

Original code is MIT licensed. Third-party research is excluded from that license and from Git by default; see [NOTICE.md](NOTICE.md). Supplied research assets are not distributed with the skill.
