# Experimental.5 release validation

Date: 2026-11-07. Release candidate: `v1.4.0-experimental.5`. Branch: `codex/experimental-5-reliability`; release PR targets the existing experimental branch, not stable/main. No production learning folder was used.

## Executed checks

| Check | Result |
|---|---|
| `python -m unittest discover -s evals -p 'test_*.py' -v` | 91 passed |
| Agent Skills reference validator | All 13 skills valid |
| `claude plugin validate .` | Passed; optional marketplace-install documentation advice only |
| `npx --yes skills add . --list` | Found 13 skills |
| Independent setup archive | Extract, initialize, context and integrity check pass with `python -S` |
| Package identity/tag safety | Current 13 packages only; mismatched tags/existing output directories refused; bytecode omitted |
| Version contract | Runtime, installed rules, marketplace and changelog agree on experimental.5; SQLite schema stays 1 |
| Release-note selection | Workflow selects the experimental.5 title and committed notes, including the acceptance-test warning |
| Active local documentation links | README, architecture, release validation and skill entrypoints resolve |
| `git diff --check` | Passed |

The suite includes eight explicitly historical Markdown reference tests. Other checks cover current SQLite behavior, optional helpers, packaging and integration; the total is not a count of conversational evaluations.

## Fresh-host scripted scenarios

All 51 cases in `scenarios.md` were attempted in separate fresh Claude Code sessions with disposable folders and skill archives built from this release candidate. The configured model reported `claude-opus-5-5`; no alternate model was selected. The harness installs only the named skill for standalone cases and retains prompts, tool events, transcripts, verdicts and any SQLite artifacts in `/tmp/opencode/experimental5-acceptance-b8njomud`.

**Result: zero accepted passes; 51 blocked/incomplete runs.** The host returned `You've hit your weekly limit · resets 9am (Asia/Jakarta)`. Scenario 3 produced a partial synthetic roleplay and self-reported checks, but exited nonzero and did not satisfy the complete harness contract; it is not counted as a pass. These are infrastructure/coverage failures, not evidence that all 51 product behaviors failed.

The owner explicitly chose **Publish prerelease** after being told that the fresh-host scenario requirement could not complete. This is a documented exception for experimental.5, not a silent waiver, passed acceptance gate or reason to describe the build as production-ready. The release PR records the same exception. See [scenario attempt record](transcripts/experimental5-scenarios.md).

The attempted protocol uses scripted synthetic roleplays with acceptance criteria available to the exercising agent, not blind learner conversations, an independent judge benchmark or evidence of learning gains. Missing exercise coverage is not treated as a pass. Fresh-host acceptance must be rerun when capacity is available.

## Scope and limits

The correctness changes and local runtime measurements are recorded in [the audit report](results-audit.md). Its timing table predates the release version bump and is a synthetic local run, not a before/after model-speed claim. Compatible indexes are installed explicitly through `optimize`; learning data and schema version are unchanged.

Semantic freshness, verification quality and full taught scope remain host assertions. SQLite is not encrypted. Summary publication is recoverable rather than a cross-filesystem transaction. Historical-grade reconciliation, deletion/reset and future-schema upgrades remain explicit maintenance. Stable/latest stays v1.3.1; this release must be marked prerelease and not latest.
