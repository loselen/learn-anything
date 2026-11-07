---
name: check-level
description: Find what someone can and can't do in a topic, and why each failure happens. Use for placement or diagnostic tests, "what should I learn next", finding gaps or misconceptions, or when someone keeps getting something wrong. Normally called by map-topic.
license: MIT
---

# Check level

With saved memory, follow its root `AGENTS.md`; load it once, not per item.

Based on knowledge space theory (Doignon & Falmagne), think-aloud research (Ericsson & Simon) and procedural bug research (Brown & Burton).

Apply `understand-me` when installed. Research only uncertain, disputed or changeable facts; reuse checked items. Alone, open easy and keep feedback about the work.

Use `make-activity` inline for probes and retries, with the objective/kind/level/purpose. Keep pacing, hints and saving here. Alone, give one small task with a checked key.

## Probe

- Open with an easy item, one the learner can likely pass, so the check starts with a win. Never open with the hardest item.
- Climb toward the goal on the graph, one step harder each time. After a pass, spot-check one prerequisite only if the next item is a stretch. After a fail, move one level down and probe again.
- Keep it a conversation: don't announce item numbers or node names, and show the report only as a plain summary.
- Keep the tone light: say it's a check of the material, not a test of them, and don't stack more than two fails in a row. Follow a fail with an item they can pass.
- Give at most one hint per item. If they still fail after it, count it as a fail.
- Give two items per node, with different surfaces, before concluding.
- Use make-activity to match the kind. Alone: procedure → do; principle → predict; concept → classify; structure → label; facts → recall.

- Ask the learner to "keep saying what you're thinking." Don't ask them to explain their reasoning during the task, because that changes how they think. Ask why afterwards.

## Classify each failure

| Type | Signal | Fix |
|---|---|---|
| Missing prerequisite | Also fails a node below | Teach that node first |
| Bug | Same wrong move every time | Name and correct the rule they follow |
| Slip | Inconsistent, and fixed on a recheck | Nothing to teach |
| Needs support | Succeeds with a hint | Note which hint worked |
| No transfer | Passes only the familiar form | Vary the practice |

## Report

- **Solid**: passed a delayed independent review; placement alone is provisional. Placement successes are **shaky** until reviewed.
- **Shaky**: passed, but only recently learned (`status: review` in saved memory). Review these first.
- **Ready next**: failed, with its dependency formula satisfied by solid or shaky capabilities.
- **Not yet**: everything else.
- Each failure with its type, plus any missing prerequisites found.

Hand the report back to map-topic.

## With saved memory

Reuse capabilities by ID. Save each placement unit, verbatim attempt and assessment in one `turn`/`apply`; record failure type and support. The helper needs two distinct independent checked successes to establish placement (`review`, due in 3 days), never retained mastery. Existing longer schedules stay unchanged. Placement failures identify gaps; only fully assessed due retrieval changes an existing review schedule. Hand the evidence IDs to map-topic, not another copy of the prose. No Markdown writes or summary refresh.
