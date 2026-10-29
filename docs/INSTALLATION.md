# Installation verification

Tested 2026-10-29 UTC with `skills@1.7.4`, Node 26.9.0 and `gh` 2.101.0. One portable skill directory is the distribution unit; it now includes the full MIT license. We use existing installers rather than maintain a separate installer or harness-specific copies of the source.

## Reproducible lifecycle checks

Run `python3 tests/installer_smoke.py` to exercise the pinned npm installer against disposable source/project directories. It needs Node/npm and registry access. It uses temporary XDG state/config and npm cache paths, never changes HOME/CODEX_HOME, and does not write to real harness installations. The dedicated Installer smoke test workflow runs the same checks in CI.

Observed local results:

| Check | Result |
|---|---|
| Four explicit targets | Codex, OpenCode and Pi share `.agents/skills/github-xp`; Claude gets `.claude/skills/github-xp` pointing to it |
| Payload completeness | Every source file, including scripts, references, assets and license, matched the installed copy |
| Installed execution | Helper `--help` ran from an unrelated working directory |
| Identical reinstall | One complete payload; no duplicate nesting |
| Same-name collision | Non-interactive reinstall replaced conflicting content and removed a local-only file; it is not a merge operation |
| Changed local source | Repeating `add` propagated changed content to all targets |
| Removal | `remove github-xp -y` removed its canonical folder, links and lock entry, preserving an unrelated skill |
| Copy mode | Complete independent Claude copy; same successful removal behavior |

User-facing instructions omit `-y`; automation tests supply it for explicitly disposable objects. When invoked inside an AI agent, version 1.7.4 may enable non-interactive mode regardless, so agents must inspect existing installations and their authorization first.

Two failed experiments informed the final instructions:

1. Removing only the four named agents left the shared directory in place because other detected harnesses could use it. Full removal of **this skill** omits the agent filter.
2. `remove --agent '*'` is documented on the inspected upstream main branch but rejected by the published 1.7.4 package. The tested command is simply `remove github-xp`, not `--all` (which would select all skills).

## GitHub CLI alternative

A clean local-source `gh skill install ... --from-local --dir <temporary-directory>` preserved the license and all supporting files. It injects source-tracking metadata into SKILL.md, so that file intentionally differs from the source. A trial against the working checkout also copied ignored Python bytecode; clean source/repository installs avoid those untracked development files.

`gh skill` is marked preview in installed help. Its `update --dir` supports isolated checking and source pinning is available on installation. This installed version does not expose a `gh skill remove` subcommand. Consequently, the skills CLI remains our primary lifecycle route. Do not combine installers on the same destination or assume their update/removal metadata is interchangeable.

## Boundaries

The lifecycle suite tests project-scope installation, symlinks/copies, reinstall, collisions and removal. It does not type through the interactive checkbox UI, modify actual user-wide installations, or exercise every host's model after every installer run. Read-only host behavior was tested separately in [VERIFY.md](VERIFY.md). Remote-source update verification is recorded separately below when executed.

For stable adoption, retain the project lock file where produced, review updates, and keep project-specific behavior in repository workflow instructions. Pin the skill to a source ref when exact content matters; pinning `skills@1.7.4` only selects the installer version.

## Remote update verified

Installed the published skill at `23737871` into a temporary project before the packaging commit. After pushing `2cde49e`, ran `npx skills@1.7.4 update github-xp -p -y` in that project. It updated one skill successfully. Every tracked file in the new skill matched the installed payload byte-for-byte, including the newly bundled license and setup instructions. Claude's link still resolved to the canonical folder, and the project lock hash advanced. This is an actual changed-version GitHub-source update, separate from the local-source reinstall checks above.

The remote-source test installation was then removed with `remove github-xp -y`; its canonical folder, Claude link and project lock entry were cleared. No actual user-wide harness installation was changed.

GitHub CI passed for the packaging commit: [installer lifecycle](https://github.com/jmf-pobox/github-xp/actions/runs/40801626445) and [package/runtime validation](https://github.com/jmf-pobox/github-xp/actions/runs/40801626417), including the Python 3.10/3.13 matrix.
