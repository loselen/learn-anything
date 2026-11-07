# 1.4.0 experimental 5

More trustworthy learning memory, with less bookkeeping. This prerelease builds on experimental.4; stable/latest remains **v1.3.1**.

## Changes

- **More accurate progress:** reused questions cannot advance independent retention; placement cannot bypass repair; fresh successful transfer is required to leave repair. Conditional slip rechecks are linked before the test begins.
- **Reliable continuity:** hints keep the current question active, answers retain their session link, and explicit topic queries return the requested topic. Notes can be archived without changing the owner's text.
- **Safer setup:** interrupted initialization can be retried, owner edits stay protected, and unsafe database symlinks are refused. Ordinary saves require a revision to prevent stale writes.
- **Less unnecessary work:** indexed evidence checks, no full graph validation on renames, batched exports, shorter repeated activity instructions, and read-only SQLite adapters for optional discovery/personalization.
- **Safer distribution:** fresh package directories and tag/version checks prevent stale or mislabeled archives. All 13 skills remain available.

## Install

```sh
npx skills add https://github.com/loselen/learn-anything/tree/v1.4.0-experimental.5 --all
```

Or download the individual `.skill` assets for a compatible host. Install experimental separately from stable. When upgrading from an older Markdown-based release, remove the retired setup-obsidian, update-vault and ask-obsidian skill folders so their instructions do not compete with SQLite.

## Existing experimental.4 memory

Back up the learning folder before experimenting. Install the matching setup-learning and update-learning packages, then ask your agent to update the learning memory. The upgrade backs up SQLite, compares/copies the matching runtime, preserves owner-edited rules, runs `optimize` for compatible indexes, and checks/resumes memory. **Database schema remains 1; no data rebuild or Markdown reimport is required.** Python 3.10+ with SQLite is enough. PyYAML is needed only for importing older Markdown vaults.

## Validation and limits

- **91 automated tests pass**, including 36 audit regressions/integration checks. All **13 skills validate**, discovery finds all 13, plugin validation passes, and an extracted setup-learning archive runs with `python -S`.
- **Fresh-host acceptance remains incomplete.** All 51 scenario runs were attempted, but the host hit its weekly usage limit; zero runs qualify as accepted passes. One partial roleplay was retained, not counted as a pass. Publication proceeds with the owner's explicit approval of this disclosed prerelease validation gap. These attempts are not a learner study or a blind conversational benchmark.
- SQLite cannot prove semantic freshness, honest verification or full taught scope; those remain tutor assertions. No end-to-end model-speed or learning-gain improvement is claimed.
- Local files are not encrypted. Model-provider processing is separate. Summary publication is recoverable, not an atomic database-plus-file transaction. Exports remain one-way snapshots.
- Already-applied historical grade corrections and deletion/reset require explicit maintenance. No automatic historical rollback or future-schema migration is invented. No production learning vault was modified during development.

See [release validation](https://github.com/loselen/learn-anything/blob/v1.4.0-experimental.5/evals/results-experimental.5.md), [changes](https://github.com/loselen/learn-anything/blob/v1.4.0-experimental.5/CHANGELOG.md) and [the memory API](https://github.com/loselen/learn-anything/blob/v1.4.0-experimental.5/skills/setup-learning/references/api.md).
