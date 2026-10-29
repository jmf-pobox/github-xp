# GitHub helper contract

Invoke the installed helper by absolute path; its location is independent of the target checkout:

```text
python3 <installed-skill-path>/scripts/xp.py --help
python3 <installed-skill-path>/scripts/xp.py <command> --help
```

Commands implement concrete reviewed operations: `setup`, `story`, `split`, `plan`, `start`, `finish`, `accept`, `close-iteration`, `velocity`, `release`. The agent supplies intent, prioritization and evidence adjudication. A JSON assertion does not establish a customer decision or prove a test passed.

Common interface: `--context` selects a JSON target/configuration file; `--input` reads a JSON operation payload from a file or stdin; `--operation-id` is stable across preview/apply/retry. Default execution is read/preview; `--apply` enables writes within existing authorization, and `--dry-run` forbids writes. Use `--help` for flags and the exact JSON inputs below for payload fields. Configuration captures IDs and semantic mappings; it is not a second planning database.

## Identities and API rules

Resolve owner kind, repository, actual default branch, Project number/node ID, field IDs, status option IDs and iteration IDs before mutation. Keep REST numeric issue IDs distinct from repository issue numbers and GraphQL node IDs. Use fully qualified issue URLs or `owner/repo#number` for cross-repository work. Resolve ambiguous names explicitly.

Use structured JSON variables and subprocess argument arrays. Never interpolate user titles/bodies into a shell or GraphQL query. Do not print auth tokens. Paginate issues, fields, views, items, nested children/dependencies and history comments; report archived/redacted or inaccessible content rather than silently excluding it from authoritative totals.

GitHub errors may appear in HTTP-successful GraphQL responses. Auth, authorization, missing capability, validation and rate-limit failures are different conditions. Bound retries; honor retry delays, reconcile uncertain writes, and report partial completion. Do not use undocumented internal browser endpoints as an API substitute.

## Capability evidence

Observed on GitHub.com, 2026-10-28/29, in a personal-account demonstration Project:

| Capability | Evidence and consequence |
|---|---|
| Number/Iteration fields and assignments | Live GraphQL creation and assignment succeeded; use discovered IDs and explicit child scheduling |
| Native sub-issues and dependencies | Live REST writes succeeded; hierarchy and blocked-by links are distinct |
| Native sub-issue auto-add | Child became a Project item automatically with Todo; Iteration did not inherit |
| Issue-closed→Done | Verified by closing a sample Task; it is bookkeeping, not acceptance |
| Done→issue-close | Enabled in the new Project; disabled through UI to protect acceptance |
| Tables, board, roadmap objects | Created through GraphQL; roadmap rejected visible-field configuration |
| View grouping | Iteration grouping set through UI; milestone grouping created through REST and verified through GraphQL |
| Scope Insights chart | Saved through UI; explicit Story filter and post-rollover visual verification were still pending in the spike |
| Manual priority order / roadmap timeline mapping | Not verified end to end in the spike; inspect actual UI behavior before claiming support |
| Organization issue types / GHES differences | Documented, not established by the personal-account spike; probe the target |

The REST view route accepted the owner login in `users/<login>/projectsV2/<number>/views`; using a numeric user ID returned 404 in that trial. Numeric field IDs came from REST fields or GraphQL `databaseId`. Treat these as observed target behavior and verify current schemas on a different host/version.

