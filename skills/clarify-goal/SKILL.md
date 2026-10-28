---
name: clarify-goal
description: Turn a vague goal into concrete performances, then check whether it's too far for the learner and lower it to a reachable goal just above their level. Use when someone brings a fuzzy goal ("get better at X", "understand Y"), asks what a boss, client or student really wants, asks whether a goal is realistic or too hard, or when map-topic needs a concrete goal.
license: MIT
---

# Clarify goal

Based on Mager's goal analysis and Vygotsky's zone of proximal development.

Ask in one direction per message. Finish step 1 before giving the step 2 task.

## 1. Clarify (only if the goal is fuzzy)

Ask one question at a time:

1. "What would you see someone doing if they had achieved this?"
2. If an answer is still vague ("be confident"), ask the same question about it, or ask "how much, how often, by when?"
3. Write each answer as an observable performance.
4. Confirm: "If all of these happen, is the goal achieved?" A "yes, but…" points to a missing performance.

## 2. Check the distance (always)

Have the learner attempt the goal task. If they get stuck, give one hint, the smallest that could work (where to look, what it resembles, which method to use). Never give a second.

| Result | Meaning | Action |
|---|---|---|
| Succeeds with no hint | Already there | Raise the goal one step |
| Succeeds after the hint | Just above | Keep it |
| Still stuck after the hint | Too far | Lower it |

To lower the goal, ask "What must they already be able to do to learn this?", take the most central answer as the new goal, and probe again. Repeat until a goal lands at "succeeds after the hint".

Keep the original as the **long-term goal**. Tell the learner it's the destination and this is the first stop, not a judgment.

## Output

- **Reachable goal**: one concrete, testable task.
- **Long-term goal** and the milestones between them, if the goal was lowered.

## With a learning vault

If the user has a learning vault (a folder whose root `AGENTS.md` starts with `# Learning vault rules`), follow its rules and hand the result to `map-topic`, which writes it in the map note's `## Goal`: **Now** (the reachable goal), **Long-term**, and **Path**. Don't create the map note yourself.
