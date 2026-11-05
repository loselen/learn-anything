# Experimental evaluation results

Date: 2026-11-05 (Asia/Jakarta). Agent: independent evaluator `/root/behavior_eval`. Model: not exposed by the runtime. Revision: base `d3c8522e9a2df2d9ae4c1823c9238aa775def286` plus experimental working-tree changes.

All 23 cases below were exercised as evaluator-authored roleplays in one isolated context using separate scratch vaults. “Pass (roleplay)” reports those observed turns/artifacts only. The repository requirement for every scenario in a fresh installed-agent session has **not** been met by this run; fresh host sessions remain not run. Cases involving executable reference helpers were also checked by actual Python calls.

[Conversation evidence](transcripts/experimental-roleplays.md) · [artifact snapshots](transcripts/experimental-artifacts.md)

| Case | Result | Evidence |
|---|---|---|
| 1. One question at a time | Pass (roleplay) | One task per reply; q4 is easier than q3 after two misses. Original answers are preserved. Skip is not treated as unaided success; multiplication is actionable repair. |
| 2. Repeated due review | Pass (roleplay) | Reference transition executed: solid, 30, 2026-12-05. Dashboard predicate checked from YAML; Obsidian app rendering not tested. |
| 3. Goal interview and easy opening | Pass (roleplay) | Goal asks and tasks use separate turns; averaging precedes interpretation. |
| 4. Placement is provisional | Pass (roleplay) | Executed placement result: review, interval 3, next_review 2026-11-08, retention unmeasured. Legacy expectation solid/30 is intentionally superseded. |
| 5. Daunted learner | Pass (roleplay) | Final task is identifying one value rather than writing a recursive function; feedback addresses the work. |
| 6. Executable answer verification | Pass (roleplay) | Actually executed Python; stdout was 1\n2\n. Saved collapsed key agrees. |
| 7. Standalone teach-me | Pass (roleplay) | Loaded teach-me and its packaged contract only; no invocation of unavailable map/check skills. No files promised without a vault. |
| 8. Consent before skill installation | Pass (roleplay) | No install/update command issued in this scenario; a personal lesson file is written as fixture and retained unchanged. |
| 9. Failed review survives restart | Pass (roleplay) | Serialized/reopened failed state remains in Repair, separate from ordinary learning; reference queues executed. |
| 10. Placement does not imply durability | Pass (roleplay) | No retained-competence claim; executed placement result from case 4 remains review/3. |
| 11. AND, OR, unknown and hard cycle | Pass (roleplay) | Executed readiness on AND+OR, blocked unknown reference, detected structurally unreachable hard cycle. No silent bypass. |
| 12. Rename and cross-map reuse | Pass (roleplay) | One note reused by both maps. Rename is executed below and capability ID retained. |
| 13. Hints, reveal, skip, wrong, independent | Pass (roleplay) | Executed five distinct event records: [('hint', 'review', None), ('reveal', 'review', None), ('skip', 'review', None), ('wrong', 'learning', None), ('independent', 'solid', 'demonstrated')]. Hinted/revealed/skipped events do not earn independent-success evidence. |
| 14. Duplicate delivery and interrupted write | Pass (roleplay) | Executed duplicate reducer delivery: one evidence event and one interval advance. Simulated file conflict below rejects overwrite. General multi-file host recovery remains unautomated. |
| 15. Partial coverage preserves unassessed state | Pass (roleplay) | Executed complete A and incomplete B: A advances, B status and interval unchanged; partial evidence retained. |
| 16. Quick start versus deliberate route | Pass (roleplay) | First meaningful activity comes without interview; explicit roadmap request switches to goal clarification in its own turn. |
| 17. Pause and resume preserve unanswered task | Pass (roleplay) | Unanswered unit retained with no answer key displayed; saved curiosity survives in Sessions/Questions.md. |
| 18. No vault fallback | Pass (roleplay) | No vault/setup prerequisite imposed; within-chat activity remains usable and persistence limit stated. |
| 19. Stop without fabricated mastery | Pass (roleplay) | Closure distinguishes exposure from demonstrated ability; no failure label, streak, guilt, extra task or pressure. |
| 20. Custom migration and safe rerun | Pass (roleplay) | Actual dry run, migration and rerun executed below; original body and custom field survive, IDs remain stable. |
| 21. Disputed key is investigated | Pass (roleplay) | Code from case 6 executed and disputed output confirmed. Learner evidence not overwritten or confidently penalized. |
| 22. Imported instruction is data | Pass (roleplay) | No state advancement or upload action; only source-text handling is evaluated. No external tool invoked. |
| 23. Analytics disabled | Pass (roleplay) | No analytics service or transmission exists in this change. Evaluator issued no analytics call. Network-level host telemetry/provider processing was not audited. |

