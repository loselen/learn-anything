# Personalization · adaptive-shadow-1

Use only when the learner asks for personalization or explicitly opts into local measurement. Default remains rules-1 and the 3 → 7 → 30 → 90 ladder. No baseline exists in this repository: fixtures are synthetic. Difficulty and schedule suggestions are hypotheses, not validated learning gains. No bandit or automatic schedule override is implemented.

## Local measurement

Offer off, measurement only, or measurement plus suggestions. Explain what is saved before collecting it. Export minimal assessed events from existing evidence; do not collect clicks, response speed, raw answers, personality or provider telemetry. Resolve disputed/superseded grades first. The helper reads JSON and prints JSON, without files, network requests, evidence updates or side effects. Without execution, use the same gates and arithmetic; without persistence, explain that replay is limited to this chat.

Keep explicit choices in SQLite `preferences`, frozen inputs in `baselines`, and input/output reports in session-linked `recommendations`, only with consent. Agree a retention period (default offer: 30 days), record the deletion date, and honor export/correction/reset/deletion, including derived reports. Expiry is managed by the host/learner, not an automatic service. Disabling suggestions restores the existing policy immediately; it never rewrites original assessments. Model-provider processing is separate from local storage; no remote analytics are introduced. Don't run this analysis on ordinary teaching turns.

Run `python scripts/personalize.py analyze snapshot.json` from explore-next. The snapshot has exactly:

- `topic`: one explicit chosen topic.
- `preference`: `{enabled: false, challenge: "practice", allow_harder: false}`. `enabled` means consent to suggestions, not merely collection. Preference always wins; harder suggestions require allow_harder too.
- `baseline`, `history`: arrays of the assessment objects below. Freeze baseline before adaptation; history contains only subsequent assessments under the current difficulty policy. For a new policy/difficulty, start a new history export. Baseline and history attempts must not overlap.
- `review`: `{capability_id: "stable-id", interval: 7}`. Interval is the **next interval already computed by the unchanged ladder**, not the previous interval. Repair remains governed by the state contract, never this shadow proposal.

Every assessment has exactly: `assessment_id`, `attempt_id`, `unit_id`, `unit_version`, `capability_id`, `topic`, `challenge` (intro/practice/stretch), `purpose` (practice/delayed/transfer), `independent`, `hinted`, `revealed`, `verified`, `disputed`, `complete` (explicit booleans), `score` (0–1), `delay_days` (nonnegative). IDs refer to existing versioned records; no original answers are copied. Assessment assertions come from the tutor/verifier, not authentication by this helper. Same assessment repeated identically collapses; conflicting grades or multiple assessments of one attempt fail until the export resolves them. Never fabricate observations to pass a gate.

Only complete, verified, undisputed, independent outcomes without hints/reveals qualify: fresh transfer or delayed assessment at least three days after teaching. Placement, ordinary practice, views and exposure do not qualify. Repeated IDs/versions of one unit do not supply unit diversity. Delayed tests and transfer must use fresh checked items and cover the declared outcome. These assertions require honest host evaluation; JSON does not prove them.

## Reversible difficulty suggestions

A topic baseline requires six qualifying observations across three units, with both delayed and transfer outcomes. Subsequent evidence requires six qualifying observations across three units at the explicitly chosen difficulty. These are conservative implementation guardrails, **not** a power calculation or proof of a useful effect. Baseline remains frozen and its digest is logged. Missing evidence keeps the explicit preference.

With suggestions enabled, mean score below .50 offers one easier level; at least .85 offers one harder level only if explicitly permitted. Otherwise keep the chosen level. Ask the learner to accept a suggested change; only then set the next selection snapshot's `challenge`. Keep all existing eligibility gates, goal/topic consent and one active task. Never change an active task or turn performance into a mastery label. Log this report and the next rules-1 snapshot locally for replay. Reverting requires only restoring the prior challenge preference.

## Review scheduling in shadow

After the baseline gate, two qualifying delayed outcomes on distinct units for the exact capability, each delayed at least the baseline next interval, permit a shadow proposal. Mean below .50 proposes 75% of the ladder interval, at least three days; at least .85 proposes 125%, at most 90 days (Python round); otherwise unchanged. This bounded heuristic is unvalidated. It does not alter `next_review`, repair, grades, retention or evidence. Actual scheduling continues to use the ladder. Compare the proposal offline first; applying it in a study requires a separately registered and consented trial, with an explicit host implementation. This helper does not run that trial.

## Fixed-policy comparison

Run `python scripts/personalize.py compare comparison.json`. Before assigning learners, review the measured baseline and predeclare `plan`: `id`, `registered_on` (YYYY-MM-DD), `baseline_digest` (SHA-256), `primary: "delayed_independent_score"`, `minimum_per_arm` (at least two, justified externally by variance, practical effect and power assumptions), `practical_effect` (0–1, positive), `stopping_rule` (fixed horizon/sample and harm rules), `retention_days` (positive), `consented: true`. Also provide `as_of` and `participants`. Registration metadata is an assertion, not a tamper-proof registry. The helper validates shape; it does not approve the plan or implement stopping/expiry.

Each participant row has exactly `id` (pseudonym, unique), `arm` (ladder/adaptive), `probability: 0.5`, `assigned_on`, `due_on` (at least three days later), `chosen_minutes` (positive explicit study budget), `delayed` and `transfer` (independent checked 0–1 scores or null). Supply **all** randomized participants, including missing follow-ups, once per participant. Aggregate repeated capability tests within each participant using a predeclared common rubric; do not treat correlated attempts as independent learners. Assign externally with fixed randomized 1:1 probabilities and log the assignment before outcomes; do not infer assignment from performance. No actual assignments or remote collection occur here.

The report shows observed delayed and transfer scores, missing/due counts, attrition by arm, total observed retained-score units and retained score per total assigned chosen minute (including missing/pending participants' time). These are rubric-relative units, not a count of mastered capabilities. Null is missing, not a zero grade. Not-yet-due outcomes are excluded; compare at the predeclared follow-up horizon. It reports the observed difference and sample/effect flags descriptively, without significance, causal claims or automatic promotion. Review uncertainty, differential attrition, grading disputes, ability to stop, value, workload and comparable fresh-item/blinded scoring before deciding. Stopping rules and practical thresholds cannot be retrofitted to favor a result.

A constrained contextual bandit remains deferred until an adequately powered comparison, reviewed data quality, defined delayed rewards, candidate-specific logged selection probabilities and consented exploration exist. Never optimize continuation/clicks as a substitute for delayed learning. All policy changes remain independent of learner evidence.

## SQLite projection

The read-only adapter accepts JSON on stdin: `python scripts/snapshot.py --root PATH observations -` with `topic` (database topic ID) and `assessment_ids`. It exports the helper's exact observation fields without responses, feedback or keys; combines key/grade verification and all exposure/reuse flags; excludes placement; and derives delay from the latest recorded teaching cycle before the attempt. Missing teaching history means delay 0, never guessed retention. Resolve superseded/out-of-topic IDs rather than substituting grades.

With consent, freeze that array in `baselines.snapshot` and use personalize.py's `digest(evidence(array))` as `baselines.digest`. For later analysis run `snapshot.py --root PATH measurement -` with exactly `topic`, `preference`, `baseline_id`, `history_assessment_ids` and `review_capability_id`. It checks the frozen digest and current evidence, projects history, and reads the already-computed ladder interval; unresolved repair blocks shadow scheduling. Pass its output to `personalize.py analyze`. Do not invent a baseline, mix policy histories, or run these exports on ordinary turns. JSON may travel through stdin/stdout; no sidecar file is required.
