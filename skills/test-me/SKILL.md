---
name: test-me
description: Test the learner with exam-style questions on what they're learning, to show what is solid and strengthen what they remember. Use when they ask to be tested, quizzed or examined, want practice questions or a review of a topic or lesson, or when someone needs an exam or quiz written for a student. Asks fresh questions one at a time, marks each with feedback, and plans the retest. For placement before learning, use check-level.
license: MIT
---

# Test me

With saved memory, follow its root `AGENTS.md` once. Keep explicit difficulty preferences and the review ladder; personalization analysis is opt-in, not part of a normal test.

Based on the revised Bloom's taxonomy (Krathwohl), test-enhanced learning (Roediger & Karpicke; Kang, McDermott & Roediger) and formative assessment (Black & Wiliam). Sources and how much of each was read: `references/sources.md`.

Apply `understand-me` when installed. Research only uncertain, disputed or changeable facts; reuse checked sources. Alone, open easy and keep feedback about the work.

Use `make-activity` inline for questions and rechecks, with the objective/kind/level/purpose. Keep coverage, pacing, scoring and saving here. Alone, use a small task with a checked key.

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
- Talk like a teacher with a student. Keep blueprints, keys and storage structure out of the learner-facing question.

## Scope

Find the subject, the learner's level, what the lessons covered, the time available and who marks. State assumptions for what you don't know and start. Ask one short question at most. Size the test to the time they have.

By default, test what is due first (`status` `review` or `solid`, `next_review` today or earlier), then what is in progress.

## Write the test

1. **Skills as verb plus topic.** Use remember, understand, apply, analyze, evaluate, create. Fractions: *apply* = compute 2/3 + 3/4; *analyze* = find the error in 2/3 + 3/4 = 5/7.
2. **Blueprint.** A grid with one row per node (with its kind: procedure, principle, concept, structure or facts) and the six verbs across. Place each question in a cell. Fill a cell only if the lessons aimed there. Test items are often mostly recall, so check your draft for that.
3. **Make them produce answers.** Prefer short answer, worked problems and explain-in-your-own-words. Use multiple choice only for quick checks, and return the correct answers. One skill per question, plain wording, no trick questions. Include a few items on material they only half know.
4. **Key.** For each question: the model answer and accepted variants, partial credit (1, ½, 0), the common wrong answers and what each shows, and a one- or two-sentence explanation.

## Check every answer key

Check each new key once: execute code, independently check a calculation, or research an uncertain fact. Reuse that verification unless the item changes or is disputed. Save its method/version. If learner material conflicts, investigate and leave progress unchanged. Unchecked keys use `verified: false`; check before rejecting a different answer. Don't research settled facts again.

## Mark and review

- Mark each answer in the next message: one or two sentences on what worked, what didn't and why. If it was correct, ask the next question in the same message.
- On a miss, ask them to explain the idea back in their own words before the next question. Then ask the next question.
- After the last question, give the results: open with what they can now do, then the nodes to revisit, then when the retest is.
- Score per node, not one total. A node passes on full marks, or one slip fixed independently on a fresh, predeclared conditional recheck. Link rechecks in the blueprint as the API describes; don't add coverage after answers. Classify misses as check-level does.
- "Yes, I get it" tells you little. The explain-back on each miss is the check.
- If the learner stops early, score only the nodes whose questions were all answered. Leave the rest unchanged.
- Use the shared 3 → 7 → 30 → 90 day ladder for delayed review; repair hands off to teach-me first. Immediate tests are practice; due delayed retrieval measures retention. Always use fresh items.
- Let the node scores set what `teach-me` teaches next.

## Output

- **In chat:** one question per message, then per-question feedback, then the results.
- **Kept back:** blueprint, remaining questions, keys and retest plan. With saved memory they are database records; ordinary context omits keys. Without memory keep keys back until answered or disclosure is requested. Record disclosure as exposure.

Reply in chat. Make a file only if asked, in the format they name.

## Limits

Most studies used college students and fact-heavy material, so they say little about problem solving or younger learners. The six verbs overlap, so use the grid for coverage, not ranking.

## With saved memory

Read one targeted context and earlier units to avoid repeats. A short due review can be one unit per capability; don't construct an exam for a quick review. For a multi-item test, batch `tests`, checked `units` and ordered `test_items` before the first answer; coverage then locks.

Save each verbatim attempt and assessment with one `turn`/`apply`, alongside the session action. On finish/early stop include `finalize_tests: [ID]`: only complete eligible coverage changes that capability, and missing/disputed/supported coverage stays unchanged. Use `delayed` only for due retrieval; otherwise `practice`. Failed due review enters repair; successful transfer through teach-me clears it. No status edits, map rewrites, exports or personal summary refresh.
