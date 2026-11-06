# Experimental.4 validation

Date: 2026-11-06. Implementation/checks: GPT-6.1 Sol through OpenCode. Synthetic scratch folders only; no real learning vault was migrated. Branch: `codex/experimental-4-sqlite`, based on experimental.3, with stable 1.3.1's make-activity behavior integrated and trimmed for inline use.

## Executed

| Check | Result |
|---|---|
| `python -m unittest discover -s evals -p 'test_*.py' -v` | 55 passed |
| Agent Skills reference validator | All 13 skills valid |
| `npx --yes skills add . --list` | Found 13 skills |
| Version/schema/package checks | Plugin, rules, runtime and changelog agree on experimental.4; database schema 1 |
| Independent setup-learning archive smoke | Extract, initialize, context and integrity check pass with `python -S` (no installed packages) |
| Local package build | Built all 13 independent `.skill` archives in scratch storage |
| Active documentation links | No broken local links in README, architecture or skill entrypoints |
| `git diff --check` | Passed |

The suite retains experimental discovery/personalization and historical reducer regressions. New executable coverage includes:

- Compact turn → save → retry → restart → resume with keys omitted.
- Atomic evidence/progress/outcome/session updates, rollback on invalid input and process exit before commit, stale-writer conflicts and immutable evidence.
- Placement vs retention, transfer completion, due-date gating, 3/7/30/90 scheduling, failure/repair and no promotion from exposure, repeated disclosed prompts, disputed or partial work.
- AND/OR prerequisites, hard cycles, escaping OR alternatives, unknown references, rename and archived-prerequisite behavior.
- Predeclared test coverage locking and per-capability partial completion.
- Verbatim learner text and superseding unapplied assessments; already-applied corrections are refused pending explicit maintenance.
- Byte-preserving legacy import, dry-run validation, custom-property/raw retention, identical retry, changed-source rejection, preserved session references and failed-import rollback.
- Safe export names, fresh-target-only publication, structured keys omitted by default, opt-in key export and SQLite online backup.
- Explicit summary publication, evidence validation, stale context, owner-edited-file merge guard, snapshot retention, crash/retry publication and rejection of an older snapshot overwrite.
- No summary refresh from lesson completion, ordinary context/progress reads or export. No legacy answer prose in ordinary lesson context.
- Static checks for make-activity caller handoffs and explicit-only personal summary instructions.

## Local performance experiment

Command: `python evals/benchmark_memory.py`.

Environment: Linux x86_64, Python 3.14.3, SQLite 3.51.2. Synthetic data: 2,000 capabilities, 20,000 units/cycles/attempts/assessments, and 2,000 notes. Fifty in-process samples; five CLI startup samples. No network calls.

| Operation | Median | p95 | Returned bytes |
|---|---:|---:|---:|
| Targeted capability context | 0.140 ms | 0.197 ms | 8,801 |
| Due queue | 0.413 ms | 0.676 ms | 2,160 |
| Free-text substring search | 3.417 ms | 4.105 ms | 112 |
| Atomic answer turn save | 0.296 ms | 0.377 ms | — |
| CLI context including Python startup | 63.180 ms | — | — |

These are one local synthetic run, not a Markdown comparison, host tool-latency benchmark, learner study or model-response speedup claim. Free-text search still scans text tables. Normal ID lookups and joins are indexed. The main workflow reduction is structural: one initial targeted read and one batched save per ordinary turn, with no Markdown/graph/summary regeneration or opt-in analysis in between.

## Not claimed / remaining validation

- `claude plugin validate .` was not run: that CLI is unavailable here. Plugin JSON and skill/package invariants were checked programmatically.
- Fresh installed-host conversations for all 44 scenarios in `scenarios.md` have **not** been run for this revision. Existing experimental transcripts remain historical, not evidence of the new SQLite prompts.
- Three summarize-me case folders cover a grounded portrait, no automatic refresh and an owner-edited snapshot. They are ready for host evaluation; no with/without-skill model benchmark or judge scores are claimed.
- Publication is handled separately by the tag-triggered release workflow. No production-vault migration was performed. Fresh-host conversational acceptance remains open and is disclosed in the prerelease notes.
- Markdown import preserves historical prose and explicit metadata; it does not parse every old cycle/test into trustworthy typed evidence. Legacy active prompts retain references and need inspection on first resume.
- SQLite and Markdown publication aren't one cross-file transaction. Summary snapshots commit first, then publish recoverably by ID. Owner file edits are guarded; arbitrary external editor races cannot be fully excluded.
- Full schema migration beyond SQLite schema 1, automatic rollback of already-applied historical grades, automated deletion/reset, semantic search and bidirectional Obsidian sync are intentionally not implemented.
