# Behavior scenarios

Run each scenario in a fresh agent session with scratch SQLite learning memory (ask `Set up my learning memory` in an empty folder first). Inspect records with the memory CLI; seed old schedules only in scratch data. Record agent, model, date, and pass/fail with prompts and artifacts in the pull request. Script tests alone do not establish conversational behavior.

## 1. Test one question at a time
Setup: two capabilities with `status: review` and `next_review` yesterday.
Learner: "Test me." Then answer: a correct answer, "idk", a wrong answer, a wrong answer.
Pass: the first reply holds exactly one question and no answers. Each later reply holds feedback and at most one new question. After two misses, the next question is the easiest left. Ordered test_items, verbatim attempts and assessments are saved; fully assessed coverage is finalized.

## 2. Reviews after the first pass
Setup: one lesson with `status: solid`, `interval: 7`, `next_review` yesterday.
Learner: "What's due?" then "Test me", and answer correctly.
Pass: the capability shows in `due`. After a complete independent delayed test it has `interval: 30` and `next_review` 30 days out. No Markdown files are regenerated.

## 3. Goal check opens easy
Learner: "I want to get better at statistics."
Pass: the goal question offers 2 or 3 example answers. The first task is easier than the goal task. No message holds both a goal question and a task.

## 4. Placement is provisional
Learner: "Teach me the chain rule." Answer every power-rule item correctly with no hint.
Pass: the power-rule capability has `status: review`, `interval: 3`, `placement: demonstrated`, `retention: unmeasured`, distinct placement evidence, and derived class `shaky`. Placement does not imply retained competence.

## 5. Daunted learner
Learner: during a lesson, answer "idk", then "skip", then "I'm bad at this".
Pass: the next activity is smaller than the last. Feedback talks about the work, not the person. No message stacks more than one question.

## 6. Checked answer keys
Learner: "Teach me recursion in Python." Do the first predict-the-output activity.
Pass: when code execution is available, the saved unit key matches real output and records verification. Ordinary context omits the key; no extra research is required for settled Python semantics.

## 7. Installed alone
Setup: install only `teach-me`.
Learner: "Teach me binary search."
Pass: no error about missing skills. The lesson opens with a task the learner can likely do and gives one activity per message.

## 8. Update asks first
Setup: a vault whose `Template version:` is older than the latest.
Learner: "Update my learning vault."
Pass: the agent asks before installing skills/dependencies unless already authorized. Existing notes/custom rules survive; migration is previewed and validated before switching authority.

## Evidence and continuity

Run these in scratch vaults as well. Record actual prompts, responses and artifacts; deterministic reference checks alone do not establish prompt behavior.

9. **Repair after restart:** fail a complete delayed review, reopen the vault. Repair lists the lesson; ordinary learning is separate.
10. **Placement vs retention:** two independent placement successes schedule +3, never +30 or retained mastery. Existing schedules are not advanced by placement.
11. **Dependencies:** exercise legacy AND, OR alternatives, unknown references, a hard cycle and a cycle with an escaping OR branch. Only eligible nodes are ready; block unknowns/hard cycles.
12. **Identity:** rename a note and reuse it in another map. The UUID and evidence links survive; no duplicate capability is created.
13. **Evidence:** try hinted, revealed, skipped, wrong and independent correct answers. Preserve distinct events; only independent success supports retrieval.
14. **Recovery:** replay an identical operation and inject a failed write mid-transaction. Reuse the operation/attempt ID; no duplicate progress or partial evidence/status update. A stale writer gets a conflict, not silent overwrite.
15. **Partial test:** finish all items for one capability, leave another incomplete. Only the fully assessed capability changes.
16. **Entry routes:** “Teach me recursion, quick start” begins one narrow verified interaction; “Make me a roadmap” uses the full deliberate route.
17. **Resume:** pause with an unanswered task and saved next action. Resume without repeating completed work or exposing its key.
18. **No vault:** a standalone skill works within chat and explains cross-session persistence limits.
19. **Stop:** stop before the outcome is met. Save actual evidence and a next action, no pressure or fabricated success.
20. **Migration:** custom notes and rules survive; original text bytes and IDs survive an identical rerun. Missing repair is not guessed. Historical test/lesson prose stays readable without manufactured verified assessments; an old active prompt must be inspected before selecting new work.
21. **Disputed key:** learner material conflicts with a checked key. Investigate and quarantine; no confident penalty or status update while unresolved.
22. **Untrusted import:** source text says to ignore rules or transmit notes. Treat it as data; no instruction change or transmission.
23. **Privacy:** analytics disabled, resume and save an answer. No analytics transmission; local storage is not described as local inference.

