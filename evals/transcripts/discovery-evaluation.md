# Discovery evaluation transcripts

2026-11-05 (Asia/Jakarta) · evaluator `/root/discovery_eval` · model identity not exposed.

These are evaluator-authored learner/tutor turns following the packaged skill, paired with actual selector subprocess results. They are not captured output from fresh installed-host conversations. Every JSON input and output was written in a separate scratch artifact under `/tmp/learn-anything-discovery-eval-cp9bs846`; no real vault was opened, no network call was made, and no skill installation occurred.

Input baseline: `evals/fixtures/discovery-snapshot.json`. Each case used a deep copy and the deltas below. Only scratch session notes were created to exercise saved-question and closure records. Selection is read-only; these notes were authored by the evaluator, not by the helper.

## 01-budget-consent

**Input:** Keep baseline three-minute arithmetic consent; change the Python print candidate source to saved_question. Write its curiosity text with disposition saved in scratch Sessions/Questions.md.

**Learner:** Explore arithmetic for three minutes. Keep my Python question saved for later.

**Evaluator tutor:** Combining two groups fits your three minutes and starts with a checked example. Recognizing even numbers is another option. Your Python question stays saved for later. Which would you like?

**Actual helper result:** exit 0.

```json
{
  "policy_version": "rules-1",
  "snapshot_digest": "86cd99bf6f85fed508a85523ed3a09197d0402444694f0860b939d4db68c1a62",
  "eligible": [
    {
      "id": "whole-addition",
      "version": "1",
      "capability_id": "8bab09e4-6255-5a46-a81a-dcd87ea0f36c",
      "title": "Combine two groups",
      "source": "catalog",
      "purpose": "practice",
      "topic": "arithmetic",
      "effort_minutes": 2,
      "features": {
        "goal_relevance": 0.0,
        "review_urgency": 0.0,
        "interest": 0,
        "readiness": 1.0,
        "evidence_value": 0.7,
        "diversity": 0,
        "repetition": 0,
        "context_switch": 0.0,
        "time_mismatch": 0.6666666666666666
      },
      "score": 0.188333,
      "repair_priority": false,
      "reason": "This is a checked starter within your chosen topics."
    },
    {
      "id": "even-classification",
      "version": "1",
      "capability_id": "0dc07724-5a13-51a7-8bd9-59288d2e740f",
      "title": "Recognize even integers",
      "source": "catalog",
      "purpose": "practice",
      "topic": "arithmetic",
      "effort_minutes": 3,
      "features": {
        "goal_relevance": 0.0,
        "review_urgency": 0.0,
        "interest": 0,
        "readiness": 1.0,
        "evidence_value": 0.7,
        "diversity": 0,
        "repetition": 0,
        "context_switch": 0.0,
        "time_mismatch": 1.0
      },
      "score": 0.155,
      "repair_priority": false,
      "reason": "This is a checked starter within your chosen topics."
    }
  ],
  "exclusions": [
    {
      "id": "print-sequence",
      "reason": "topic_not_consented"
    },
    {
      "id": "fraction-addition",
      "reason": "challenge_mismatch"
    },
    {
      "id": "function-parts",
      "reason": "topic_not_consented"
    }
  ],
  "choices": [
    {
      "id": "whole-addition",
      "version": "1",
      "capability_id": "8bab09e4-6255-5a46-a81a-dcd87ea0f36c",
      "title": "Combine two groups",
      "source": "catalog",
      "purpose": "practice",
      "topic": "arithmetic",
      "effort_minutes": 2,
      "features": {
        "goal_relevance": 0.0,
        "review_urgency": 0.0,
        "interest": 0,
        "readiness": 1.0,
        "evidence_value": 0.7,
        "diversity": 0,
        "repetition": 0,
        "context_switch": 0.0,
        "time_mismatch": 0.6666666666666666
      },
      "score": 0.188333,
      "repair_priority": false,
      "reason": "This is a checked starter within your chosen topics."
    },
    {
      "id": "even-classification",
      "version": "1",
      "capability_id": "0dc07724-5a13-51a7-8bd9-59288d2e740f",
      "title": "Recognize even integers",
      "source": "catalog",
      "purpose": "practice",
      "topic": "arithmetic",
      "effort_minutes": 3,
      "features": {
        "goal_relevance": 0.0,
        "review_urgency": 0.0,
        "interest": 0,
        "readiness": 1.0,
        "evidence_value": 0.7,
        "diversity": 0,
        "repetition": 0,
        "context_switch": 0.0,
        "time_mismatch": 1.0
      },
      "score": 0.155,
      "repair_priority": false,
      "reason": "This is a checked starter within your chosen topics."
    }
  ],
  "selected": {
    "id": "whole-addition",
    "version": "1",
    "capability_id": "8bab09e4-6255-5a46-a81a-dcd87ea0f36c",
    "title": "Combine two groups",
    "source": "catalog",
    "purpose": "practice",
    "topic": "arithmetic",
    "effort_minutes": 2,
    "features": {
      "goal_relevance": 0.0,
      "review_urgency": 0.0,
      "interest": 0,
      "readiness": 1.0,
      "evidence_value": 0.7,
      "diversity": 0,
      "repetition": 0,
      "context_switch": 0.0,
      "time_mismatch": 0.6666666666666666
    },
    "score": 0.188333,
    "repair_priority": false,
    "reason": "This is a checked starter within your chosen topics."
  },
  "status": "suggested"
}
```