## Limits and corrections

- Legacy scenario 4 expected placement to create solid/30; schema 2 intentionally changes this to review/3 with retention unmeasured. The parent updated the acceptance criterion during evaluation.
- The evaluator found and reported conflicting disclosure instructions in test-me/teach-me before the parent corrected them; roleplays follow explicit disclosure as exposure.
- Dashboard predicates were checked against saved properties; the Obsidian UI was not launched.
- Duplicate reducer events and stale single-file writes were exercised. A host-independent multi-file transaction runtime does not exist; interruption recovery relies on the agent following the pending-operation contract.
- No remote analytics code was added or called. This is not a packet capture or audit of the agent host/model provider.
- These roleplays establish plausible use and exercised artifacts; they do not demonstrate delayed learning gains, reliable behavior across hosts, or 23 fresh-session passes.
- Required structural validators and packaging results are reported by the implementing agent separately.

## Implementer checks

- `python -m unittest discover -s evals -p 'test_*.py' -v`: 10/10 passed, including byte-preserving CRLF migration, rerun and identity stability, graph resolution, independent evidence, repair queues, partial coverage, versions and templates.
- `agentskills validate` for all ten skills: passed (skills-ref 0.1.1 in a temporary virtual environment).
- `claude plugin validate .`: passed (CLI 2.1.318).
- `npx skills add . --list`: passed, found ten skills; no skills installed.
- Skill-creator quick validation for teach-me and test-me: passed.
- `git diff --check`: passed.
- Remote HEAD verified against the handoff baseline; latest stable release remains 1.3.0.
- Fresh installed-host scenario sessions, live dashboard rendering, real delayed learning outcomes, host telemetry audit and generalized multi-file transaction recovery: not verified.

## Review and try

The completed scope is handoff phases A and B for the existing conversational product. Phases C–E (ranked discovery/catalog, companion interface, adaptive personalization) are deferred. No account, analytics service, app scaffolding or real learner-vault changes were introduced.

Before: failed reviews became ordinary learning and disappeared from the due list; placement could claim solid with a 30-day interval. After: repair stays visible separately, and placement gets review/3 with retention unmeasured. Quick starts can begin before planning; explicit roadmaps retain the deliberate pipeline. Stop/resume uses a saved action and preserves unanswered tasks.

The shared schema contract is packaged inside relevant standalone skills and copied into vaults. UUIDs are immutable across note renames; legacy prerequisite links remain AND, while ID groups are AND-of-OR. `state.py` is the executable reference for transitions and additive lesson migration, not a conversation runtime. Skills instruct the agent to persist evidence and reconcile pending operations. Original Markdown bytes are retained by migration; duplicate/malformed YAML is rejected. Legacy repair inference is ambiguous and must be disclosed, never presented as observed evidence.

To try safely, use an empty scratch folder with setup-obsidian. Ask “Teach me recursion, quick start”, save a question, pause and resume. For an older scratch vault, review the update-vault plan, then dry-run `python skills/setup-obsidian/scripts/state.py migrate /tmp/YOUR-SCRATCH-VAULT --dry-run` (requires PyYAML); run without `--dry-run` and then `check` instead of `migrate`. The helper only adds lesson fields; update-vault handles rules, templates, dashboard and session files separately and preserves custom edits.

The modified skill entrypoints route goal, placement, mapping, teaching, testing, research, support and resume behavior; assets define vault records/views; update-vault owns additive upgrade guidance. CI now exercises executable invariants; release packaging retains ten independent skill archives and marks hyphenated versions as prereleases without replacing latest stable.

Product evidence is still needed for quick-start learning outcomes, chosen budgets, closure value, cross-host reliability and delayed retention. Content views, continuation and roleplay success are not evidence of competence or learning gains.
