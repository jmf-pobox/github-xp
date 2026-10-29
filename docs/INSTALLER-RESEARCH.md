# Multi-harness installer research

Research date: 2026-10-29 UTC. Scope: inspect existing installer designs and test discovery without installing into the user's harness directories.

## Recommendation

Use the existing **Vercel skills CLI** as the primary interactive installer, matching Herdr's published skill-install route. Offer the existing **GitHub CLI skill installer** as an alternative for users who already have a sufficiently recent `gh`. Keep manual folder copying as a fallback. Do not build a custom installer or require separate plugin packages merely to distribute this one skill.

Our current `skills/github-xp/SKILL.md` layout is already discoverable by both tools. Runtime remains Python stdlib + gh + Git; using npx adds a Node requirement only for that installation route.

## Compared options

| Option | Observed design | Fit |
|---|---|---|
| [Herdr skill installation](https://herdr.dev/docs/agent-skill/) | Recommends `npx skills add herdrdev/herdr --skill herdr -g`; project scope when `-g` is omitted | Direct precedent for using a shared installer rather than implementing one |
| [Vercel skills](https://github.com/vercel-labs/skills) | Agent detection, interactive searchable multi-selection, project/global scope, canonical storage with symlink or copy, update/check/remove commands | Best match for the requested checkbox UX; all four target harnesses mapped in source |
| [GitHub CLI](https://cli.github.com/manual/gh_skill_install) | Interactive selection, explicit agent/scope, duplicate-destination handling, tagged release/commit pinning and source tracking for updates | Particularly attractive because gh is already a runtime dependency; check installed version for command availability |
| [Skillshare](https://skillshare.runkids.cc/docs/reference/commands/init/) | Detects target CLIs, imports existing skills, configures a source repository and synchronizes targets; asks questions before a final summary | Useful for users managing a whole skill collection; broader than installing github-xp alone |
| [OpenSkills](https://github.com/numman-ali/openskills) | Install/read/update flow plus `sync` to expose skills through AGENTS.md; universal mode uses `.agent/skills` | Useful compatibility layer for agents without native skill discovery; unnecessary extra instruction integration for our four targets |
| [Clack](https://bomb.sh/docs/clack/packages/prompts/) | TypeScript prompt toolkit with selection, multi-selection, cancellation and progress components | UI building block if custom installation is later justified; it does not supply harness paths or update logic |
| [Questionary](https://questionary.readthedocs.io/en/stable/) | Python interactive prompt library | Python alternative for a custom wizard; still requires us to implement installation lifecycle and adds a dependency |

## Source observations

Inspected `vercel-labs/skills` at commit `92a9a34ac3bf88e695e468b90c7bf32f163d32c8`, declaring version 1.7.4 and MIT license:

- `package.json` declares Node >=22.20.0 and `@clack/prompts`; the agent picker uses its own searchable multi-select implementation.
- `src/agents.ts` explicitly maps `codex`, `claude-code`, `opencode`, and `pi`.
- `src/add.ts` uses an interactive agent selector and remembers prior choices. Agents sharing `.agents/skills` may appear in a locked universal group, so four independent checkboxes should not be promised.
- `src/add.ts` detects execution inside an AI agent and enables non-interactive mode; our discovery test visibly detected Codex. In automation, pass explicit agent flags rather than assume a human picker appears.
- `src/installer.ts` recursively copies the skill directory, retaining bundled references, scripts and assets. The root repository LICENSE is outside that directory: include a license inside the distributed skill before treating installation packaging as complete.
- [`docs/commands.md`](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) documents `add`, `check`, `update`, and `remove`, along with copy/symlink modes. Updates are not a merge strategy for local customization. Use a tested version/ref and verify overwrite behavior in an isolated install lifecycle test.

## Commands and checks

For a human in a normal terminal, the proposed default is:

```sh
npx skills add jmf-pobox/github-xp --skill github-xp
```

Add `-g` for user-wide installation. An explicit multi-harness route is:

```sh
npx skills add jmf-pobox/github-xp --skill github-xp -a codex -a claude-code -a opencode -a pi
```

A gh alternative, on versions that provide `gh skill`, is:

```sh
gh skill install jmf-pobox/github-xp github-xp --agent claude-code --scope project
```

These installation commands are recommendations from documented/source-inspected interfaces, not claims of installation tests performed here.

Actual read-only discovery checks:

- `skills@1.7.4 add jmf-pobox/github-xp --list` found exactly one skill, `github-xp`, and displayed its description. Ran with a temporary npm cache and telemetry disabled. No harness installation was requested.
- Installed `gh` 2.101.0 exposes `gh skill install`; its help lists all four target agents. Non-interactive `gh skill install jmf-pobox/github-xp` listed `github-xp` at source commit `23737871`, without a skill argument or `--all`, which is the documented list-only mode.
- Node available locally: 26.9.0. No runtime/tool upgrades were performed.

Before making either route the documented default: bundle the license, exercise project installation in a temporary directory, verify all support files and links, test update/reinstall/removal and existing-install collisions, then update README with exact commands and observed results. A custom wrapper is warranted only if those tests reveal a concrete missing behavior.

## Implementation follow-up

The license is now bundled and the lifecycle tests are implemented in `tests/installer_smoke.py`. The README uses the pinned, tested installer interface. See [INSTALLATION.md](INSTALLATION.md) for results, including differences between upstream main documentation and the published npm package. No custom installer or plugin wrapper was needed.
