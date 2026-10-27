---
name: test-me
description: Test the learner with exam-style questions on what they're learning, to show what is solid and strengthen what they remember. Use when they ask to be tested, quizzed or examined, want practice questions or a review of a topic or lesson, or when someone needs an exam or quiz written for a student. Asks fresh questions and waits, marks with feedback, and plans the retest. For placement before learning, use check-level.
license: MIT
---

# Test me

Based on the revised Bloom's taxonomy (Krathwohl), test-enhanced learning (Roediger & Karpicke; Kang, McDermott & Roediger) and formative assessment (Black & Wiliam). Sources and how much of each was read: `references/sources.md`.

```
pick scope → blueprint → questions → wait for "done" → mark and give feedback → retest later
```

## Rules

- Test only what has been taught. Never ask about a `planned` lesson.
- Every question is fresh: not a lesson activity, not an earlier test's question.
- Stop after the questions. Give no answers and no hints until the learner says done. A blank or a guess is useful data.
- Ask in one direction per message. Don't mix a feedback question with a next-lesson offer.

## Scope

Find the subject, the learner's level, what the lessons covered, the time available and who marks. State assumptions for what you don't know and start. Ask one short question at most. Size the test to the time they have.

By default, test what is due for review first, then what is in progress.

## Write the test

1. **Skills as verb plus topic.** Use remember, understand, apply, analyze, evaluate, create. Fractions: *apply* = compute 2/3 + 3/4; *analyze* = find the error in 2/3 + 3/4 = 5/7.
2. **Blueprint.** A grid with one row per node (with its kind: procedure, principle, concept, structure or facts) and the six verbs across. Place each question in a cell. Fill a cell only if the lessons aimed there. Test items are often mostly recall, so check your draft for that.
3. **Make them produce answers.** Prefer short answer, worked problems and explain-in-your-own-words. Use multiple choice only for quick checks, and return the correct answers. One skill per question, plain wording, no trick questions. Include a few items on material they only half know.
4. **Key.** For each question: the model answer and accepted variants, partial credit (1, ½, 0), the common wrong answers and what each shows, and a one- or two-sentence explanation.

## Mark and review

- Mark in the next message after done, with feedback on each question. Open with what they can now do.
- Score per node, not one total. A node passes on full marks, or on one slip that a recheck fixes. Classify each miss as check-level does: missing prerequisite, bug, slip or no transfer.
- Ask them to explain each missed question back in their own words. "Yes, I get it" tells you little.
- Retest the missed and shaky nodes two days to a week later, with fresh items. The first test is practice. The retest is the measure.
- Let the node scores set what `teach-me` teaches next.

## Output

- **Test:** instructions, time, questions, marks per question.
- **Key:** blueprint, answers and retest plan. Keep it until they say done.

Reply in chat. Make a file only if asked, in the format they name.

## Limits

Most studies used college students and fact-heavy material, so they say little about problem solving or younger learners. The six verbs overlap, so use the grid for coverage, not ranking.

## With a learning vault

If the user has a learning vault (a folder whose root `AGENTS.md` starts with `# Learning vault rules`), follow its rules and save the test as it happens:

- Search `Tests/` for earlier tests on the same lessons, and write new questions.
- Create the test note in `Tests/` from the test template, with the blueprint and the questions. Put each key in a collapsed `> [!success]- Answer` callout.
- When the learner shares their answers in chat, copy them verbatim under `## My answers` before marking.
- Append the marks, failure types and feedback under `## Results`.
- Update lessons in the same turn as the results, without asking. Only `review` and `solid` lessons change:
  - Pass: set `status: solid`, `last_reviewed` to today and `next_review` by the vault's review schedule.
  - Fail: set `status: learning` and `next_review` 3 days out.
  - A lesson still `learning` keeps its status. The marks stay in the test note.
- Regenerate the map's node classes as the vault rules say.
