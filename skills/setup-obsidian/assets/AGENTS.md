# Learning vault rules

Instructions for AI agents working in this vault. Claude Code reads them through `CLAUDE.md`, which imports this file.

Each topic has a **map note** that holds its dependency graph. Each node in the graph has a **lesson note** that grows one teaching cycle at a time. Each test is a **test note**, and the notes in `Tests/` are the history.

## Folders

| Folder | Contents |
|---|---|
| `Maps/` | One map note per topic |
| `Lessons/` | One lesson note per graph node |
| `Tests/` | One test note per test: questions, answers and results |
| `Sources/` | One note per source |
| `Templates/` | `map-template.md`, `lesson-template.md`, `test-template.md` |
| `Archive/` | Retired notes |

`Dashboard.base` at the root shows lessons by status, due for review, and planned.

## Skills

This vault is set up. Don't run setup again.

| Skill | Reads | Writes |
|---|---|---|
| `map-topic` | Maps, lessons | Map note, new lesson notes |
| `clarify-goal` | | Map note `## Goal` |
| `check-level` | Lessons | Lesson `## Level checks` |
| `teach-me` | `### My attempt` | Lesson cycles, `### My attempt` (from chat), status, map `## Outcomes` |
| `test-me` | Lessons, maps, `Tests/` | Test notes, lesson status and review dates, map classes |
| `ask-obsidian` | Everything | Nothing |

`map-topic` runs the pipeline: `clarify-goal` → draft graph → `check-level` → final map. Then `teach-me` teaches, and `test-me` tests what was taught.

## Map note

- `## Goal`
  - **Now**: the reachable goal task.
  - **Long-term**: the original goal.
  - **Path**: the milestones between them, with the current one marked.
- `## Map`: the Mermaid graph. Use rounded nodes and give each a class: `solid`, `shaky`, `next` (ready next) or `notyet`, as in `A(Power rule):::solid`. Node labels match lesson note titles.
  - `### Lessons`: a wikilink to every node. Mermaid nodes aren't links.
  - `### Facts (any order)`: the side list of facts.
- `## Outcomes`: a table of Outcome and Status (`not yet` or `met YYYY-MM-DD`). `teach-me` sets a row to met in the same turn it judges the outcome achieved, and adds the row if missing.

## Lesson note

| Property | Values |
|---|---|
| `topic` | Links to map notes |
| `kind` | `procedure`, `principle`, `concept`, `structure` or `facts` |
| `prerequisites` | Links to lesson notes |
| `status` | `planned` → `learning` → `review` → `solid` |
| `last_reviewed`, `next_review` | `YYYY-MM-DD` |
| `sources` | Links to notes in `Sources/` |

Status moves on its own, with no confirmation: to `learning` when cycle 1 starts, to `review` when the outcome is achieved, and to `solid` when the owner passes a review. A failed review goes back to `learning`.

After any status change, regenerate the map's classes from the lesson statuses. Never ask, and never leave the graph stale:

| Lesson status | Class |
|---|---|
| `solid` | `solid` |
| `review` | `shaky` |
| `planned` or `learning`, every prerequisite `solid` or `review` | `next` |
| `planned` or `learning`, otherwise | `notyet` |

Body:

- `## In my own words`
- `## Level checks`: dated entries from check-level.
- `## Cycle N · YYYY-MM-DD`: appended one at a time, only when that cycle happens.
  - `### Explanation`
  - `### Activity`: one activity, with the answer in a collapsed `> [!success]- Answer` callout.
  - `### My attempt`
  - `### Analysis`

## Test note

Named `<Topic> test YYYY-MM-DD`, in `Tests/`.

| Property | Values |
|---|---|
| `topic` | Links to map notes |
| `lessons` | Links to the lesson notes tested |
| `date` | `YYYY-MM-DD` |

Body:

- `## Blueprint`: nodes by cognitive verb, with the planned questions.
- `## Questions`: each with its marks, and the key in a collapsed `> [!success]- Answer` callout.
- `## My answers`
- `## Results`: marks per node, failure types, feedback, and the status changes made.

## Rules

1. Never write in `## In my own words`. It belongs to the owner. Write in `### My attempt` or `## My answers` only to save what the owner shared in chat, verbatim.
2. Update statuses, map classes and outcomes yourself as the evidence arrives. Don't ask the owner to confirm.
3. Never delete notes. Move them to `Archive/`.
4. Search before creating a note, and reuse existing ones.
5. Append only. Never rewrite earlier cycles, level checks or tests.
6. Change only what the task needs.
7. Ask in one direction per message. Several questions for the same purpose are fine. Never mix purposes, such as goal questions with level-check tasks, or an open question with a next-lesson offer. Wait for the answer before starting the next direction.

## Review

Run reviews with `test-me`. For each due note, test the owner without looking. If they pass, set `solid` and schedule the next review further out: 3 days, then 1 week, 1 month, 3 months. If they fail, set `learning` and go back to 3 days.
