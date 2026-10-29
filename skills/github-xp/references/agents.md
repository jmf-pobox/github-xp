# Delegation and human takeover

Use the host's available delegation mechanism only when it is available and authorized. Python helpers never launch models or another agent CLI. Reuse the existing coordinator and its engineering agents; create a planning or acceptance-assistance role only when it adds useful independent work.

Before concurrent implementation, assign disjoint scope and one writer per branch/worktree. Shared files, dependent changes, Project mutations and history writes require serialized coordination. If scopes overlap, repartition or run sequentially. Do not rely on different agent names to isolate a shared checkout.

Each dispatch includes the work brief from [integration](integration.md), a stopping condition, allowed side effects and the required result. Review identifies the inspected revision. Relevant changes after review require renewed verification under repository policy. An agent reviewing its own change is not independent review.

| Situation | Behavior |
|---|---|
| Solo owner wants to focus on product | Offer a bounded plan; delegate implementation through the existing workflow; return evidence and unresolved product decisions |
| Owner wants to code | Give the same Task brief to the human; agents may test, investigate or review as requested |
| Human takeover | Preserve branch/worktree and uncommitted work; summarize current state, tests, blockers and next action; do not reset or restart |
| Team | Respect actual assignees, availability and approval rules; do not overwrite another contributor's work |
| No sub-agents | Perform responsibilities sequentially and disclose that review was not independent |
| Review loop stalls | Preserve findings and follow the existing workflow's stopping rule; do not relax criteria to obtain a green result |

Keep useful outcomes and current responsibility on the issue/PR. Assignees are real GitHub accounts; record an agent role in context rather than inventing an identity. Shared credentials are not separate human approvals.

The owner remains product acceptance authority unless explicitly delegated. Agents may recommend acceptance but cannot fabricate a decision. Two unsuccessful attempts bounds this skill's own planning/reconciliation retries, not the existing engineering review loop.
