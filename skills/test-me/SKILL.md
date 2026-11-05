---
name: test-me
description: Test the learner with exam-style questions on what they're learning, to show what is solid and strengthen what they remember. Use when they ask to be tested, quizzed or examined, want practice questions or a review of a topic or lesson, or when someone needs an exam or quiz written for a student. Asks fresh questions one at a time, marks each with feedback, and plans the retest. For placement before learning, use check-level.
license: MIT
---

# Test me

Read [the shared state contract](references/learner-state.md) before placement, evidence, scheduling or session writes. With a vault, also follow its rules. For requested personalization, use explore-next’s local measurement contract if installed; otherwise keep explicit difficulty preferences and the existing review ladder. Never change evidence to fit a recommendation.

Based on the revised Bloom's taxonomy (Krathwohl), test-enhanced learning (Roediger & Karpicke; Kang, McDermott & Roediger) and formative assessment (Black & Wiliam). Sources and how much of each was read: `references/sources.md`.

Load `understand-me` and `research-it` first if you haven't this session and they are installed. If not, still open easy, keep each ask small, aim feedback at the work, and check facts you are unsure of.

```
pick scope → blueprint → ask one question → wait for the answer → feedback → next question → results → retest later
```

## Rules

- Test only what has been taught. Never ask about a `planned` lesson.
- Every question is fresh: not a lesson activity, not an earlier test's question.
- Ask one question per message, then stop. Never show upcoming questions or keys unprompted. Honor answer requests and record disclosure as exposure, never independent retrieval.
- Give no answer and no hint before an attempt unless explicitly requested; track any support. "I don't know", a skip or a guess counts as an answer and is useful data.
- Order questions from easiest to hardest. After two misses in a row, ask the easiest remaining question next.
- Say how much is left in a few words ("two to go"), never as a numbered list.
- Ask in one direction per message. Don't mix a feedback question with a next-lesson offer.
- Talk like a teacher with a student. Don't show the blueprint, the key or note structure in chat. That belongs in the vault.

## Scope

Find the subject, the learner's level, what the lessons covered, the time available and who marks. State assumptions for what you don't know and start. Ask one short question at most. Size the test to the time they have.

By default, test what is due first (`status` `review` or `solid`, `next_review` today or earlier), then what is in progress.

## Write the test

1. **Skills as verb plus topic.** Use remember, understand, apply, analyze, evaluate, create. Fractions: *apply* = compute 2/3 + 3/4; *analyze* = find the error in 2/3 + 3/4 = 5/7.
2. **Blueprint.** A grid with one row per node (with its kind: procedure, principle, concept, structure or facts) and the six verbs across. Place each question in a cell. Fill a cell only if the lessons aimed there. Test items are often mostly recall, so check your draft for that.
3. **Make them produce answers.** Prefer short answer, worked problems and explain-in-your-own-words. Use multiple choice only for quick checks, and return the correct answers. One skill per question, plain wording, no trick questions. Include a few items on material they only half know.
4. **Key.** For each question: the model answer and accepted variants, partial credit (1, ½, 0), the common wrong answers and what each shows, and a one- or two-sentence explanation.

## Check every answer key

Before you save or use a key, check it: run code if you can execute it, solve a calculation a second way, and run facts through `research-it`. Record how the key was verified and its version. If learner material conflicts with a checked key, investigate; quarantine disputed items and leave affected state unchanged. If you can't check a key, mark it `unverified` in its callout, and re-check before marking a different answer wrong.

## Mark and review

- Mark each answer in the next message: one or two sentences on what worked, what didn't and why. If it was correct, ask the next question in the same message.
- On a miss, ask them to explain the idea back in their own words before the next question. Then ask the next question.
- After the last question, give the results: open with what they can now do, then the nodes to revisit, then when the retest is.
- Score per node, not one total. A node passes on full marks, or on one slip that a recheck fixes. Classify each miss as check-level does: missing prerequisite, bug, slip or no transfer.
- "Yes, I get it" tells you little. The explain-back on each miss is the check.
- If the learner stops early, score only the nodes whose questions were all answered. Leave the rest unchanged.
- Use the shared 3 → 7 → 30 → 90 day ladder for delayed review; repair hands off to teach-me first. Retest with fresh items. The first test is practice. The retest is the measure.
- Let the node scores set what `teach-me` teaches next.

## Output

- **In chat:** one question per message, then per-question feedback, then the results.
- **Kept back:** blueprint, the remaining questions, the key and the retest plan. With a vault, they go in the test note, with each key in a collapsed `> [!success]- Answer` callout. Without one, keep them to yourself and reveal a key after that question is answered or disclosure is requested, recording exposure.

Reply in chat. Make a file only if asked, in the format they name.

## Limits

Most studies used college students and fact-heavy material, so they say little about problem solving or younger learners. The six verbs overlap, so use the grid for coverage, not ranking.

## With a learning vault

If the user has a learning vault (a folder whose root `AGENTS.md` starts with `# Learning vault rules`), follow its rules and save the test as it happens:

- Search `Tests/` for earlier tests on the same lessons, and write new questions.
- Create the test note in `Tests/` from the test template, with the blueprint and the questions. Put each key in a collapsed `> [!success]- Answer` callout.
- After each answer, append it verbatim under `## My answers` as `### Q<n>` before marking it, then append its mark, failure type and feedback under `## Results` as `### Q<n>`.
- After the last question, append `### Summary` under `## Results`: marks per node and the status changes made. Mark the test `partial` in the summary if the learner stopped early.
- Update lessons in the same turn as the summary, without asking. Only fully assessed `review` and `solid` lessons change; repair lessons follow the shared repair contract:
  - Pass: set `status: solid`, step `interval` up and set `last_reviewed` and `next_review`, as the vault's `## Review` says.
  - Fail: set `status: learning`, `repair: true`, `interval: 3`, `last_reviewed` to today and `next_review` 3 days out.
  - Ordinary `learning` keeps its status; repair clears only after fresh independent transfer through teach-me. The marks stay in the test note.
- Regenerate the map's node classes as the vault rules say.
