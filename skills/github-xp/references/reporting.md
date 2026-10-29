# Iterations, metrics and releases

Read [history](history.md) for record semantics. Use native views and Insights for current scope; provide links alongside interpretation.

## Close an iteration

Use an explicit source iteration and explicit next iteration. Read the original plan, changes, accepted credit and full current scope. Distinguish planned, added, removed, accepted and carried Stories; show Points and unknowns. Explain that completed Task count is execution progress, not delivered Story value. Include one brief reflection or improvement.

Persist the close report before rollover. With already authorized scope, move unfinished Stories and their open Tasks to the selected next iteration without changing Points. Completed Tasks retain their completed period; accepted Stories retain their acceptance assignment. If no next iteration exists, propose creating/selecting it; do not invent dates or loop to a different period on retry.

Reconcile the same close identity after interruption. An already-moved item is complete for this operation, not a reason to move it again. Stop on conflicting concurrent changes and show what remains. Do not silently recalculate a published report from today's mutable fields.

## Velocity and forecasts

Report accepted, completed Story Points credited once per Story, excluding Tasks, Spikes, cancellations and partial work. Show the last six completed periods by default. Planning uses the last three periods including genuine zeros, with sample size. Missing history is unknown, not zero; fewer known periods or gaps must be visible. Current partial iterations are excluded.

An iteration assignment is not an acceptance timestamp. A current Points-by-iteration chart shows current scope. Historical burnup follows actual state events; synthetic past assignments do not create past delivery. Never label those charts accepted velocity without verifying the measure. Native charts remain useful for scope and progress, with accepted-delivery reports in the GitHub planning log supplying the history they lack.

Use velocity to discuss sustainable scope, not productivity targets, individual rankings, LOC/commit counts or agent multipliers. If evidence/history is missing or conflicting, present the incomplete report and recovery options.

## Release

Require the repository, milestone, explicit tag and target commit. Inspect all milestone issues, including closed-not-planned items and pagination. Verify no open scope remains and all included Stories have valid accepted credit; reconcile cancellations with the customer. Draft Story-centered notes with links, known constraints and evidence. Do not call an arbitrary closed issue accepted.

Inspect an existing tag/release before writing. Reuse a matching draft or stop on conflicting identity/target; never overwrite a published release. Close the milestone and create/reuse the draft under the requested scope, resuming safely if only one step succeeded. Publication, version policy and deployment belong to the existing workflow and require their own authorization.
