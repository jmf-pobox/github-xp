# Reconcile Story acceptance

Acceptance is a product decision supported by evidence. Read [history](history.md) before recording credit and [GitHub contract](github.md) before calling `accept`.

Re-read the current Story and all required child issues, including additional pages. Identify inline criteria or referenced specification sections at a known revision. An empty section, unresolved reference, unrelated checklist, unchecked requirement, inaccessible specification or bare “done” assertion cannot establish acceptance. Ignore example checklists inside code fences.

For each criterion, establish the evidence and revision that verifies it. Inspect the relevant test/review/demo artifact, not just its title. Confirm required code has integrated into the actual default branch and that no relevant later change invalidates the evidence. Report precise gaps instead of manufacturing criteria or acceptance.

Verify the owner/customer decision or an explicit delegation rule and its applicability. Reuse a valid existing operator demonstration or acceptance comment; do not demand it again. The solo owner may also be the implementer. Agents sharing credentials do not supply independent human approval. An agent recommendation alone is not a customer decision.

Required Tasks must be completed and verified. A cancelled Task needs an explicit agreed scope change; it cannot silently satisfy a criterion. The current helper refuses acceptance while any linked child is cancelled. Resolve the agreed decomposition/criteria through an authorized GitHub change first and re-read the Story, rather than bypassing this check. An explicitly unsplit Story can have no children. Green CI or 100% sub-issue progress alone is insufficient.

Record the decision time separately from credit time. Credit time is when all required acceptance and integration conditions hold, not automatically the PR merge timestamp; a later customer decision delays credit. A pre-merge demonstration can remain valid, but earns no delivery credit before integration. Resolve the actual credit iteration using UTC, the helper calendar. The helper refuses a completion timestamp outside the selected iteration or inside overlapping iterations. A break or overlap requires correcting the calendar/scope or proposing a supported adaptation; do not falsify the completion time to pass validation. Do not move already accepted work to improve a report.

Use the stable Story credit identity. Persist the pending acceptance evidence, reconcile completed closure, then finalize credit according to the helper's history protocol. On interruption, resume the same operation from GitHub. Report whether acceptance is pending or finalized. Reopening and accepting again does not earn a second credit; corrections require an explicit reason and authorization, preserving the original published history.

Evidence adjudication remains the agent's responsibility. Structured helper inputs capture the reviewed facts; they do not prove those facts merely by existing in JSON.
