# GitHub XP

Practice Extreme Programming through native GitHub Issues and Projects, primarily as a solo developer working with agents, with the same model supporting teams.

One portable skill supplies XP planning, GitHub workspace setup, iteration management, acceptance and delivery reporting. It hands bounded work to your existing coding/review/merge workflow. GitHub provides the XPlanner-like interface: Stories, native child Tasks, iterations, milestones, saved views, progress and charts. No separate web application or local planning database.

**Status: initial implementation, with offline tests, live GitHub checks and read-only client smoke tests.** See [verification and limits](docs/VERIFY.md). The helpers target GitHub.com and use Python 3.10+, GitHub CLI and Git. No Python packages are required at runtime.

## Install

Run this in a normal terminal from the repository where you want to use the skill:

```sh
npx skills@1.7.4 add jmf-pobox/github-xp --skill github-xp
```

The shared installer lets you select your coding harnesses and choose installation options. Add `-g` for user-wide installation. The tested installer version requires Node.js 22.20+; Node is an installation dependency, not a skill runtime dependency. Codex, OpenCode and Pi share the project `.agents/skills` location; Claude Code can use a symlink from `.claude/skills`. The picker may group shared targets rather than show independent checkboxes.

To select our four supported harnesses explicitly:

```sh
npx skills@1.7.4 add jmf-pobox/github-xp --skill github-xp -a codex -a claude-code -a opencode -a pi
```

When run inside an agent, the installer may automatically skip prompts. Review the destination and existing installations first. Use `--copy` if symlinks are unsuitable. Reinstallation can replace the entire installed skill, including local customizations; keep project-specific policies in your repository workflow instead of editing installed files.

Update or remove a project installation:

```sh
npx skills@1.7.4 update github-xp -p
npx skills@1.7.4 remove github-xp
```

Removal above targets this skill across all harnesses, including the shared canonical directory; unrelated skills remain installed. Removing only selected harnesses can leave the shared copy available.

For user-wide installations, use `-g` instead of `-p` for update and add `-g` to removal. The npm version above pins the installer, not the skill's source revision. For a reproducible source version, use an explicit Git ref through a supported installer route.

If your installed GitHub CLI provides `gh skill`, it offers an alternative without Node:

```sh
gh skill install jmf-pobox/github-xp github-xp --agent claude-code --scope project
```

Use `--pin <tag-or-commit>` to pin the skill source. Avoid mixing installers for the same destination. See [installation tests and limitations](docs/INSTALLATION.md) for observed behavior and [installer research](docs/INSTALLER-RESEARCH.md) for the selection rationale.

Manual fallback: copy the entire [`skills/github-xp`](skills/github-xp) directory, including its bundled license, into a discovery directory:

| Client | Project-local destination | Invocation |
|---|---|---|
| Codex | `.agents/skills/github-xp/` | `$github-xp` |
| Claude Code | `.claude/skills/github-xp/` | `/github-xp` |
| OpenCode | `.agents/skills/github-xp/` | Ask to use `github-xp` |
| Pi | `.agents/skills/github-xp/` | `/skill:github-xp` |

Start a fresh session after installation. [Setup](skills/github-xp/references/setup.md) covers user-level paths and official client sources. Installation supplies one canonical portable skill; it does not change your engineering workflow or configure a GitHub Project automatically.

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
