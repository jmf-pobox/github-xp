# GitHub history and recovery

Use one explicitly selected GitHub planning-log issue, outside release milestones and delivery counts. Local JSON inputs are temporary execution payloads, not a planning database. Native mutable Project fields do not preserve original commitment or accepted credit, so use concise readable comments with versioned machine-readable records.

The helper owns exact record serialization. Keep the following meanings stable when creating or reviewing inputs:

| Record | Required meaning |
|---|---|
| Plan | Project/iteration identity, stable operation ID, time recorded, ordered Stories with Points snapshots, selected open Tasks and capacity assumptions |
| Acceptance | Story credit identity, actual credit iteration, Points snapshot, criteria and evidence revisions, product decision and time, integration evidence, pending/finalized state and credit time |
| Close | Fixed source/target iteration identity, original commitment, added/removed/accepted/carried scope, accepted total, reflection and rollover status |
| Correction | Published close-record identity, reason, authorizing decision, evidence and replacement period Points total; retain the original report |

GitHub comments can be edited or deleted. This is auditable application history, not tamper-proof storage. Reject malformed/contradictory records, report inaccessible or missing history, and do not silently fill gaps. Do not directly edit machine-readable records to make a report look correct. `correct-history` supports an explicit restatement of a published close report's Points total. It also supports revoking an invalid acceptance credit with `revoke:true`, a reason, decision and evidence. Revocation removes that credit from future close/release eligibility; explicitly restate any already published affected period total. Reports warn about revocations until reviewed. The revoked Story cannot automatically earn new credit: use a new Story for new scope or review a specific history repair. Do not hand-edit records to bypass invariants.

## Credit invariants

Credit once per Story across the selected Project. A reopen preserves the original published period; reacceptance does not earn extra Points. If the original credit was invalid, preserve the original evidence and report the problem. The current helper can record an authorized published period-total correction, labeling restated totals, but cannot invalidate the individual acceptance used by release checks. Do not treat that limitation as corrected release eligibility. New customer scope normally becomes a new Story. Legacy closure without evidence is unverified.

Product decision time and delivery-credit time are distinct. Pending acceptance earns no credit. Finalization requires completed closure plus valid integration/evidence. A timeout between those steps requires reconciliation, not another Story credit. Do not infer acceptance history solely from `closedAt`.

The current helper calendar is UTC. Enumerate expected completed iterations including zero-delivery periods; distinguish missing records from actual zero. Do not hide gaps by substituting an older period in a three-period average. Acceptance in a break or overlapping iterations fails validation; resolve the calendar or propose an adaptation without inventing timestamps.

## Operation recovery

Serialize shared planning writes through one coordinator. Before applying, compare the reviewed facts with fresh issue/Project state; stop if relevant state changed. This is optimistic conflict detection, not a server transaction.

Use stable operation IDs from preview through retries. Creation markers allow discovery after partial failure, but do not guarantee exactly-once creation by concurrent clients. After uncertain create results, reread and locate the marker before retrying. If multiple matches exist, report the conflict rather than picking a title match.

Record an iteration close before moving items. Resume using that record's fixed source and target. Preserve completed Task assignments and original Points. A retry must skip already-completed moves rather than advance the iteration again. After two unsuccessful skill-owned attempts, or sooner without progress, report completed steps, remaining work and the blocker.
