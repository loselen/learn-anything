# Experimental.5: reliable local memory

## Design and implementation order

1. Start with experimental.3; include stable 1.3.1's make-activity behavior and handoffs.
2. Replace authoritative Markdown with one SQLite database and standard-library runtime.
3. Add a small hot path: bounded context once, then one atomic turn save.
4. Keep migration, exports, summaries, discovery and personalization off that path.
5. Change all skills to use the runtime, add summarize-me, and validate behavior and cost.

The goal is less agent bookkeeping, not more infrastructure. No server, MCP installation, vector database, ORM, background jobs, automatic summaries or two-way sync. SQL execution is not the expensive part being assumed here: fewer tool round trips, smaller reads and no graph/file rewriting are the intended improvements. Model generation and provider/tool latency remain outside the runtime's control.

## Storage

`.learning/memory.sqlite3` is authoritative; `.learning/memory.py` is the installed interface. Python 3.10+ with SQLite is sufficient. Database schema **1** is independent of old Markdown schema **2** and package version **1.4.0-experimental.5**.

| Tables | Responsibility |
|---|---|
| topics, capabilities, topic_capabilities, outcomes | Goals and reusable capability identity; evidence-derived progress |
| prerequisite_groups, prerequisite_members | AND-of-OR graph; foreign keys, cycle validation, derived readiness |
| units, cycles | Checked/versioned activities and one stored explanation |
| attempts, assessments, applied_evidence | Verbatim responses, superseding grades, once-only transitions |
| tests, test_items | Immutable blueprint and coverage locked on first response |
| sources, capability_sources, notes | References, own words and general notes |
| sessions, questions, recommendations | One active task, saved branches, opt-in replay |
| preferences, baselines | Explicit choices and frozen opt-in inputs |
| operations | Content-digested retry IDs and saved results |
| summary_snapshots | Explicit dated personal portraits with evidence and source revision |
| legacy_documents | Original imported Markdown bytes and hashes |

`schema.sql` is the exact field/constraint contract. Primary/foreign-key indexes support ID-based context, evidence joins, prerequisite lookups and due queues. Free-text search is bounded substring matching, not semantic retrieval or an unbounded agent file scan; it can scan text tables and is not promised to be constant-time. Add FTS only if measured vault sizes require it.

Experimental.5 retains schema 1: structured blueprints use the existing text field, and archival changes only note metadata. After an explicit runtime update, `optimize` installs compatible indexes without changing learning data or revision. Initialization journals file installation and publishes the database last; an interrupted install can be retried with the same command/version without overwriting owner edits.

WAL, foreign keys, a five-second busy timeout, full synchronization and `BEGIN IMMEDIATE` provide local transactions. Evidence, progress, outcomes, session state and retry records commit together. A stale revision or any failed constraint rolls the batch back. Append-only IDs prevent accidental overwrites. The database serializes writers; owner-edited external files are not covered by its transaction. Backups use SQLite's online backup API.

## Agent hot path

`context --capability ID` → explain/one activity → `turn`.

After an answer, reuse context and save the response, feedback, next activity and session in one `turn`. The result returns IDs and revision. Don't fetch context again unless it is missing, stale or a session resumes. Keys stay out of context; retrieve a specific key only if absent from the current marking context. Store content once; don't copy the whole chat into notes.

Derived views remove map synchronization. Standard status and interval rules remain; placement, practice, transfer and delayed retrieval are distinct. Evidence assertions still come from the tutor—SQLite cannot establish whether an activity really tested transfer. Existing experimental discovery/personalization helpers are retained, opt-in, and not automatically invoked on each lesson. make-activity is applied inline after loading, not a nested planning pipeline.

The runtime rejects missing revisions and repeated-unit independent evidence, preserves hint-only active tasks, and requires transfer to leave repair. Conditional slip rechecks must be linked in an immutable blueprint before the first attempt; they do not turn one successful placement response into two. SQLite projections for optional policies live in explore-next's `scripts/snapshot.py`; full taught scope and consent remain explicit host assertions. See [release validation](../evals/results-experimental.5.md).

## Optional outputs and migration

Obsidian is a read-only projection into a fresh directory. No per-turn exports or Markdown dependency. Owner changes in exports aren't silently imported. Original Markdown imports retain bytes and explicit state without manufacturing verified historical assessments; unresolved/ambiguous graph links fail preflight. Historical cycles/test prose remain searchable legacy notes, not guessed structured events. These notes may contain old keys: ordinary lesson context excludes legacy prose until explicitly read, and exports warn that original keys may remain. Existing legacy prompt references are saved for explicit resumption.

`My Summary.md` is the one intentionally maintained root Markdown output. summarize-me refreshes it only on an explicit request; no completion/startup/export hook exists. It is a current portrait from learning and other saved context, with evidence, uncertainty and explicit preferences—not inferred personality. DB snapshots preserve earlier summaries. Publishing the file after the DB commit is retryable; it is not falsely described as an atomic DB-plus-file transaction.

## Validation and limits

Automated tests cover transactions, retry/conflict safety, state transitions, tests, restart, migration, exports and summary isolation. The benchmark uses synthetic local data and reports runtime timing/returned bytes, not an unmeasured claim about end-to-end agent speed. Fresh-session conversational scenarios must still be checked with a chosen host/model before publishing; deterministic tests don't substitute for that.

No network memory service or analytics. Local files are not encrypted. Backups/exports and model-provider processing have separate privacy implications. Corrections after a grade has already changed scheduling, deletion and reset require explicit maintenance rather than a generic automatic rollback. Unknown future schema versions are refused; a future migration must be specified and tested before use.
