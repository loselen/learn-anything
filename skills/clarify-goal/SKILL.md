---
name: clarify-goal
description: Turn a vague goal into concrete performances, then check whether it's too far for the learner and lower it to a reachable goal just above their level. Use when someone brings a fuzzy goal ("get better at X", "understand Y"), asks what a boss, client or student really wants, asks whether a goal is realistic or too hard, or when map-topic needs a concrete goal.
license: MIT
---

# Clarify goal

Based on Mager's goal analysis and Vygotsky's zone of proximal development.

Load `understand-me` and `research-it` first if you haven't this session and they are installed. If not, still open easy, keep each ask small, aim feedback at the work, and check facts you are unsure of.

Ask in one direction per message. Finish step 1 before giving the step 2 task.

Use `make-activity` when installed to design every learner activity, including retries and transfer checks. Pass the objective, knowledge kind, level and purpose; keep this skill's pacing, hints, scoring and saving rules. If unavailable, make one small task requiring the target performance, with observable evidence and a checked key; keep the key back until the attempt.

## 1. Clarify (only if the goal is fuzzy)

Ask one question at a time:

1. "What would you see someone doing if they had achieved this?" Offer 2 or 3 example answers to react to, since a novice may lack the words.
2. If an answer is still vague ("be confident"), ask the same question about it, or ask "how much, how often, by when?"
3. Write each answer as an observable performance.
4. Confirm: "If all of these happen, is the goal achieved?" A "yes, but…" points to a missing performance.

## 2. Check the distance (always)

Say first that this shows where to start and isn't a grade, and that the last task may feel hard. Open with an easier task on the way to the goal, one they will very likely get. If they get it, give the goal task. If they miss it, treat the goal as too far and skip the goal task.

On the goal task, give at most one hint, the smallest that could work (where to look, what it resembles, or which method to use). If they still fail after it, count it as stuck.

| Result | Meaning | Action |
|---|---|---|
| Succeeds with no hint | Already there | Raise the goal one step |
| Succeeds after the hint | Just above | Keep it |
| Still stuck after the hint | Too far | Lower it |

To lower the goal, ask "What must they already be able to do to learn this?", take the most central answer as the new goal, and probe again. Repeat until a goal succeeds after the hint.

Keep the original as the **long-term goal**. Tell the learner it's the destination and this is the first stop, not a judgment.

## Output

- **Reachable goal**: one concrete, testable task.
- **Long-term goal** and the milestones between them, if the goal was lowered.

## With a learning vault

If the user has a learning vault (a folder whose root `AGENTS.md` starts with `# Learning vault rules`), follow its rules and hand the result to `map-topic`, which writes it in the map note's `## Goal`: **Now** (the reachable goal), **Long-term**, and **Path**. Don't create the map note yourself.