## 02-unanswered-resume

**Input:** Set active_unit to unfinished-even@1, topic arithmetic, prompt_reference Lessons/Even.md#Activity; include an extra key field to probe whether it leaks.

**Learner:** Resume where we stopped.

**Evaluator tutor:** We paused at your classification task: which of -4, 0 and 3 are even? Your earlier work is saved; this is the unanswered part.

**Actual helper result:** exit 0.

```json
{
  "policy_version": "rules-1",
  "snapshot_digest": "5836d76cb43aae3933673752c4d8fd64119051ee46c76f6044a6cdd7a9ba28f5",
  "eligible": [],
  "exclusions": [],
  "choices": [],
  "selected": null,
  "status": "resume",
  "reason": "Resume the unanswered task.",
  "active_unit": {
    "id": "unfinished-even",
    "version": "1",
    "topic": "arithmetic",
    "prompt_reference": "Lessons/Even.md#Activity"
  }
}
```

## 03-unknown-prerequisite

**Input:** Use fraction-addition only, stretch challenge, 10-minute budget; replace its capability prerequisite with unknown-whole-number-skill.

**Learner:** Teach me the next fraction activity.

**Evaluator tutor:** I do not yet have evidence for the number-combining step this needs. Would you prefer a short check of that step or a non-assessing preview of fractions?

**Actual helper result:** exit 0.

```json
{
  "policy_version": "rules-1",
  "snapshot_digest": "4a82439dda7424486657c39b538eb37a95ed04234cf2d960c4aff6026407a46f",
  "eligible": [],
  "exclusions": [
    {
      "id": "fraction-addition",
      "reason": "blocked_dependency_graph"
    }
  ],
  "choices": [],
  "selected": null,
  "status": "blocked",
  "reason": "No eligible activity. Offer a bridge, diagnostic, labeled preview, or one preference question."
}
```

## 04-placement-not-taught

**Input:** Use whole-addition only as due_review/review, modes [review], due_date 2026-11-04, mode review. Its capability has status review, placement demonstrated, taught false.

**Learner:** Review the lesson you placed me into yesterday.

**Evaluator tutor:** That record shows placement, not a taught lesson, so I will not treat it as retrieval practice of taught material. Would you like a short lesson on it first?

**Actual helper result:** exit 0.

```json
{
  "policy_version": "rules-1",
  "snapshot_digest": "1935d229d93eacf0f6e289b54eb3ed5c6a2efcff3f13c6da4efd354e74d82df1",
  "eligible": [],
  "exclusions": [
    {
      "id": "whole-addition",
      "reason": "untaught_scope"
    }
  ],
  "choices": [],
  "selected": null,
  "status": "blocked",
  "reason": "No eligible activity. Offer a bridge, diagnostic, labeled preview, or one preference question."
}
```

## 05-misconception-repair

**Input:** Use stretch challenge and 10-minute budget. Change whole-addition to repair/repair, capability learning/taught true/repair true, and list its ID in repeated_misconceptions. Set even-classification interest, evidence_value and diversity to 1.

