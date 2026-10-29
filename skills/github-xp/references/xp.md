# XP decisions

Use XP to choose the next useful action, not to add ceremony. The planning game joins customer priorities with developer estimates and observed delivery. In solo work one person may hold both responsibilities; agents help explore choices and perform work without manufacturing product authority.

| Practice | Decision it changes | GitHub support and limit |
|---|---|---|
| Small releases and simple design | Slice a visible outcome that can be demonstrated; postpone speculative infrastructure | Stories, milestones and draft Releases expose scope; a milestone alone does not make an increment releasable |
| Customer collaboration | Ask for examples where behavior is ambiguous; demonstrate outcomes early | Issue conversations preserve decisions, but do not substitute for useful direct collaboration |
| Test-first development | Define a failing behavioral example before implementing a bug fix or new behavior where appropriate | CI publishes test results; checkboxes are not executable tests |
| Continuous integration | Keep changes small and integrate frequently through the existing workflow | PRs and CI support integration; long-lived agent branches delay feedback |
| Pair programming | Collaborate interactively on a hard decision or implementation | Human–agent pairing can shorten feedback; PR review is not automatically pairing |
| Refactoring and quality | Improve structure while preserving tested behavior | Keep refactoring within scope; do not trade away quality to inflate velocity |
| Collective ownership and coding standards | Let the best available contributor improve code under shared conventions | Repository instructions and review support shared ownership; do not assign permanent code territories to agents |
| Sustainable pace | Limit concurrent work to actual implementation, review and integration capacity | Board WIP exposes overload; agent count is not a capacity estimate |
| Reflection | At an iteration boundary identify one concrete improvement | A short close report preserves learning without requiring a new meeting |

Examples:

- “Support every vocabulary variant” is too broad for a first slice. Propose “choose one regional variant when generating a deck,” with concrete input/output examples, then estimate.
- An unknown media API is a timeboxed Spike with a question and expected evidence. Do not hide uncertain research inside a confident Story estimate.
- A Story has all Tasks closed but its display has not been demonstrated in the real client. Keep it open and state the missing acceptance evidence.
- Three implementation agents finish changes faster than the owner can review demos. Reduce WIP and planned scope rather than increase the iteration commitment.

Communication means exposing decisions and uncertainty. Simplicity means the smallest useful slice and fewest necessary fields. Feedback means short implementation and customer loops. Courage means surfacing risk and changing scope openly. Respect means accepted responsibility, transparent estimates and sustainable work.