Sources: [Projects GraphQL](https://docs.github.com/en/graphql/reference/projects), [REST views](https://docs.github.com/en/rest/projects/views), [REST fields](https://docs.github.com/en/rest/projects/fields), [sub-issues](https://docs.github.com/en/rest/issues/sub-issues), [dependencies](https://docs.github.com/en/rest/issues/issue-dependencies), [organization issue types](https://docs.github.com/en/rest/orgs/issue-types), [built-in automation](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-built-in-automations), [Insights](https://docs.github.com/en/issues/planning-and-tracking-with-projects/viewing-insights-from-your-project/about-insights-for-projects).

## Exact CLI inputs (v1)

`--help` describes flags; this section describes JSON. `--input -` reads stdin. `--fixture snapshot.json` performs offline previews and refuses `--apply`. `--keyring` explicitly ignores token environment overrides only in gh subprocesses; otherwise authentication is unchanged. Helpers currently target GitHub.com. They do not silently claim GHES compatibility.

Context is a configuration file, not cached planning state:

```json
{
  "owner": "your-login",
  "repos": ["your-login/your-repo"],
  "project": 3,
  "history": "your-login/your-repo#20",
  "fields": {"points": "Points", "iteration": "Iteration", "status": "Status"},
  "status": {"todo": "Todo", "in_progress": "In Progress", "done": "Done"},
  "labels": {"story": "type:story", "task": "type:task", "spike": "type:spike"}
}
```

Only `owner` and nonempty `repos` are initially required. Add `project` after creation and `history` after selecting/creating the planning-log issue. Optional `types` maps `story/task/spike` to existing organization issue-type names; setup probes these rather than modifying organization taxonomy. Include repositories containing related children/blockers; inaccessible related scope fails closed. Omit optional mappings to use the defaults above.

Run from any directory:

```text
python3 /absolute/skill/scripts/xp.py plan --context /tmp/context.json --input /tmp/plan.json --operation-id plan-2026-11-02 --dry-run
python3 /absolute/skill/scripts/xp.py plan --context /tmp/context.json --input /tmp/plan.json --operation-id plan-2026-11-02 --apply
```

Use the same operation ID and input when resuming. Preview results list ordered API calls. Apply prints completed steps; an error stops further writes. Creation results supply new IDs. Preview IDs that depend on creation are symbolic `$ref` values resolved only during apply. Serialize writers: fresh-state checks detect intervening edits but are not atomic compare-and-swap locks.

### Setup

No input inspects the selected workspace with zero mutations. Without a selected Project, pass `{"title":"My XP workspace"}` and a stable operation ID. Creation includes that ID in the title so an uncertain create can be reconciled. Use the returned Project number in context and rerun. Do not rename away the marker until creation is reconciled.

For configuration:

```json
{
  "configure": true,
  "iterations": [
    {"title":"Week 1","startDate":"2026-11-02","duration":7},
    {"title":"Week 2","startDate":"2026-11-09","duration":7}
  ],
  "views": [
    {"name":"Backlog","layout":"TABLE_LAYOUT","filter":"label:\"type:story\" is:open no:iteration"},
    {"name":"Iteration Planning","layout":"TABLE_LAYOUT","filter":"label:\"type:story\" is:open"},
    {"name":"Current Iteration","layout":"BOARD_LAYOUT","filter":"iteration:@current"},
    {"name":"Release Plan","layout":"TABLE_LAYOUT","filter":"label:\"type:story\""},
    {"name":"Attention","layout":"TABLE_LAYOUT","filter":"label:\"xp:attention\" is:open"},
    {"name":"Iteration Roadmap","layout":"ROADMAP_LAYOUT","filter":"label:\"type:story\""}
  ]
}
```

Existing fields are reused; iteration definitions are only used to create a missing field, never to silently replace its calendar. Selected views are created/reconfigured by exact unique name; unrelated views remain untouched. Optional `visible_fields` contains exact existing field names; create fields first, then preview views using them. Roadmap cannot take visible fields. Adjust filters to native issue types when configured. Field sums, grouping, rank, workflows and charts have explicit UI instructions in setup; helpers do not claim to configure those settings. Templates are bundled assets to propose through the existing repository review process, not files automatically overwritten by setup.

### Create and split

Story input:

```json
{"repo":"your-login/your-repo","title":"Resume practice","body":"## Outcome\nResume where I stopped.\n\n## Acceptance criteria\nAC1: Reopening resumes the last card.","criteria_reviewed":true,"points":3}
```

Omit Points for explicitly unknown estimates. Optional `milestone` is a repository milestone number. For a Spike use `kind: "spike"`, nonempty `question` and `timebox`, and render those in `body`; omit Points. Body is literal Markdown, never shell code. `criteria_reviewed` records the agent's completed inspection, not a substitute for it.

Split input:

```json
{"story":"your-login/your-repo#21","tasks":[{"key":"persist","repo":"your-login/your-repo","title":"Persist practice position","body":"Scope and verification instructions.","blocked_by":[]}]}
```

Task `key` must be unique and stable. `blocked_by` accepts existing qualified issue references. Create new dependent Tasks in successive reviewed batches if their IDs are not yet known. Existing native membership is reused and child Iteration assigned explicitly. Helpers refuse reparenting and cycles.

### Plan and start

Plan input:

```json
{"iteration":"discovered-iteration-id","stories":["your-login/your-repo#21"],"availability":"Owner has two hours for product decisions and demos; one implementation stream."}
```

An explicit empty `stories` list records an intentional zero-scope period. Stories are in customer-selected order; this does not reorder the web view automatically. Unknown Points require estimation before committing this plan. Planning adds selected Stories/open Tasks to the iteration; it does not silently remove other scope. Use a new reviewed operation for a revised plan; original commitment remains the first recorded plan.

Start input supplies `issue`, optional real GitHub `assignee`, and `brief` with nonempty `criteria`, `scope`, `instructions`, `workflow`, `dependencies`, `allowed_actions`, `expected_evidence`, and `executor`. Use explicit text such as `"none"` for no dependencies. Include `started: true` only once execution has begun. For a tiny directly implemented Story add `unsplit: true`. The helper records the brief and updates Status; it does not spawn agents or create branches.

### Finish and accept

Shared evidence shape:

```json
{
  "revision":"tested-integrated-revision",
  "verified_revision":"tested-integrated-revision",
  "tests":["Actual command, result, and evidence reference"],
  "criteria":{"AC1":"Demonstration/test evidence for AC1"},
  "gates_passed":true,
  "prs":["https://github.com/your-login/your-repo/pull/22"],
  "pr_revisions":{"https://github.com/your-login/your-repo/pull/22":"inspected-pr-head-sha"}
}
```

The agent must inspect source criteria, actual test/review/demo evidence, revision validity, and authorization before constructing this object. The helper verifies required structure and live PR merge/default-branch/head facts. It cannot establish the truth of arbitrary assertions or decide product acceptance. For non-code work replace PR fields with `non_code: true` and nonempty `completion_evidence`.

Finish input is `{"issue":"owner/repo#22","evidence":{...}}`, plus `unsplit: true` for a directly implemented Story. Tasks close only after verification; Stories remain open. Existing merged PR traceability must be checked by the agent; helper output gives the expected qualified closing/reference syntax without creating or editing a PR.

Accept input:

```json
{
  "story":"your-login/your-repo#21",
  "unsplit":true,
  "iteration":"discovered-credit-iteration-id",
  "criteria":{"source":"issue URL or authoritative spec section","revision":"verified criteria revision","items":["AC1"],"verified":true},
  "evidence":{"revision":"sha","verified_revision":"sha","tests":["actual test evidence"],"criteria":{"AC1":"verified outcome evidence"},"gates_passed":true,"non_code":true,"completion_evidence":"only use this alternative for genuinely non-code work"},
  "decision":{"authority":"owner or explicitly delegated authority","reference":"recorded decision URL or durable decision text","accepted":true,"revision":"sha","at":"2026-11-03T14:00:00Z"},
  "completed_at":"2026-11-03T14:05:00Z"
}
```

Use actual times and actual evidence; this is a schema example, not an approval. Code Stories require the PR evidence shape above. `unsplit` is needed only when there are intentionally no child Tasks. Every required child must be closed as completed; a cancelled Task requires resolving scope explicitly first. The helper writes acceptance intent, reconciles closure/Status, checks completed closure and writes final credit. Resuming uses unchanged input/operation ID. Reacceptance of a reopened Story records the new decision and closes it without granting second credit.

### Close, report, correct and release

Close input: `{"iteration":"source-id","next_iteration":"target-id","reflection":"Try one smaller Story next week."}`. The source period must have ended in UTC and have a recorded plan. Supply a `cancellations` mapping from cancelled Story references to explicit scope decisions when applicable. The close record freezes scope before moves; reuse the original request to finish interrupted rollover. Missing next iteration, archived/inaccessible scope, or closed Stories without acceptance history stop the operation.

Velocity input is optional `{"count":6}`. Reports enumerate configured completed calendar periods, distinguish missing from zero, and calculate the last three periods only when all available periods in that window are recorded. Fewer than three show sample size; no history yields unknown. Removed calendar definitions cannot be reconstructed automatically; retain the Project calendar and history.

`correct-history` input: `{"target":"full-close-record-key","replacement_points":3,"reason":"Why published total was wrong","decision":"Explicit authorizing decision","evidence":"Supporting evidence"}`. It appends a correction and labels reports restated. It does not alter original records or award another Story credit. To revoke an invalid acceptance, target its full acceptance-record key and supply `revoke:true` instead of replacement_points, with the same reason/decision/evidence fields. Future close/release eligibility excludes revoked credit; explicitly restate already published affected totals. Reports flag revocations, and a revoked Story cannot silently receive new credit.

Release input: `{"repo":"owner/repo","milestone":1,"tag":"v0.1.0","target":"40-character-commit-sha","cancellations":{"owner/repo#9":"Recorded scope-removal decision"}}`. `name` is optional. All milestone issues must be closed and completed Stories credited. Existing tag targets are checked; an existing matching draft is reused. Published or conflicting releases stop the operation. The helper prepares a draft and closes the milestone; it never publishes or deploys.