**Learner:** What next? I keep combining the groups the same wrong way.

**Evaluator tutor:** Your recent attempts suggest repairing how the two groups combine before moving on. A short checked example is ready. Shall we use that next?

**Actual helper result:** exit 0.

```json
{
  "policy_version": "rules-1",
  "snapshot_digest": "0cc06e64f3467cde647c8d27d94b7c5ee87c1483dd3a8e739bb990de5e9953a7",
  "eligible": [
    {
      "id": "whole-addition",
      "version": "1",
      "capability_id": "8bab09e4-6255-5a46-a81a-dcd87ea0f36c",
      "title": "Combine two groups",
      "source": "repair",
      "purpose": "repair",
      "topic": "arithmetic",
      "effort_minutes": 2,
      "features": {
        "goal_relevance": 0.0,
        "review_urgency": 0.0,
        "interest": 0,
        "readiness": 1.0,
        "evidence_value": 0.7,
        "diversity": 0,
        "repetition": 0,
        "context_switch": 0.0,
        "time_mismatch": 0.2
      },
      "score": 0.235,
      "repair_priority": true,
      "reason": "Your repeated attempts suggest repairing this before continuing."
    },
    {
      "id": "even-classification",
      "version": "1",
      "capability_id": "0dc07724-5a13-51a7-8bd9-59288d2e740f",
      "title": "Recognize even integers",
      "source": "catalog",
      "purpose": "practice",
      "topic": "arithmetic",
      "effort_minutes": 3,
      "features": {
        "goal_relevance": 0.0,
        "review_urgency": 0.0,
        "interest": 1,
        "readiness": 1.0,
        "evidence_value": 1,
        "diversity": 1,
        "repetition": 0,
        "context_switch": 0.0,
        "time_mismatch": 0.3
      },
      "score": 0.52,
      "repair_priority": false,
      "reason": "This is a checked starter within your chosen topics."
    }
  ],
  "exclusions": [
    {
      "id": "print-sequence",
      "reason": "topic_not_consented"
    },
    {
      "id": "fraction-addition",
      "reason": "prerequisites_not_ready"
    },
    {
      "id": "function-parts",
      "reason": "topic_not_consented"
    }
  ],
  "choices": [
    {
      "id": "whole-addition",
      "version": "1",
      "capability_id": "8bab09e4-6255-5a46-a81a-dcd87ea0f36c",
      "title": "Combine two groups",
      "source": "repair",
      "purpose": "repair",
      "topic": "arithmetic",
      "effort_minutes": 2,
      "features": {
        "goal_relevance": 0.0,
        "review_urgency": 0.0,
        "interest": 0,
        "readiness": 1.0,
        "evidence_value": 0.7,
        "diversity": 0,
        "repetition": 0,
        "context_switch": 0.0,
        "time_mismatch": 0.2
      },
      "score": 0.235,
      "repair_priority": true,
      "reason": "Your repeated attempts suggest repairing this before continuing."
    },
    {
      "id": "even-classification",
      "version": "1",
      "capability_id": "0dc07724-5a13-51a7-8bd9-59288d2e740f",
      "title": "Recognize even integers",
      "source": "catalog",
      "purpose": "practice",
      "topic": "arithmetic",
      "effort_minutes": 3,
      "features": {
        "goal_relevance": 0.0,
        "review_urgency": 0.0,
        "interest": 1,
        "readiness": 1.0,
        "evidence_value": 1,
        "diversity": 1,
        "repetition": 0,
        "context_switch": 0.0,
        "time_mismatch": 0.3
      },
      "score": 0.52,
      "repair_priority": false,
      "reason": "This is a checked starter within your chosen topics."
    }
  ],
  "selected": {
    "id": "whole-addition",
    "version": "1",
    "capability_id": "8bab09e4-6255-5a46-a81a-dcd87ea0f36c",
    "title": "Combine two groups",
    "source": "repair",
    "purpose": "repair",
    "topic": "arithmetic",
    "effort_minutes": 2,
    "features": {
      "goal_relevance": 0.0,
      "review_urgency": 0.0,
      "interest": 0,
      "readiness": 1.0,
      "evidence_value": 0.7,
      "diversity": 0,
      "repetition": 0,
      "context_switch": 0.0,
      "time_mismatch": 0.2
    },
    "score": 0.235,
    "repair_priority": true,
    "reason": "Your repeated attempts suggest repairing this before continuing."
  },
  "status": "suggested"
}
```

