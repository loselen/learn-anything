# Changelog

## 1.4.0

- Stable release of the SQLite learning memory from experimental.4–5: bounded context, one transactional save per turn, derived progress, opt-in discovery and personalization, and make-activity across the learning skills.
- summarize-me writes a narrative root `my-summary.md` with a Mermaid progress graph per topic, built by the runtime. An older `My Summary.md` is kept and its owner text merged on the next request.
- Markdown migration covers stable 1.x vaults: archived lessons no longer block import, map goals and outcomes (with met dates) and own-words sections are imported, and old rules/templates stay as original bytes instead of searchable notes.
- Leaner hot path: shorter learning-folder rules, understand-me evidence moved to a reference, duplicated key-check text trimmed, cached record schemas, and `legacy.py` no longer copied into each learning folder.
- Exports color map nodes and skip edges to capabilities outside the topic.
- Agent-session evals are run by the owner and no longer ship in skill packages.

## 1.4.0-experimental.5

- Enforce fresh independent evidence, transfer-only repair, required revisions and predeclared conditional slip rechecks.
- Preserve hinted active prompts, link attempts to sessions, honor explicit context scope, and allow note archival without editing content.
- Make initialization retryable and refuse database symlinks; add index-only updates and batched Markdown export queries.
- Add read-only SQLite projections for opt-in selection and frozen-baseline analysis, and build release packages into fresh directories with tag/version checks.
- Add live-runtime audit regressions; historical Markdown tests remain separately labeled. No real learning vault was migrated during development.

## 1.4.0-experimental.4

- SQLite is the main learning memory: bounded context, one transactional turn save, retry IDs, derived progress and map classes. No per-turn Markdown bookkeeping.
- Obsidian is an optional one-way export; legacy Markdown imports preserve originals without inventing verified historical assessments.
- Add summarize-me: explicitly requested root `My Summary.md` snapshots, never automatic lesson/startup updates.
- Rename setup-obsidian → setup-learning, update-vault → update-learning, ask-obsidian → ask-memory.
- Include stable 1.3.1's make-activity and its caller handoffs. Apply activity design inline; avoid repeated planning, research, scoring and personalization on ordinary turns.
- Keep experimental.3's discovery and baseline-gated personalization as opt-in workflows.

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


## 1.3.1

- Add make-activity for aligned diagnostics, practice, retries, transfer checks and test questions.
- Goal checks, placement, teaching, testing and smaller-task support share the activity designer while retaining their own pacing, hint and evidence rules.
- Activity design is a practical synthesis, not a validated framework.

## 1.3.0

- test-me asks one question at a time and gives feedback after each answer.
- Spaced review works past the first pass: the dashboard lists due `solid` lessons, and a new `interval` property tracks the 3, 7, 30, 90 day ladder.
- clarify-goal opens with an easier task before the goal task.
- Level checks set lesson statuses, so known nodes show as solid on the map.
- Lessons end with an optional own-words summary, saved under `## In my words`.
- teach-me and test-me check answer keys before using them.
- Skills work when installed alone; update-vault asks before updating skills.
- Run `Update my learning vault` to get the new dashboard, template and rules.
