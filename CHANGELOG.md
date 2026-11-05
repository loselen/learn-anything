# Changelog

## 1.4.0-experimental.3

- Phase E adds opt-in local baseline measurement, reversible difficulty suggestions and a shadow review scheduler.
- Fixed-policy comparison reports delayed outcomes, transfer, attrition and retained score relative to chosen time; no automatic promotion or bandit.
- Phase D is skipped. Adaptive use remains gated on actual baseline evidence and learner choice.

## 1.4.0-experimental.2

- Phase C adds explore-next, a five-unit verified starter catalog, and replayable rules-1 selection.
- Eligibility checks precede ranking; suggestions preserve topic consent, active tasks, review scope and session endpoints.
- Eleven independently packaged skills; continues experimental.1 without changing its tag or assets.


## 1.4.0-experimental.1

- Experimental phases A–B: stable capability IDs, explicit AND/OR prerequisites, independent evidence and visible failed-review repair.
- Quick start, adjustable session budgets, saved questions and next actions, and evidence-based closure.
- Additive migration helper and deterministic state checks; no real vaults modified.
- Placement now schedules a 3-day review instead of claiming 30-day retention.
- Discovery ranking, companion UI and adaptive personalization remain deferred.


## 1.3.0

- test-me asks one question at a time and gives feedback after each answer.
- Spaced review works past the first pass: the dashboard lists due `solid` lessons, and a new `interval` property tracks the 3, 7, 30, 90 day ladder.
- clarify-goal opens with an easier task before the goal task.
- Level checks set lesson statuses, so known nodes show as solid on the map.
- Lessons end with an optional own-words summary, saved under `## In my words`.
- teach-me and test-me check answer keys before using them.
- Skills work when installed alone; update-vault asks before updating skills.
- Run `Update my learning vault` to get the new dashboard, template and rules.
