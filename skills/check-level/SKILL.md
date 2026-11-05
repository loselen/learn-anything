---
name: check-level
description: Find what someone can and can't do in a topic, and why each failure happens. Use for placement or diagnostic tests, "what should I learn next", finding gaps or misconceptions, or when someone keeps getting something wrong. Normally called by map-topic.
license: MIT
---

# Check level

Based on knowledge space theory (Doignon & Falmagne), think-aloud research (Ericsson & Simon) and procedural bug research (Brown & Burton).

Load `understand-me` and `research-it` first if you haven't this session and they are installed. If not, still open easy, keep each ask small, aim feedback at the work, and check facts you are unsure of.

Use `make-activity` when installed to design every learner activity, including retries and transfer checks. Pass the objective, knowledge kind, level and purpose; keep this skill's pacing, hints, scoring and saving rules. If unavailable, make one small task requiring the target performance, with observable evidence and a checked key; keep the key back until the attempt.

## Probe

- Open with an easy item, one the learner can likely pass, so the check starts with a win. Never open with the hardest item.
- Climb toward the goal on the graph, one step harder each time. After a pass, spot-check one prerequisite only if the next item is a stretch. After a fail, move one level down and probe again.
- Keep it a conversation: don't announce item numbers or node names, and show the report only as a plain summary.
- Keep the tone light: say it's a check of the material, not a test of them, and don't stack more than two fails in a row. Follow a fail with an item they can pass.
- Give at most one hint per item. If they still fail after it, count it as a fail.
- Give two items per node, with different surfaces, before concluding.
- Use `make-activity` to match each item to its knowledge kind. Without it: procedure → do; principle → predict; concept → classify; structure → label; facts → recall.

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

- **Solid**: passed.
- **Shaky**: passed, but only recently learned. With a vault, these are lessons at `status: review`. Review these first.
- **Ready next**: failed, with every prerequisite solid or shaky.
- **Not yet**: everything else.
- Each failure with its type, plus any missing prerequisites found.

Hand the report back to map-topic.

## With a learning vault

If the user has a learning vault (a folder whose root `AGENTS.md` starts with `# Learning vault rules`), follow its rules. For each node you probed whose lesson note exists, append a dated entry to `## Level checks` (result, failure type, and the hint that worked) and set its status:

| Result | Lesson status |
|---|---|
| Passed both items with no hint | `solid`, `interval: 30`, `last_reviewed` today, `next_review` 30 days out |
| Failed a lesson that was `review` or `solid` | `learning`, `interval: 3`, `next_review` 3 days out |
| Anything else | Unchanged |

When notes don't exist yet, hand the entries and statuses to map-topic, which writes them when it creates the notes.
