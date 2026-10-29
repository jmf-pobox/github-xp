# Live native GitHub spike

Executed 2026-10-28 Pacific / 2026-10-29 UTC against the user-authorized `jmf-pobox/github-xp` repository. [Open the Project](https://github.com/users/jmf-pobox/projects/3). The Project is private; sign in as its owner to inspect it. Repository issues are public. All sample issues are labeled `xp:demo` and titled `[XP demo]`.

This is a synthetic vocabulary-learning project, not evidence that any product was implemented or accepted. Past iteration assignments are sample data; GitHub event timestamps are real spike timestamps. No commits, PRs, releases, custom Actions, or web application were created.

## Tour

| Surface | What to inspect |
|---|---|
| [Backlog](https://github.com/users/jmf-pobox/projects/3/views/1) | One unassigned Story, with Points and milestone |
| [Iteration Planning](https://github.com/users/jmf-pobox/projects/3/views/2) | Open Stories grouped by Iteration; Count and Points sums configured through the UI |
| [Current Iteration](https://github.com/users/jmf-pobox/projects/3/views/3) | Board grouped by Status, using `iteration:@current`; its contents change with the calendar |
| [Release inventory](https://github.com/users/jmf-pobox/projects/3/views/4) | All Stories with milestone, iteration, estimate and progress |
| [Attention](https://github.com/users/jmf-pobox/projects/3/views/5) | A Story awaiting acceptance and a decision Spike; explicit attention labels, not automatic blocker detection |
| [Iteration Roadmap](https://github.com/users/jmf-pobox/projects/3/views/6) | Native roadmap created; timeline field mapping remains visually unverified |
| [Delivered Stories](https://github.com/users/jmf-pobox/projects/3/views/7) | Two synthetically completed Stories; closure is not sufficient production acceptance evidence |
| [Release Planning by Milestone](https://github.com/users/jmf-pobox/projects/3/views/8) | Native milestone grouping created through REST and verified through GraphQL |
| [Story points by iteration chart](https://github.com/users/jmf-pobox/projects/3/insights/1) | Saved native chart with Iteration on X and Sum of Points on Y; see limitations below |

## Dataset and experiments

The final dataset has six Stories, eight native sub-issue Tasks, one time-boxed Spike, three weekly iterations, two release milestones, and a native blocked-by relationship. Personal-account labels supply Story/Task/Spike classification. Only Stories receive Points; Tasks measure execution progress without duplicating estimates.

| Assignment | Story Points after rollover |
|---|---:|
| Demo 1, October 19–25 | 5 |
| Demo 2, October 26–November 1 | 2 |
| Demo 3, November 2–8 | 8 |
| Backlog | 3 |

These are current scope totals, not historical velocity. The open-Story Planning view excludes the two completed Demo 1 Stories.

- [Story #4](https://github.com/jmf-pobox/github-xp/issues/4) remains open despite 100% completed sub-issues. Its example acceptance decision is still outstanding. Native progress and product acceptance are different facts.
- [Task #12](https://github.com/jmf-pobox/github-xp/issues/12) is natively blocked by [Spike #14](https://github.com/jmf-pobox/github-xp/issues/14). A text reference alone was not used as the dependency.
- Creating [Task #15](https://github.com/jmf-pobox/github-xp/issues/15) under Story #3 caused the enabled native sub-issue workflow to add it to the Project automatically. It received Todo but **did not inherit Iteration**. We assigned Iteration explicitly; closing it then changed Status to Done through the native workflow.
- Rollover moved [Story #3](https://github.com/jmf-pobox/github-xp/issues/3) and its open Task #10 from Demo 2 to Demo 3. Closed Tasks #9 and #15 remained in Demo 2. Story Points stayed at 3. A comment on Story #3 records the synthetic experiment. This tests the state transition, not a production retry-safe command.
- The new Project initially enabled Done-to-issue-close automation. We disabled it so a board drag cannot bypass acceptance. Closed-to-Done remains enabled and was tested. PR-related workflows were observed but not exercised.

## What the spike establishes

GitHub supplies a useful XPlanner-like workspace: native hierarchy, completion percentages, estimates, iteration scheduling, release milestones, dependencies, grouped tables, board columns, scope totals, and an Insights chart. Agents can maintain that workspace while a solo owner plans and accepts work directly in GitHub. The same model can support a team; team permissions and multi-user operation were not tested here.

GraphQL successfully created the Project, number/iteration fields, views and assignments. Native sub-issues and dependencies were written using REST. REST view creation supports `group_by`; the inspected GraphQL view configuration exposes fewer layout settings. The REST view path worked with the owner login (`users/jmf-pobox/projectsV2/3/views`), while using the numeric user ID returned 404 in this trial. Field numeric IDs came from `databaseId` / REST fields. Roadmap views rejected visible-field configuration, so their creation omitted it. These are observed API details, not claims that every GitHub host behaves identically.

The initial authentication failure came from an invalid `GH_TOKEN` overriding a valid keyring login. Removing that variable only from CLI subprocess environments restored access. No credentials were printed or changed.

## Metrics and remaining checks

The saved native chart was visually verified before rollover with scope totals 5, 5, 5, 3. Its filter is still blank. It is numerically Story-only in this fixture because only Stories have Points, but the final setup must explicitly filter Stories and visually recheck the post-rollover chart (expected 5, 2, 8, 3).

The default burnup was inspected. It counted mixed issue types and their actual spike-day events. Assigning work to a past iteration does not create past delivery events. Reliable accepted-Story velocity, original commitment versus later changes, and corrections need explicit evidence/history beyond a current scope chart. Native charts remain part of the product; a small GitHub planning log should supplement only these proven history gaps.

Safari became unavailable to computer control before the explicit chart filter and roadmap timeline checks could finish. Planning grouping persisted in the API; Points sums were configured and saved in the UI but were not rechecked after rollover. No claim of complete visual verification is made. No retry/fault injection, multi-page dataset, PR integration, four-host skill execution, or real product acceptance was tested.

## Evidence and follow-through

[Final API snapshot](spike/verified-project.json), [compact checked summary](spike/verified-summary.json), and [object manifest](spike/manifest.json) identify the live objects. `spike/dataset.json` is the initial 14-item seed; Task #15 and rollover are subsequent experiments. `spike/auto-add-observation.json` and `spike/rollover-before.json` preserve intermediate evidence. Raw local API logs contain requests and responses, not tokens; they are excluded from Git.

The revised prompt and design incorporate these findings. Final skill/runtime construction remains at the design-review checkpoint. The next build should reconcile existing fields, objects and workflows; verify actual membership instead of blindly adding; explicitly schedule children; preserve acceptance boundaries; and provide concrete UI steps for settings without a verified API path.

References: [Projects GraphQL](https://docs.github.com/en/graphql/reference/projects), [REST views](https://docs.github.com/en/rest/projects/views), [REST fields](https://docs.github.com/en/rest/projects/fields), [native Insights](https://docs.github.com/en/issues/planning-and-tracking-with-projects/viewing-insights-from-your-project/about-insights-for-projects).

## Build follow-up, 2026-10-29 UTC

The portable helper now exists and passed live creation/retry checks: history issue [#16](https://github.com/jmf-pobox/github-xp/issues/16) and synthetic helper Spike [#17](https://github.com/jmf-pobox/github-xp/issues/17). An identical Spike request yielded zero planned mutations. The original fixture remains 15 items; the helper test adds one Project item without Points and one history issue outside the Project.

A later Safari observation verified Planning sums after rollover: Demo 2 = 2, Demo 3 = 8, backlog = 3. Browser control then failed again, so the explicit chart Story filter and roadmap mapping remain unfinished. See [VERIFY.md](VERIFY.md) for the implemented skill and client checks.
