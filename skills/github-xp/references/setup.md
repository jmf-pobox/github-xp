# Install and configure

## Install through the shared CLI

From a normal terminal in the target repository, run:

```sh
npx skills@1.7.4 add jmf-pobox/github-xp --skill github-xp
```

Choose the harness targets and install method. Add `-g` for user-wide scope; default is project scope. Node 22.20+ is required by this installer, but not by the Python skill helpers. One canonical folder serves Codex, OpenCode and Pi; Claude Code normally receives a symlink. `--copy` requests copies. Shared targets may be grouped in the picker.

Inside an agent, the installer may choose non-interactive mode automatically. Inspect existing destinations before running it; specify `-a codex -a claude-code -a opencode -a pi` when those are the intended targets. Do not assume activation authorizes overwriting another skill of the same name. Reinstall replaces installed content; keep local policies in repository instructions, not in the installed skill.

Update a remote project installation with `npx skills@1.7.4 update github-xp -p`; use `-g` for user-wide updates. Local-source installs are refreshed by repeating `add` against the source path. Remove this skill from the selected scope with `npx skills@1.7.4 remove github-xp` (add `-g` for user-wide removal). Omitting agent filters removes its shared canonical directory and harness links; filtering to individual agents can retain the shared directory. Unrelated skill names are preserved. Avoid `--all`, which selects every skill.

The installed GitHub CLI may also provide the preview `gh skill install` command. For example: `gh skill install jmf-pobox/github-xp github-xp --agent claude-code --scope project`. `--pin <tag-or-commit>` pins source content. Do not mix installers at one destination. The npm version pins the installer, not the skill source.