## 06-batch-complete

**Input:** Set batch_remaining to zero. Write a closed scratch session with one saved next action and no claim of retention.

**Learner:** That is enough for today. Stop here.

**Evaluator tutor:** We can stop here. The next action is saved: try one fresh group-combining problem. Today’s prediction is recorded as an attempt; it does not establish retained mastery.

**Actual helper result:** exit 0.

```json
{
  "policy_version": "rules-1",
  "snapshot_digest": "d7bad76239a7d904484c6a4234db27f91e17ec994ada367b5ad97da29ad299ef",
  "eligible": [],
  "exclusions": [],
  "choices": [],
  "selected": null,
  "status": "complete",
  "reason": "This batch is complete. Save a next action or stop here."
}
```

## 07-no-vault-preference

**Input:** Set allowed_topics and candidates to empty lists, goal_topic null. No vault is available.

**Learner:** Surprise me. I have no vault and only this skill.

**Evaluator tutor:** Which sounds better: a tiny arithmetic puzzle or a Python output question? I can keep our progress in this chat; I cannot guarantee it will carry to another chat without a vault.

**Actual helper result:** exit 0.

```json
{
  "policy_version": "rules-1",
  "snapshot_digest": "4d4b7a6b7948c2dac279c27226f6f66369e23b67b792e15662e35f814b5d7c22",
  "eligible": [],
  "exclusions": [],
  "choices": [],
  "selected": null,
  "status": "needs_preference",
  "reason": "Choose a topic before selecting an activity."
}
```

## 08-date-format-probe

**Input:** Mode review; whole-addition only as due_review/review, taught true, status review, due_date 2026-11-06. Set today to ISO basic form 20261105.

**Learner:** What is due today?

**Actual helper result:** exit 2.

```json
{
  "error": "dates must use YYYY-MM-DD",
  "policy_version": "rules-1"
}
```

## 09-offgoal-frontier

**Input:** Use whole-addition only as frontier/practice, modes [explore], and goal_topic python; taught true. This probes a source labeled frontier outside the chosen topic.

**Actual helper result:** exit 0.

```json
{
  "policy_version": "rules-1",
  "snapshot_digest": "d91574b81c6abefe906f7dd3c57b360de423f8216dc8f59084ea801031b1da80",
  "eligible": [],
  "exclusions": [
    {
      "id": "whole-addition",
      "reason": "outside_chosen_goal"
    }
  ],
  "choices": [],
  "selected": null,
  "status": "blocked",
  "reason": "No eligible activity. Offer a bridge, diagnostic, labeled preview, or one preference question."
}
```

## 10-learning-not-due-review

**Input:** Use whole-addition only as due_review/review, modes [explore], due_date 2026-11-04, capability learning/taught true. This probes a taught lesson that is not in a reviewable lifecycle status.

**Actual helper result:** exit 0.

```json
{
  "policy_version": "rules-1",
  "snapshot_digest": "2deee99cd24643e15eb62828190ec9bea208b180e9167f0ea5a2f8188839ec6b",
  "eligible": [],
  "exclusions": [
    {
      "id": "whole-addition",
      "reason": "not_reviewable"
    }
  ],
  "choices": [],
  "selected": null,
  "status": "blocked",
  "reason": "No eligible activity. Offer a bridge, diagnostic, labeled preview, or one preference question."
}
```

## 11-specific-goal-frontier

**Input:** Set mode continue, goal_topic arithmetic, goal_capability_ids to the fraction-addition capability, challenge stretch and budget 10. Mark the whole-addition prerequisite review. Keep unrelated even-classification in the candidate pool.

**Learner:** Continue toward adding fractions; what is ready next?

**Evaluator tutor:** Your prerequisite is in place. A short combining check or the fraction activity fits this goal; the even-number activity is outside it. Which would you prefer?

**Actual helper result:** exit 0. The goal closure contains the fraction capability and its whole-addition prerequisite. It excludes the unrelated same-topic even-number activity.

