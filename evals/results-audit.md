# Unreleased audit fixes

Date: 2026-11-07. Branch: `codex/experimental-4-sqlite`. Implementation and checks: GPT-6.1 Sol Fast through OpenCode. Synthetic scratch memory only; no production learning folder, historical release, tag or installed user skill was changed.

This records the pre-release audit state. See [experimental.5 release validation](results-experimental.5.md) for the subsequent release decision and the explicitly disclosed blocked fresh-host scenario run.

## Validation

| Check | Result |
|---|---|
| `python -m unittest discover -s evals -p 'test_*.py'` | 91 passed, including 36 added regressions/integration checks |
| Agent Skills validator | All 13 valid; validator installed in an isolated scratch environment |
| `claude plugin validate .` | Passed; advisory about an optional marketplace install line only |
| `npx --yes skills add . --list` | Found 13 skills |
| Package build/tag guard | Fresh-directory builds contain exactly the current 13 skills; wrong tags and existing outputs are rejected; no bytecode included |
| Independent setup archive | Extracted archive initializes and reads working memory with `python -S` |
| `git diff --check` | Passed |
| Active local documentation links | README, architecture and skill entrypoint links resolve |

Eight suite tests are explicitly historical Markdown reference checks, not current-runtime evidence. The other tests cover current SQLite behavior, optional helpers, packaging and integration. Passing tests do not establish every conversational behavior.

## Audit disposition

- **Evidence:** placement cannot reschedule repair; delayed retrieval cannot clear repair; only fresh successful transfer can. Repeated attempts on a used unit do not establish independent evidence. Summaries and optional projections expose reuse.
- **Slip rechecks:** immutable structured blueprints link conditional rechecks before exposure. One later independent successful recheck can resolve one slip, not a bug or multiple failures. The exception does not apply to placement/transfer. Missing/supported needed coverage stays unchanged; unused conditional items do not block success. Applied original/recheck grades remain correction-protected.
- **Continuity:** hint/disclosure-only exposure keeps the question active; replacement requires an answer or explicit skip. Compact turns attach attempts to their session. Explicit topic/capability context is honored while retaining the active prompt reference.
- **API:** revisions are required on ordinary writes; identical retries still work. Note content/timestamps remain immutable while archival metadata can change. Session evidence supplied to summaries can be cited.
- **Initialization:** database symlinks are refused before connection. A journal permits retry after file-installation failure or process exit, with the database published last and owner edits protected. New-file publication does not replace a concurrently appearing file.
- **Optional policies:** a read-only SQLite adapter projects selected prerequisite closure, candidate-specific seen IDs and current due/repair roles. Observation exports combine verification, exposure/reuse and recorded teaching delay, omit raw responses/keys, reject superseded/out-of-topic evidence, and check frozen baselines. Consent and full taught scope remain explicit host assertions. Helpers accept stdin; nothing runs automatically per turn.
- **Cost:** compatible evidence indexes have an explicit index-only update command; exact duplicate checks avoid decoding unrelated history. Title edits skip graph validation. Markdown export prefetches grouped rows; query count does not grow per unit/attempt. Benchmarks now include next cycles, actual transitions, placement aggregation and graph validation.
- **Instructions/packages:** repeated activity handoffs were shortened while preserving standalone fallbacks. update-learning explicitly requires the matching setup-learning package. Historical tests are labeled separately. Release builds use a new directory and compare the tag with runtime/rules/package versions. Ignored historical `dist/` artifacts are left untouched and are no longer a publication source.

## Synthetic runtime measurements

Command: `python evals/benchmark_memory.py`. Linux x86_64, Python 3.14.3, SQLite 3.51.2. Initial data: 2,000 capabilities, 20,000 units/cycles/attempts/assessments, 2,000 notes. Fifty samples per operation; five CLI startup samples. Timed writes build new cycles/units and accumulate evidence; transfer and delayed sequences assert a real capability update on every sample.

| Operation | Median | p95 |
|---|---:|---:|
| Targeted context (8,801 returned bytes) | 0.271 ms | 0.339 ms |
| Due queue | 0.809 ms | 1.216 ms |
| Substring search | 6.397 ms | 7.840 ms |
| Practice answer + next cycle | 0.797 ms | 1.248 ms |
| Transfer answer + next cycle | 0.853 ms | 1.112 ms |
| Due retrieval + next cycle | 0.942 ms | 1.350 ms |
| Placement answer + next cycle | 1.269 ms | 2.003 ms |
| New capability first turn + graph validation | 3.391 ms | 4.044 ms |
| CLI context including process startup | 124.159 ms | — |

These are synthetic local measurements, not a controlled before/after speed comparison or a host/model latency claim. The placement sequence preserves an existing solid schedule; its recorded capability updates are placement metadata, not review advances. The earlier experimental.4 timing table remains a historical measurement of its narrower workload.

## Remaining acceptance work

- Fresh installed-host conversations for the 51 scenarios in `scenarios.md` have not been run for these changes. No with/without-skill model benchmark or conversational pass rate is claimed.
- No release was made. Version strings remain experimental.4 until the next separately validated, versioned release; the existing tagged install does not contain these fixes. Database schema remains 1; compatible indexes are installed explicitly with `optimize` after a runtime update.
- SQLite cannot prove semantic freshness, honest verification or full taught scope. These remain tutor assertions. Arbitrary external editor races are not a cross-filesystem transaction.
- Automatic historical-grade reconciliation, deletion/reset automation, encryption, semantic search and two-way Markdown synchronization remain deliberately out of scope.