Sources: [skills CLI](https://github.com/vercel-labs/skills/blob/main/docs/commands.md), [GitHub CLI](https://cli.github.com/manual/gh_skill_install). Instructions above use the tested `skills@1.7.4` interface; newer documentation can describe unreleased behavior.

## Install the portable folder

Copy the complete `github-xp` directory, including references, scripts and assets, to one chosen host discovery location. Check for an existing installation before copying; do not overwrite it or create duplicate same-named installations silently. Keep the source canonical and update installed copies deliberately.

| Host | Project location | User location | Explicit request |
|---|---|---|---|
| Codex | `.agents/skills/github-xp/` | `~/.agents/skills/github-xp/` | `$github-xp` followed by the task |
| Claude Code | `.claude/skills/github-xp/` | `~/.claude/skills/github-xp/` | `/github-xp` followed by the task |
| OpenCode | `.agents/skills/github-xp/` | `~/.agents/skills/github-xp/` | Ask “Use the github-xp skill to …”; the agent loads it with its skill tool |
| Pi | `.agents/skills/github-xp/` | `~/.agents/skills/github-xp/` | `/skill:github-xp` followed by the task |

These are documented local discovery paths, not a claim of execution on every host/version. Start a fresh session after installation; in Pi `/reload` reloads resources. Confirm the skill appears, then ask for a read-only plan and inspect which references were loaded. Shared format does not make sub-agent tools or permissions identical.

Sources checked 2026-10-29: [Codex](https://developers.openai.com/codex/skills/), [Claude Code](https://code.claude.com/docs/en/skills), [OpenCode](https://opencode.ai/docs/skills/), [Pi](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md). No host-specific frontmatter or orchestrator is required.

## Inspect before adoption

Verify Python 3, Git and authenticated `gh` availability without changing credentials. On auth failure, report whether environment token selection might override an existing login; do not print tokens, remove a user's configuration or refresh permissions automatically.

Read [integration](integration.md). Identify actual owner kind, repositories/default branches, explicit Project number, existing taxonomy, fields and status options, views, built-in workflows, permissions and the planning-log issue. Probe with reads. A 401/403 is not proof that a feature is unsupported; distinguish authorization, validation, rate limit and host/version limitations.

Use existing fields and semantic equivalents where unambiguous. Resolve duplicate names with IDs. Personal repositories use labels; organizations can use native issue types after capability discovery. Preserve an organization's existing taxonomy. If using labels, ensure `type:story`, `type:task`, `type:spike` and an agreed attention label exist before creating issues/forms that reference them.

Show a concrete setup plan and its adopted responsibility map. Create a Project/history issue only when that scope is authorized. The helpers currently calculate iteration boundaries and credit in UTC. Make that policy explicit; do not claim support for a different calendar without an adaptation. Seven-day iterations are the recommended default, with an explicit start. Keep release milestones separate. Template adoption goes through the existing branch/PR workflow, preserving existing forms; bundled assets are optional starting points.

## Staged helper setup

With no `context.project`, `setup` creates or finds a Project whose title includes the stable operation marker, then returns its number. Put that number in `context.project` and rerun; this stage does not create fields or views. Inspect the selected Project first. To configure it, supply `configure: true` and explicit iteration definitions if the Iteration field is missing.

Configuration creates missing fields/classification labels and can create or find a marked planning-log issue in the first selected repository. Review that location as part of the authorized setup scope; then explicitly set `context.history` to the returned issue reference before history-dependent operations. It is not adopted automatically.

Supply only the views you intend to configure in `input.views`; unrelated views are preserved. If newly created fields are needed in `visible_fields`, finish field creation and rerun view configuration after rereading IDs. The helper configures view objects, layout, filters and visible fields; grouping, ordering, sums, chart and workflow verification still follow the UI recipe below. It does not install templates or silently alter repository policies.

The shipped helpers target GitHub.com and require every related repository in `context.repos`. They fail closed when required APIs are unavailable; support on GHES is not implied by the portable skill format.

## Native workspace recipe

Use APIs through the helpers where supported. For missing API paths, configure authorized settings through GitHub UI or provide these exact steps and mark them pending. View filters below assume labels; substitute the discovered native issue-type filter where appropriate and verify results.

| View | Layout and filter | Fields, grouping and order |
|---|---|---|
| Backlog | Table; `label:"type:story" is:open no:iteration` | Title, Points, Status, Sub-issues progress, Milestone; customer manual order, no implicit sort |
| Iteration Planning | Table; `label:"type:story" is:open` | Title, Points, Iteration, Status, Sub-issues progress, Milestone; group by Iteration; Count and Points sums; preserve customer order within groups |
| Current Iteration | Board; `iteration:@current` | Columns by Status; Title, Labels, Points, Parent issue, Sub-issues progress; Stories and Tasks visible, Points only on Stories |
| Attention | Table; `label:"xp:attention" is:open` or adopted equivalent | Title, Iteration, Parent issue, Status; explicitly maintained attention items, not a claim that the label automatically discovers blockers |
| Release Plan | Table; `label:"type:story"` | Group by Milestone; Title, Points, Iteration, Status, Sub-issues progress; distinguish unscheduled release scope |
| Iteration Roadmap | Roadmap; `label:"type:story"` | Configure Iteration as timeline source where supported; verify actual bars and dates rather than merely creating the view |
| Delivered Stories | Table; `label:"type:story" is:closed` | Iteration, Points, Milestone and closure context; title/description must clarify closure alone is not accepted velocity |

In each view, use its menu to select layout, visible fields, grouping and sorting; enter the filter; choose **Save** to persist changes. For Planning, choose field sums and enable Points (Count may remain). Navigate away and back, checking both settings and visible totals. If the host does not support the desired setting, state the observed limitation and the smallest useful alternative.

For the roadmap, open the view's date/timeline configuration and select Iteration where offered. Confirm one scheduled Story spans its actual iteration dates and an unscheduled Story is not silently assigned dates. If this is not possible, use the grouped iteration/release table and explicitly report the roadmap gap.

## Automation and charts

Open the Project menu → Workflows. Inspect enabled recipes. Allow issue-closed→Done bookkeeping. Disable or adjust Done→issue-close when it could close an unaccepted Story. Native child auto-add can remain enabled; prove membership with a child test or read before using an explicit add, and assign Iteration separately. Keep auto-archive off until retained history and reports are verified. Do not install a parent-closing Action.

Open Insights → New chart. Configure a chart named **Story Points by iteration — current scope** with Story-only filter, Iteration on X, and Sum of Points on Y. Save, leave and return, then compare its totals against the same filtered items. Missing estimates remain unknown and must be called out. If a blank Iteration group is omitted by the chart, show backlog unknown/scope separately instead of pretending it is zero.

Inspect the native historical burnup with a Story-only filter. Verify what Done/closed means under the adopted workflow and label the measure accordingly. It is not automatically accepted velocity, and historical chart availability may depend on plan/host. Archived/deleted items and mutable estimates can affect interpretation. Use the planning log for reproducible accepted delivery while retaining useful native charts.

Finish with direct links and a tour: prioritize in Backlog, select scope in Planning, inspect execution in Current, resolve Attention, and inspect release scope and charts. Report API-created, UI-configured, visually verified and pending settings separately. Never report complete setup merely because objects exist.
