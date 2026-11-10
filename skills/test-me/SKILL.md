---
name: test-me
description: Designs a short activity that checks one learning outcome, evaluates the learner's attempts with a rubric, gives targeted feedback and hints, records every attempt in SQLite, and decides whether the outcome is met. Use at the end of every teach-me step.
---

# test-me

Check one outcome with a task that requires exactly the ability the outcome names, then act on what the answer shows.

Based on: formative assessment (Black & Wiliam 1998), hinge questions (Wiliam 2011), constructive alignment (Biggs 1996), production over recognition (McDaniel et al. 2007), generative tasks (Fiorella & Mayer 2016), rubrics (Jonsson & Svingby 2007), elaborated feedback (Shute 2008; Hattie & Timperley 2007), contingent scaffolding and hint ladders (Wood et al. 1976; Aleven et al. 2016), bug analysis (Brown & Burton 1978), mastery criteria (Kelly et al. 2015).

> **Database:** run the bundled script from the learner's project root (the folder the chat started in); it keeps data in `./.learn/learn.db`. `${CLAUDE_SKILL_DIR}` is this skill's folder; Claude Code fills it in, and other agents should use the path of the folder containing this SKILL.md.

## 1. Design the activity

Match the task to the outcome's verb: if it says "explain", ask for an explanation; "solve" or "write", an unseen problem with different surface details from the lesson; "debug", flawed work to fix.

Plan **2–3 items**, given **one per message**:
1. **Hinge item:** a multiple-choice question or "predict what happens", where every wrong option matches a specific misconception. The right answer must be hard to guess.
2. **Production item:** the learner produces the answer themselves on a new problem (near transfer).
3. *(optional)* **Generative item:** explain why, find the error, or apply it to a slightly different situation.

Never reuse an item from the lesson or from an earlier attempt.

## 2. Evaluate each answer

1. Ask "How sure are you: 1 guess, 2 fairly sure, 3 certain?" right after they answer.
2. Judge against a 2–4 criterion rubric taken from the outcome's standard (e.g. correct result, valid reasoning, right terms). Verdict: `correct`, `partial`, or `incorrect`.
3. If wrong, classify the error: **slip**, **gap** (missing prerequisite), or **misconception** (a consistent wrong rule).

## 3. Give feedback

Keep it short, about the work, and answer three questions:
- **What worked:** one specific thing, quoting their answer.
- **What's off:** the single most important issue, at the level of their method, not just the final answer.
- **Next:** one concrete action.

If they were confident and wrong, say so plainly ("you were sure, and here's why it fails"); those corrections stick best.

On a wrong answer, give one hint rung per new try, never jumping to the solution:
1. Pointing hint: "look at step 2 again"
2. Principle prompt: "what rule applies when ...?"
3. A partial worked step
4. Full solution, then a **new parallel item** they must solve with no help

## 4. Record every attempt

After evaluating each answer, save it (one row per item attempt):

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/db.py" attempt '{"outcome_id": 7, "activity": "<the item>", "answer": "<learner answer>", "verdict": "correct", "feedback": "<short: error type, hint level used, confidence, what you told them>"}'
```

Use a heredoc on stdin if the text contains awkward quotes.

## 5. Decide

The outcome is **met** when all of these hold:
- the last **3 items in a row** were correct
- at least one of them was a production or transfer item
- none of them needed hint rung 4
- the learner gave at least one correct explanation with confidence 2 or 3

Then mark it:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/db.py" met '{"outcome_id": 7}'
```

This saves the date the outcome was met. The result says how many outcomes are left in the node. Hand back to teach-me.

If it is **not met**, choose a route and hand back to teach-me:
- slip → one more new item
- misconception → reteach by making the conflict visible, then a new activity
- gap → teach or add the missing prerequisite (create-map)
- 3+ failed activities on the same outcome → the outcome is too big; split the step and teach smaller

## Pitfalls

- Recognition questions when the outcome asks for production.
- Multiple-choice options that reveal nothing about how the learner thinks.
- Declaring mastery after one correct answer.
- Reusing items, so the learner remembers instead of thinks.
- Giving the answer at the first mistake.
- Listing every error at once. Fix the most important one first.
