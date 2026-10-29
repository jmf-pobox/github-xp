# XPlanner, XP, and portability research

Research date: 2026-10-28. Sources distinguish observations from proposed design choices.

## What survives of XPlanner

The [wcherry/XPlanner repository](https://github.com/wcherry/XPlanner) remains publicly available and describes an XP schedule board. The [XPlanner+ SourceForge page](https://sourceforge.net/projects/xplanner-plus/) remains available; it lists iterations, stories, tasks, virtual note cards, time tracking, burndown, and estimate accuracy, and displays a last-update date of 2013-09-14. This supports “historical tool with surviving artifacts,” not a claim of current active maintenance. The original SourceForge page could not be fetched during this pass.

The supplied InfoWorld article, “Manage the agile team with XPlanner,” by David Elliot and Justin Smith, describes customer stories refined collaboratively into developer tasks, planned/unplanned work, ideal-hour estimates and actuals, and fixed iteration boundaries. It describes XPlanner as LGPL software. We use this as historical context, not a proposal to revive its Java stack or copy its code.

## What the supplied images show

All three JPGs were visually inspected. The collage shows an iteration dashboard, a task-edit screen, a Story with a task table, and people/effort charts. The two Portuguese presentation screenshots show tabular iteration/story tracking and a separate charts page. The images are low resolution; they support the overall interaction pattern, not reliable transcription of every number or label.

The small `Extreme_Programming.pdf` presents nested feedback loops, from code/pairing and unit tests through acceptance and iteration/release planning. The other two XP PDFs discuss values and practices. Their useful implication here is that a planning board covers only part of XP: the skill also needs implementation and customer-feedback behavior.

Local inputs inspected:

- `research/Manage the agile team with XPlanner | InfoWorld.pdf`
- `research/Extreme_Programming.pdf`
- `research/Extreme programming - Wikipedia.pdf`
- `research/XP Values, Principles & Practices: Complete Overview.pdf`
- `research/screen_collage-164508183.jpg`
- `research/Ferramentas-de-Planejamento-e-Acompanhamento-22-320-1162423354.jpg`
- `research/Ferramentas-de-Planejamento-e-Acompanhamento-23-320-1533026249.jpg`

PDFs were text-extracted; screenshots were visually inspected. This is content research, not full PDF layout verification. The [Agile Alliance XP overview](https://agilealliance.org/glossary/xp/) supplies additional methodology context. The historical extremeprogramming.org pages did not load in this pass.

## Design interpretation

| Keep from the observed pattern | Translate into GitHub | Leave out of v1 |
|---|---|---|
| Shallow planning hierarchy | Project Iteration → Story issue → native Task sub-issue | Custom hierarchy database |
| A readable shared board | Backlog, Current, and Planning views | Recreated web UI and decorative charts |
| Customer outcomes and discussion | Story body, examples, evidence, acceptance decision | PRD/epic gate for every change |
| Developer-owned task detail | Small Tasks, assignees, dependencies where necessary | Assignment by utilization targets |
| Fixed timebox and replanning | Carry unfinished work without extending the period | Pseudo-iteration for Backlog; use unset Iteration |
| Honest learning from delivery | Accepted-story points and short reflection | Mandatory timesheets, individual rankings, LOC velocity |

Story points and the proposed completion history are this project's design choices. They are not claims about original XPlanner behavior or universal XP requirements. Likewise, a seven-day iteration is a configurable default, not a definition of XP.

## Portability evidence

The [Agent Skills specification](https://agentskills.io/specification) defines a folder containing `SKILL.md`, with YAML name/description and optional supporting resources. Use that common packaging and load references only when relevant.

- [Codex skill documentation](https://learn.chatgpt.com/docs/build-skills): reviewed as the official source for packaging and client integration.
- [Claude Code skills](https://code.claude.com/docs/en/skills): documents the shared standard and Claude extensions. Keep those extensions out of the common skill.
- [OpenCode skills](https://opencode.ai/docs/skills/): documents discovery, frontmatter, and naming requirements.
- [Pi skills](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md): documents the standard, relative resource paths, progressive loading, and `/skill:name` explicit invocation. The requested historical badlogic/pi-mono documentation URL redirects to this repository.

One canonical folder with plain instructions and deterministic helpers is the proposed portability baseline. Actual installation paths and host-specific invocations belong in the eventual setup reference and require host discovery tests. No runtime host compatibility has been tested yet.
