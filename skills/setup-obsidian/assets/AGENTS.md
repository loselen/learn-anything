# Learning vault rules

Instructions for AI agents working in this vault. Claude Code reads them through `CLAUDE.md`, which imports this file.

Each topic has a **map note** that holds its dependency graph. Each node in the graph has a **lesson note** that grows one teaching cycle at a time.

## Folders

| Folder | Contents |
|---|---|
| `Maps/` | One map note per topic |
| `Lessons/` | One lesson note per graph node |
| `Sources/` | One note per source |
| `Templates/` | `map-template.md`, `lesson-template.md` |
| `Archive/` | Retired notes |

`Dashboard.base` at the root shows lessons by status, due for review, and planned.

## Skills

This vault is set up. Don't run setup again.

| Skill | Reads | Writes |
|---|---|---|
| `map-topic` | Maps, lessons | Map note, new lesson notes |
| `clarify-goal` | | Map note `## Goal` |
| `check-level` | Lessons | Lesson `## Level checks` |
| `teach-me` | `### My attempt` | Lesson cycles, status, map `## Outcomes` |
| `ask-obsidian` | Everything | Nothing |

`map-topic` runs the pipeline: `clarify-goal` → draft graph → `check-level` → final map. Then `teach-me` teaches.

## Map note

- `## Goal`
  - **Now**: the reachable goal task.
  - **Long-term**: the original goal.
  - **Path**: the milestones between them, with the current one marked.
- `## Map`: the Mermaid graph. Use rounded nodes and give each a class: `solid`, `shaky`, `next` (ready next) or `notyet`, as in `A(Power rule):::solid`. Node labels match lesson note titles.
  - `### Lessons`: a wikilink to every node. Mermaid nodes aren't links.
  - `### Facts (any order)`: the side list of facts.
- `## Outcomes`: a table of Outcome and Status (`not yet` or `met YYYY-MM-DD`).

## Lesson note

| Property | Values |
|---|---|
| `topic` | Links to map notes |
| `kind` | `procedure`, `principle`, `concept`, `structure` or `facts` |
| `prerequisites` | Links to lesson notes |
| `status` | `planned` → `learning` → `review` → `solid` |
| `last_reviewed`, `next_review` | `YYYY-MM-DD` |
| `sources` | Links to notes in `Sources/` |

Status moves to `learning` when cycle 1 starts, to `review` when the outcome is achieved, and to `solid` when the owner confirms after a review.

Body:

- `## In my own words`
- `## Level checks`: dated entries from check-level.
- `## Cycle N · YYYY-MM-DD`: appended one at a time, only when that cycle happens.
  - `### Explanation`
  - `### Activity`: one activity, with the answer in a collapsed `> [!success]- Answer` callout.
  - `### My attempt`
  - `### Analysis`

## Rules

1. Never write in `## In my own words` or `### My attempt`. Those belong to the owner.
2. Set `solid`, or mark an outcome met, only after the owner confirms.
3. Never delete notes. Move them to `Archive/`.
4. Search before creating a note, and reuse existing ones.
5. Append only. Never rewrite earlier cycles or level checks.
6. Change only what the task needs.

## Review

For each due note, have the owner redo the activity without looking. If they pass, schedule the next review further out: 3 days, then 1 week, 1 month, 3 months. If they fail, go back to 3 days.
