# Discovery evaluation results

Date: 2026-11-05 (Asia/Jakarta). Evaluator: `/root/discovery_eval`; model identity not exposed. Baseline revision: `1f6bab8`, plus unreleased phase C working-tree changes. Evaluated selector SHA-256: `f3d5c4f1a81d10ed6c6a2ac8261fa86cc998b846bd1e914d47f756bb560019a6`.

Seven requested scenarios and four additional probes were executed through the real read-only selector CLI. The learner/tutor turns are evaluator-authored roleplays following the skill; they are not fresh installed-host conversations. Exact input/output JSON files and scratch session notes are under `/tmp/learn-anything-discovery-eval-cp9bs846`. No real vault, installed skill, network service or telemetry was used.

[Requests, decisions and actual JSON output](transcripts/discovery-evaluation.md)

| Case | Result | Observable evidence |
|---|---|---|
| Three-minute arithmetic exploration | Pass | Only whole-addition and even-classification were offered; a saved Python curiosity was excluded for topic_not_consented and retained as a scratch saved question. |
| Resume unanswered task | Pass | status resume, no new choices, only the saved prompt reference returned. An extra key field in active_unit was omitted. |
| Unknown prerequisite | Pass | status blocked; fraction activity excluded as blocked_dependency_graph. Tutor offers a diagnostic or explicitly non-assessing preview. |
| Placement-only due review | Pass | status blocked; taught false caused untaught_scope despite lifecycle review and demonstrated placement. |
| Repeated misconception | Pass | Repair candidate scored 0.235 yet outranked a 0.52 alternative because repair_priority was true. No precomputed next task was activated. |
| Batch complete and stop | Pass | batch_remaining 0 returned complete with empty choices. Scratch closure records an attempt and next action without retained-mastery claims. |
| Standalone/no vault | Pass | Missing topic consent returned needs_preference. Tutor offers one small preference and states chat persistence limits; no setup is required. |
| ISO basic-date input | Pass after correction | today 20261105 is rejected with exit 2 and dates must use YYYY-MM-DD; an ambiguous lexical comparison cannot admit future review. |
| Off-goal frontier | Pass after correction | Frontier activity outside the goal scope is excluded; no topic switch is silently activated. |
| Learning-state due review | Pass after correction | Even taught material at lifecycle learning is excluded as not_reviewable from due retrieval. |
| Specific goal within a broad topic | Pass after correction | With a fraction-addition goal, its prerequisite closure is eligible and the unrelated arithmetic even-number activity is outside_chosen_goal. |

## Findings and corrections

- Static inspection found that accepting ISO basic dates while comparing raw date strings could misclassify due dates. The implementer independently found the same issue and added strict YYYY-MM-DD validation before this evaluator’s runtime probe. The recorded probe verifies rejection; it does not claim a captured pre-fix failure.
- The first contract constrained continue mode only by a broad goal_topic. That could treat unrelated work in the same topic as goal-relevant. The evaluator reported this; the implementer added explicit goal_capability_ids and prerequisite closure filtering. Case 11 executes the corrected behavior.
- Follow-up probes verified the implementer’s lifecycle gate for due_review and scope gate for frontier.

## Limits

- Conversational turns here are one evaluator context using the skill, not captured output from fresh installations in multiple hosts. These are plausible observed decisions and executed helper outputs, not cross-host reliability evidence.
- The selector trusts verified-content assertions from the tutor/verifier. Digests detect changed payloads, not false provenance or a fabricated verification claim. It does not grade learner responses.
- The evaluator did not re-audit every catalog answer key; the implementer’s executable content checks cover those. Catalog coverage remains a small arithmetic/Python starter set, not a curriculum.
- No live dashboard/UI, packet capture, model-provider audit, general multi-file recovery, retention outcome or causal learning-gain study was performed.
- Scratch session writes demonstrate possible records; the read-only selector does not itself persist them. Actual host agents must follow the saving/reconciliation instructions.
- Existing release artifacts and real vaults were not changed during evaluation. Phase C remains unreleased.

## Implementer verification and handback

- 22 deterministic tests passed: prior state/migration checks plus eligibility, AND/OR/cycles, goal closure, consented cross-topic prerequisites, repeat repair, dates, replay, no evidence mutation, privacy of key payloads, active resume, endpoint closure, stale content, and actual catalog calculations/execution.
- All eleven skills passed agentskills validation; explore-next passed skill-creator validation. Plugin validation passed; discovery found eleven skills without installing them.
- Skill archives were built locally and checked for integrity and their own entrypoints; release packaging discovers skill folders automatically. The badge was rendered and visually checked after changing its outlined number to eleven.
- The final catalog makes equivalent-fraction and common-denominator capabilities explicit prerequisites. They remain planned/unknown without independent evidence; there are no starter units for those bridges, so a tutor must diagnose or teach them before offering fraction addition. Catalog and fixture IDs/references are checked together.
- No new required vault property, migration or template version is introduced. Recommendation sections/snapshots are additive, derived and local; existing learner IDs, attempts and grades remain authoritative. Updating the policy does not revise evidence.
- Completed handoff phase C for conversational skills: seven candidate sources, versioned eligibility/ranking, plain reasons, per-answer reranking, and session boundaries. Companion UI and adaptive personalization (D–E) remain deferred pending evidence or a separate request.
- This work is unreleased. The 2026-11-05 prerelease tag/assets stay immutable; AGENTS.md limits releases to one per day. Version metadata stays at the previously published version until the next batched release is prepared. PR #16 contains the development changes.

Try the read-only demo with `python skills/explore-next/scripts/select.py evals/fixtures/discovery-snapshot.json`, or load explore-next in a scratch learning conversation and ask “Explore arithmetic for three minutes”. The demo never modifies a vault. A real host agent must gather explicit preferences, verify candidate assertions, persist the input snapshot/recommendation, and hand the chosen unit to teaching/review. No live recommendation daemon or application platform was added.

## Experimental.2 publication

The owner explicitly authorized publishing `v1.4.0-experimental.2` on 2026-11-05 as a continuation and exception to the one-release-per-day convention. This supersedes the unreleased scheduling note above; prior evaluation evidence and its limitations are unchanged. Only release metadata and documentation changed after the evaluated discovery implementation. Template/plugin versions advance together; no new required vault schema or learner content change is introduced.

Pre-publication checks rerun: 22 deterministic tests, all eleven agentskills validators, plugin validation, eleven-skill discovery and diff whitespace checks passed. Existing scenario evidence covers scenarios 1–23 through evaluator roleplays and discovery scenarios 24–30 through executed CLI probes and evaluator-authored turns. Fresh installed-host scenarios remain not run; this prerelease makes no claim to satisfy that validation level. No real vault or installed skills were modified.
