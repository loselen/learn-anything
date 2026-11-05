# Phase E implementation checks

Date: 2026-11-05. Agent: Codex (model identifier unavailable). Base revision: 07dd5176cbd09b21442c0b806f31ed29b2d23e83; results cover the uncommitted phase E changes. Phase D deliberately skipped. No real vault touched or installed skill changed. Publication of experimental.3 was subsequently authorized by the learner-facing repository owner.

## Executed

- `python -m unittest discover -s evals -p 'test_*.py' -v`: **29 passed** (22 existing, seven new meaningful executable tests).
- Eleven skill directories validated with skills-ref in `/tmp/learn-anything-validation`.
- `claude plugin validate .`: passed.
- `npm_config_cache=/tmp/learn-anything-npm npx --yes skills add . --list`: found 11, list only. It initially waited on package resolution; the cached CLI also independently found 11.
- `git diff --check`: passed.
- Empty-baseline CLI fixture: baseline_ready=false, preference remains practice, ladder interval remains three, applied=false, bandit_enabled=false. Input digest: `f4169f14001c671d9e047de31f6e72b5eece1c65df0254363b43c02b86d80d24`.

## Scenario coverage and concrete evidence

These are deterministic helper evaluations, not fresh installed-host roleplays. Scenarios 1–30 retain earlier behavioral evidence and executable regressions; they were not rerun in fresh conversational hosts here.

| New scenario | Executed evidence | Limit |
|---|---|---|
| 31 No baseline / off | `test_baseline_optin_and_difficulty`: missing baseline keeps practice; opt-out restores practice and seven-day baseline, no mutation | Host explanation not separately evaluated |
| 32 Independent outcomes | `test_ineligible_observations_and_diversity`, `test_idempotency_corrections_and_replay`: support/disputes/partial/practice excluded; duplicate IDs collapse; conflicting grades and overlapping histories reject | Host grading/provenance trusted |
| 33 Preferences/scope | `test_preferences_and_scoping`: no harder without permission; low score offers intro; different topic/difficulty does not transfer evidence | Acceptance and subsequent selection remain agent actions |
| 34 Shadow schedule | `test_baseline_optin_and_difficulty`, `test_preferences_and_scoping`: 7→9 or 7→5 only in report, wrong capability unchanged, input deep-equal after analysis | No alternative scheduler deployed |
| 35 Comparison | `test_comparison_missingness_time_and_no_promotion`, `test_comparison_rejects_invalid_trial`: missing outcome yields 50% attrition; assigned-time denominator retained; early results, duplicate learners and nonfixed probabilities rejected | Trial assignment, scoring, sample-power assumptions and stopping rules external |
| 36 Privacy/rollback | `test_invalid_evidence_and_cli`: raw-answer fields reject without echo; CLI only reads input and emits stdout; opt-out tested above | Actual host consent, deletion and expiry not executed |

Synthetic six-outcome histories across three units exercise the gating logic; these are **not real baseline measurements** and do not validate calibration thresholds or schedule improvements. The comparison fixture is a four-person synthetic arithmetic example, not a powered study. No model-learned policy, causal estimator, confidence interval, live trial assignment, automated retention service, remote analytics, or bandit exists. UI, real learner outcomes, fresh host behavior and provider-side processing were not measured.

## Review and try

Read `skills/explore-next/references/personalization.md`, then run:

```sh
python skills/explore-next/scripts/personalize.py analyze evals/fixtures/personalization-empty.json
python -m unittest discover -s evals -p 'test_*.py' -v
```

No vault schema/template properties changed; no migration needed. Release metadata and the template version are synchronized at 1.4.0-experimental.3. Policy outputs are derived and reversible. The existing state reducer and rules-1 selector remain unchanged. Difficulty is applied only after explicit learner acceptance through a new selection snapshot. Shadow schedules never change review dates. Adaptive deployment and bandits remain gated by actual baseline collection and a reviewed, consented comparison; implementation alone cannot supply that evidence.

## Publication

The user explicitly requested this release as a continuation on the same day as earlier experimental builds, continuing the previously authorized exception to the daily release limit. Experimental.1 and experimental.2 remain unchanged. Fresh installed-host scenario execution remains unverified as detailed above; executable regression coverage and limitations are included in the PR and release notes.
