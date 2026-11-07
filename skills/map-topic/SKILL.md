---
name: map-topic
description: Build a prerequisite map for a topic someone wants to learn, fitted to what they already know. Use when the user asks what to learn first, the prerequisites of a subject, a learning path or roadmap, or feels lost and doesn't know where to start. This skill runs the learning pipeline.
license: MIT
---

# Map topic

With saved memory, follow its root `AGENTS.md` once. Deliberate mapping is for a requested roadmap; don't run this pipeline for every small lesson.

Based on Gagné's learning hierarchies.

Apply `understand-me` when installed. Research uncertain or changeable facts only; reuse checked sources.

## Pipeline

This skill runs the pipeline:

1. **Goal**: run clarify-goal and build for the reachable goal it returns.
2. **Draft**: build a rough graph. Don't show it yet.
3. **Check**: run check-level against the draft.
4. **Map**: finish the graph, fitted to the level check, and give the learner the big picture.
5. **Teach**: offer to start teach-me on the ready-next nodes; explore-next, if installed, can choose among eligible nodes with a reason.

Each step is its own message: never put goal questions and level-check tasks in the same one.

If the user skips the level check, build from what they say they know.

## Building the graph

- Start from the goal task and ask, "What must someone already be able to do to learn this?" Each answer becomes a node one level down. Repeat until you reach what the learner already knows.
- Phrase nodes as abilities ("solve a 2×2 linear system"), not topics ("linear algebra").
- Put isolated facts in a side list. They have no prerequisites.
- Record AND requirements and explicit OR groups using stable capability IDs, as the shared contract defines. Check unknown references and hard cycles before giving a study order.

## The map

The database graph is memory, not the learner's reading. Keep a requested map under about 20 capabilities. Store stable IDs and prerequisite groups, not Mermaid source. Map classes (**solid**, **shaky**, **ready next**, **not yet**) and the frontier are derived; Mermaid is generated only on export. Choose one study order starting at ready-next capabilities.

## Tell the learner

Talk it through like a teacher: what they already have, where to start, roughly what comes after, and, if the goal was lowered, how the path reaches the long-term goal. Name a few nodes in passing. Don't list them all or show statuses, arrows or code.

## With saved memory

Search once for reusable capability IDs. Batch topics, new capabilities (default planned), topic membership, outcomes and prerequisite groups/members in one `apply`. Every group is required; any member satisfies it. The helper rejects unknown references, empty groups and hard cycles before committing. Reuse check-level's evidence rather than writing it again. Do not regenerate Markdown or refresh the personal summary. Without memory, keep a small plan in the chat context.
