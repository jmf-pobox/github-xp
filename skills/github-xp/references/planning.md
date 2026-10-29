# Shape and plan

## Story or Spike

Find existing work before creating anything. Shape a Story around an observable customer outcome, examples and exclusions. Criteria may be inline or stable references to authoritative specification sections; identify the revision used. Keep uncertainty visible. A Spike has a learning question, timebox and expected evidence, with no Points.

Use the developers' estimate, or propose an estimate for confirmation when acting as developer. The solo owner can make both priority and engineering decisions. Never invent precision or treat an unestimated Story as zero. Keep Points only on Stories.

Use the `story` helper for concrete issue creation and Project membership. A helper must receive the explicitly rendered body: CLI creation does not automatically apply a repository issue form. Adapt the bundled Story/Spike assets only if existing formats lack the needed information; do not overwrite templates.

## Split

Split only where useful for bounded implementation or delegation. Preserve vertical customer value at Story level; Tasks may represent concrete engineering work but should be independently verifiable. Tiny Stories can remain unsplit. Use native sub-issues, not a checklist as the hierarchy of record. Give Tasks no Points.

Resolve dependencies by issue identity. Avoid self-links and cycles. A parent relationship is not a dependency. Use the `split` helper to create/reuse the agreed children, link them, and verify Project membership. Enabled native auto-add may already add a child; it does not guarantee inherited Iteration. Schedule open children explicitly with their Story.

## Plan an iteration

1. Inspect the Backlog in its customer-controlled order, the chosen iteration dates, current scope, blockers and unknown estimates. A Project item connection is not evidence of saved view order. If the API cannot expose canonical rank, inspect the view or request an explicit ordered list.
2. Read [history](history.md) when computing capacity. Show the last three completed periods including real zeros, sample size and missing history. With no reliable history, call capacity unknown and choose a small initial scope with the owner.
3. Account for the human's product, demo and integration availability, not just agent implementation time. Identify dependencies, one practical WIP limit and the proposed cut line.
4. Show selected Stories in priority order with Points/unknowns, excluded work, blockers and availability assumptions. Honor existing authorization; ask for a scope decision only when it is not already established.
5. Record the plan before changing assignments. Assign selected Stories and their open Tasks to the explicit iteration. Recheck membership and preserve completed Tasks' history. Report direct links and any partial failure.

The `plan` helper applies a concrete reviewed selection; it does not decide value, priority or capacity. It requires nonnegative Points for every selected Story. You can discuss unestimated work and leave it in Backlog, but must resolve estimates before applying that selection; do not insert zero as a substitute. Carrying incomplete work belongs to [iteration reporting](reporting.md), not a silent extension of dates or inflation of Points.