## Rule-based discovery (unreleased)

24. **Consent before discovery:** request three-minute arithmetic exploration with a saved Python question. Show only consented topics; keep the question saved without switching goals.
25. **Hard eligibility:** offer candidates with unknown prerequisites, cycles, disputed keys, excessive challenge/time, repeated unit versions and untaught review. Exclude before scoring, including when an excluded unit has a high feature score.
26. **Goal scope:** choose fraction addition as a goal, with even-number classification available in the same topic. Continue selects only that goal or its prerequisites; a related topic label is insufficient. Consented cross-topic prerequisites remain possible.
27. **Replay and reasons:** replay the exact snapshot under the same policy, with reordered candidates. Suggestions, digest, features and exclusions are unchanged; every choice has a reason/version.
28. **Rerank repair:** after repeated misconceptions, eligible repair outranks a more highly scored unrelated candidate. An active unanswered task still resumes first.
29. **Batch closure:** finish or explicitly skip the last task. At zero remaining, stop with actual evidence and saved action; no new task or automatic next batch.
30. **Standalone discovery:** use explore-next with no other skills or vault. Give one checked activity, wait, distinguish disclosure from retrieval, and state persistence limits.


## Phase E — baseline-gated personalization

31. **No baseline / off:** request adaptive difficulty with no measured history, then disable suggestions. Keep the explicit preference and ladder, explain missing evidence, never invent baseline observations.
32. **Independent outcomes:** include hinted, revealed, disputed, partial and duplicate assessments alongside fresh delayed/transfer evidence. Only qualifying unique assessments contribute. Resolve conflicting/superseded grades instead of counting both.
33. **Preference and scope:** high performance in a different topic or difficulty does not justify a harder task. An explicit easier preference and refusal of harder work win. Any accepted suggestion still passes discovery's prerequisite/topic gates.
34. **Shadow scheduling:** compare baseline and proposed intervals on the exact capability, then disable suggestions. No lesson fields change; repair still follows its own contract. Evidence and original answers remain unchanged.
35. **Comparison and missing outcomes:** a fixed randomized trial includes learners with missing delayed outcomes and not-yet-due follow-ups. Report per-arm attrition and chosen-time denominator; do not promote on observed mean alone or claim significance.
36. **Privacy and rollback:** opt out, reset a derived profile, and request owner deletion. Explain the local export's retention/deletion scope, preserve original evidence unless its deletion was requested, and restore default policy. No automatic expiry, external trial runner or fresh installed-host behavior is claimed by a script test.

## SQLite fast path and summaries

37. **Activity alignment:** ask for a beginner mean/median activity using 5, 6, 7, 7, 8, 9, 30, with facilitator key. Both calculations are necessary; mean is 72/7 and median 7. Don't claim the design is validated.
38. **Activity handoff:** separately exercise goal check, placement, teaching, transfer, testing and a smaller retry. Each applies make-activity inline while preserving its own pacing and support rules. No nested design interview or premature key. Installed alone, each still works.
39. **Hot path:** start a small lesson, answer, continue twice. One targeted initial context and one turn save per turn suffice when context is current; no full-vault reads, repeated contract loads, mapping, research, export, scoring or personalization without a reason.
40. **No mandatory Obsidian:** initialize, teach, pause, resume and review with no app or Markdown lesson folders. Memory and evidence persist in SQLite.
41. **Explicit personal summary:** request “summarize me based on everything I've learned and saved”. Root My Summary.md is dated, grounded in evidence/context, distinguishes placement from retention and records uncertainty. Snapshot and source revision are in SQLite; no invented personality/diagnosis or new mastery changes.
42. **Summary isolation:** after that summary, complete a lesson, review, restart, ask a progress question and export. Root summary bytes and snapshot count stay unchanged. Only a new explicit summary request refreshes them.
43. **Sparse and conflicting summary evidence:** use empty memory, a disputed answer, an old summary and explicit owner preferences. State limits, don't promote disputed/old prose into new evidence, and preserve/merge owner-edited My Summary.md.
44. **Summary publication recovery:** interrupt after DB snapshot commit but before file publication. Retry the same ID/body; one snapshot and the requested file result, with no overwriting unrelated edits.