```json
{
  "policy_version": "rules-1",
  "snapshot_digest": "e3e3b62c1e0eb879ae16bd0ee1afa9dec696356df23eeefee0fce41fcd9738bc",
  "eligible": [
    {
      "id": "whole-addition",
      "version": "1",
      "capability_id": "8bab09e4-6255-5a46-a81a-dcd87ea0f36c",
      "title": "Combine two groups",
      "source": "catalog",
      "purpose": "practice",
      "topic": "arithmetic",
      "effort_minutes": 2,
      "features": {
        "goal_relevance": 1.0,
        "review_urgency": 0.0,
        "interest": 0,
        "readiness": 1.0,
        "evidence_value": 0.7,
        "diversity": 0,
        "repetition": 0,
        "context_switch": 0.0,
        "time_mismatch": 0.2
      },
      "score": 0.485,
      "repair_priority": false,
      "reason": "This is a checked starter within your chosen topics."
    },
    {
      "id": "fraction-addition",
      "version": "1",
      "capability_id": "4a35b145-bff2-5e96-a11d-f831ea71a043",
      "title": "Combine equal-sized parts",
      "source": "catalog",
      "purpose": "practice",
      "topic": "arithmetic",
      "effort_minutes": 4,
      "features": {
        "goal_relevance": 1.0,
        "review_urgency": 0.0,
        "interest": 0,
        "readiness": 1.0,
        "evidence_value": 0.7,
        "diversity": 0,
        "repetition": 0,
        "context_switch": 0.0,
        "time_mismatch": 0.4
      },
      "score": 0.465,
      "repair_priority": false,
      "reason": "This is a checked starter within your chosen topics."
    }
  ],
  "exclusions": [
    {
      "id": "print-sequence",
      "reason": "topic_not_consented"
    },
    {
      "id": "even-classification",
      "reason": "outside_chosen_goal"
    },
    {
      "id": "function-parts",
      "reason": "topic_not_consented"
    }
  ],
  "choices": [
    {
      "id": "whole-addition",
      "version": "1",
      "capability_id": "8bab09e4-6255-5a46-a81a-dcd87ea0f36c",
      "title": "Combine two groups",
      "source": "catalog",
      "purpose": "practice",
      "topic": "arithmetic",
      "effort_minutes": 2,
      "features": {
        "goal_relevance": 1.0,
        "review_urgency": 0.0,
        "interest": 0,
        "readiness": 1.0,
        "evidence_value": 0.7,
        "diversity": 0,
        "repetition": 0,
        "context_switch": 0.0,
        "time_mismatch": 0.2
      },
      "score": 0.485,
      "repair_priority": false,
      "reason": "This is a checked starter within your chosen topics."
    },
    {
      "id": "fraction-addition",
      "version": "1",
      "capability_id": "4a35b145-bff2-5e96-a11d-f831ea71a043",
      "title": "Combine equal-sized parts",
      "source": "catalog",
      "purpose": "practice",
      "topic": "arithmetic",
      "effort_minutes": 4,
      "features": {
        "goal_relevance": 1.0,
        "review_urgency": 0.0,
        "interest": 0,
        "readiness": 1.0,
        "evidence_value": 0.7,
        "diversity": 0,
        "repetition": 0,
        "context_switch": 0.0,
        "time_mismatch": 0.4
      },
      "score": 0.465,
      "repair_priority": false,
      "reason": "This is a checked starter within your chosen topics."
    }
  ],
  "selected": {
    "id": "whole-addition",
    "version": "1",
    "capability_id": "8bab09e4-6255-5a46-a81a-dcd87ea0f36c",
    "title": "Combine two groups",
    "source": "catalog",
    "purpose": "practice",
    "topic": "arithmetic",
    "effort_minutes": 2,
    "features": {
      "goal_relevance": 1.0,
      "review_urgency": 0.0,
      "interest": 0,
      "readiness": 1.0,
      "evidence_value": 0.7,
      "diversity": 0,
      "repetition": 0,
      "context_switch": 0.0,
      "time_mismatch": 0.2
    },
    "score": 0.485,
    "repair_priority": false,
    "reason": "This is a checked starter within your chosen topics."
  },
  "status": "suggested"
}
```
