# Changelog

## 1.3.1

- Add make-activity, adapted from activity-grammar-designer, for activities aligned with observable learning goals.
- Goal checks, level checks, lessons, tests and smaller retry tasks share its design process while keeping their pacing and standalone fallbacks.
- Add the skill to the vault rules and update the skill count to 11. No note schema changes.

## 1.3.0

- test-me asks one question at a time and gives feedback after each answer.
- Spaced review works past the first pass: the dashboard lists due `solid` lessons, and a new `interval` property tracks the 3, 7, 30, 90 day ladder.
- clarify-goal opens with an easier task before the goal task.
- Level checks set lesson statuses, so known nodes show as solid on the map.
- Lessons end with an optional own-words summary, saved under `## In my words`.
- teach-me and test-me check answer keys before using them.
- Skills work when installed alone; update-vault asks before updating skills.
- Run `Update my learning vault` to get the new dashboard, template and rules.
