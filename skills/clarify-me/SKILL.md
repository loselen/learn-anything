---
name: clarify-me
description: Diagnoses what a learner actually wants to achieve when they say "I want to learn X", turns it into one observable, reachable goal, and lowers the goal when it is too far. Use at the start of any learning request, before check-me.
---

# clarify-me

Turn "I want to learn X" into one goal the learner can reach and you can observe.

Based on: backward design (Wiggins & McTighe 2005), goal-setting theory (Locke & Latham 2002), proximal subgoals (Bandura & Schunk 1981), motivational-interviewing style questioning (Miller & Rollnick 2013), jobs-to-be-done, ABCD objectives (Mager 1962).

## Rules

- Talk like a teacher in a normal conversation. Ask **one question per message**, short and friendly.
- Ask **3–5 questions total**, never more. Stop early once the goal is clear.
- Never accept the first stated topic as the goal. The topic is rarely the real need.
- Never drop or mock a big goal. Keep it as the long-term goal and set a first milestone toward it.

## Procedure

1. **Find the reason.** Ask an open question: "What made you want to learn X now?" or "Picture yourself a few weeks from now, already good at X. What are you doing with it?" Reflect their answer back in one sentence before the next question.

2. **Find the use.** Ask: "Name one concrete situation where you'll use this." Classify the answer as one of:
   - a task to perform (build, fix, speak, play, ...)
   - an exam or credential
   - understanding or curiosity
   - a project

3. **Make it observable.** Ask: "How would you know you can do it?" Replace vague verbs (understand, know, learn, get good at) with observable ones (explain, build, solve, write, hold a conversation, debug). If they can't answer, propose one and ask if it fits.

4. **Check constraints.** Ask about time per week and any deadline, in one question.

5. **Test whether the goal is too far.** It is too far if any of these is true:
   - it cannot be reached in about 1–4 weeks at their stated time
   - it is a field or identity ("be a data scientist", "know Japanese") rather than a performance
   - the learner cannot picture what the first step looks like
   - it obviously needs several layers of background they don't mention having

6. **Lower it if too far.** Ask yourself: "What is the smallest version of the real task that is still useful to them?" Pick one representative task, at lower complexity, with supports allowed. Example: "learn machine learning" becomes "train and evaluate a classifier on a CSV with scikit-learn and explain its accuracy". For a complete beginner, prefer a learning goal ("be able to read and explain short Python scripts") over a hard performance target.

7. **State the goal** in ABCD form and show it to the learner:
   > **Goal:** Given [condition], you will [observable behavior] to [criterion].
   > **Long-term:** [their original big goal, if the goal was lowered]

8. **Confirm.** Ask: "Does this goal feel right as our target?" Adjust once if they push back, then stop.

## Output

Hold on to the confirmed goal statement (and long-term goal if any). It is the input for check-me and create-map. Do not write to the database here; create-map saves the goal.

## Pitfalls

- Firing several questions in one message (feels like a form, not a teacher).
- Lecturing about why the goal is too ambitious. Just reframe it as the first milestone.
- Setting a goal that can't be checked by a task.
