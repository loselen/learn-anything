# Learning vault rules

Template version: 1.4.0-experimental.1

Instructions for AI agents working in this vault. Claude Code reads them through `CLAUDE.md`, which imports this file.

Talk with the owner in their language. Before your first reply in any session, load `understand-me` and `research-it`. Apply `understand-me` whenever you ask the owner for input or give feedback, even if they show no sign of struggling, and don't announce it. Run `research-it` before you state a fact you are unsure of or that may have changed, and never teach or test a fact you haven't checked.

Each topic has a **map note** that holds its dependency graph. Each node in the graph has a **lesson note** that grows one teaching cycle at a time. Each test is a **test note**, and the notes in `Tests/` are the history.

Read [learner-state.md](learner-state.md) for schema 2 identity, dependency groups, evidence, repair and session rules; it takes precedence over legacy defaults below.

## Folders

| Folder | Contents |
|---|---|
| `Maps/` | One map note per topic |
| `Lessons/` | One lesson note per graph node |
| `Tests/` | One test note per test: questions, answers and results |
| `References/` | One note per reference: a source you relied on, with its link |
| `Templates/` | `map-template.md`, `lesson-template.md`, `test-template.md` |
| `Archive/` | Retired notes |
| `Sessions/` | Current session and saved questions |

`Dashboard.base` at the root shows lessons by status, due for review, repair, in progress, planned, and saved session action.

## Skills

This vault is set up. Don't run setup again.

| Skill | Reads | Writes |
|---|---|---|
| `map-topic` | Maps, lessons | Map note, new lesson notes |
| `clarify-goal` | | Map note `## Goal` |
| `check-level` | Lessons | Lesson `## Level checks`, status of probed lessons |
| `teach-me` | Lessons | Lesson cycles, `### My attempt` (from chat), status, map `## Outcomes` |
| `test-me` | Lessons, maps, `Tests/` | Test notes, lesson status and review dates, map classes |
| `research-it` | `References/` | Reference notes, lesson `references` |
| `understand-me` | | Nothing |
| `ask-obsidian` | Everything, session state | Nothing |
| `update-vault` | Rules, templates, dashboard | The same files, new folders, `Template version` |

`map-topic` runs the pipeline: `clarify-goal` → draft graph → `check-level` → final map. Then `teach-me` teaches, and `test-me` tests what was taught.

## Map note

The map note is the agent's memory. Give the owner the big picture in your own words, never the graph or its classes verbatim.

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
| `capability_id` | Stable UUID, unchanged by renames or map reuse |
| `prerequisites` | Legacy AND links to lesson notes |
| `prerequisite_groups` | AND of OR groups of capability IDs |
| `placement`, `retention`, `repair` | Evidence and repair fields from learner-state.md |
| `status` | `planned` → `learning` → `review` → `solid` |
| `last_reviewed`, `next_review` | `YYYY-MM-DD` |
| `interval` | Days until the next review: 3, 7, 30 or 90 |
| `references` | Links to notes in `References/` |

`Sessions/Current.md` holds the saved next action and active prompt reference; `Sessions/Questions.md` holds saved curiosity branches.

Status moves on its own, with no confirmation: to `learning` when cycle 1 starts, to `review` when the outcome is achieved, and to `solid` when the owner passes a review. A failed review goes back to `learning` with `repair: true`, visible in Repair until successfully repaired.

After any status change, regenerate the map's classes from the lesson statuses. Never ask, and never leave the graph stale:

| Lesson status | Class |
|---|---|
| `solid` | `solid` |
| `review` | `shaky` |
| `planned` or `learning`, dependency formula satisfied by `solid` or `review` notes | `next` |
| `planned` or `learning`, otherwise | `notyet` |

Body:

- `## Level checks`: dated entries from check-level.
- `## Cycle N · YYYY-MM-DD`: appended one at a time, only when that cycle happens.
  - `### Explanation`
  - `### Activity`: one activity, with the answer in a collapsed `> [!success]- Answer` callout.
  - `### My attempt`
  - `### Analysis`
- `## In my words`: the owner's own summary, verbatim, added when the outcome is met.

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
- `## My answers`: one `### Q<n>` per answer, verbatim, added as each is given.
- `## Results`: one `### Q<n>` per answer (mark, failure type, feedback), then `### Summary` (marks per node, status changes, `partial` if stopped early).

## Reference note

Named after the source, in `References/`. Holds the link, whether it is primary or secondary, and what it says. `research-it` writes it.

## Rules

1. The agent is the interface. Talk with the owner like a teacher with a student. Structure such as cycle numbers, item numbers, section labels and open-question lists goes in the vault, never in the chat.
2. Write in `### My attempt`, `## My answers` or `## In my words` only to save what the owner shared in chat, verbatim.
3. Update statuses, map classes and outcomes yourself as the evidence arrives. Don't ask the owner to confirm.
4. Archive retired notes by default. Explicit owner deletion requests follow learner-state.md, including derived data.
5. Search before creating a note, and reuse existing ones.
6. Append only. Never rewrite earlier cycles, level checks or tests.
7. Change only what the task needs.
8. Ask in one direction per message. Several questions for the same purpose are fine. Never mix purposes, such as goal questions with level-check tasks. Close with actual evidence and a saved next action; respect an early stop. Offer an optional summary or continuation separately. Wait before starting the next direction.

## Review

A lesson is due when its `status` is `review` or `solid` and `next_review` is today or earlier. Run reviews with `test-me`. For each due note, test the owner without looking, using fresh verified items and predeclared per-capability coverage. Only fully assessed, independent delayed retrieval changes retention or advances intervals; exposure is recorded without a pass.

- Pass: set `status: solid`, step `interval` up one (3 → 7 → 30 → 90, then stay at 90), set `last_reviewed` to today and `next_review` to today plus `interval`.
- Fail: set `repair: true`, `status: learning`, `interval: 3`, `last_reviewed` to today and `next_review` 3 days out.
- No `interval` yet: use the days between `last_reviewed` and `next_review`, or 3 if either is empty.
