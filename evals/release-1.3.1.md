# 1.3.1 release checks

Date: 2026-11-05 (Asia/Jakarta). Implementation and local checks: Codex; exact model identifier unavailable.

## Scope

Renamed and synthesized activity-grammar-designer as make-activity. Direct callers: clarify-goal, check-level, teach-me, test-me and understand-me. map-topic reaches it through clarify-goal and check-level; research-it, ask-obsidian, setup-obsidian and update-vault do not generate learner activities. Existing note templates need no schema changes. The requested patch version is an explicit exception to the usual minor bump for vault-file changes.

## Local checks

| Check | Result |
|---|---|
| skills-ref validation | Pass, all 11 skills |
| skill-creator quick_validate.py | Pass, make-activity |
| claude plugin validate . | Pass |
| npx skills add . --list | Pass, 11 skills discovered |
| Marketplace and template versions | Pass, both 1.3.1 |
| Changelog entry | Pass |
| Release archives | Pass, all 11 built in dist/ and contents round-tripped |
| Badge SVG | Pass, XML parsed; digits remain outlined |
| git diff --check | Pass |

## Behavior scenarios

Behavioral scenarios were not run. The user explicitly waived this release gate and requested publication without external Claude evaluations. No behavioral pass is claimed.

| Scenario | Result |
|---|---|
| 1. Test one question at a time | Waived; not run |
| 2. Reviews after the first pass | Waived; not run |
| 3. Goal check opens easy | Waived; not run |
| 4. Known nodes become solid | Waived; not run |
| 5. Daunted learner | Waived; not run |
| 6. Checked answer keys | Waived; not run |
| 7. Installed alone | Waived; not run |
| 8. Update asks first | Waived; not run |
| 9. Activity alignment | Waived; not run |
| 10. Activity handoff | Waived; not run |
| 11. Activity designer installed alone | Waived; not run |

Release authorized by the user with the behavioral checks waived; local validation results above remain the verification evidence.
