# 1.4.0 experimental 4

SQLite-first learning memory, focused on reducing agent bookkeeping. Includes experimental.3 and stable 1.3.1's make-activity behavior.

## Changes

- SQLite is authoritative for notes, learning evidence, progress and session state. Normal teaching uses targeted context and one transactional turn save.
- No per-turn Markdown rewrites, map regeneration, automatic summary refresh, repeated contract loading or mandatory research/discovery/personalization.
- Obsidian is optional: export a one-way Markdown snapshot to a new folder when requested.
- New `summarize-me` writes root **My Summary.md** only on an explicit personal-summary request. It retains earlier snapshots and preserves owner-edited content.
- Storage skills are now `setup-learning`, `update-learning`, and `ask-memory`, replacing `setup-obsidian`, `update-vault`, and `ask-obsidian`.
- Thirteen independently packaged skills, including `make-activity` and its caller handoffs.

## Install

```sh
npx skills add https://github.com/loselen/learn-anything/tree/v1.4.0-experimental.4 --all
```

Or download the `.skill` assets for a compatible host. Remove the three retired storage skill folders when upgrading so old instructions don't compete with SQLite workflows. Stable/latest remains **v1.3.1**.

Ask your agent to set up a dedicated learning folder. Python 3.10+ with SQLite is sufficient for normal use. Existing Markdown vaults use update-learning's dry-run import; PyYAML is needed only for that migration. Back up real notes before experimenting. Obsidian isn't required.

## Validation and known limits

- **55 automated tests pass**, all **13 skills validate**, discovery finds all 13, and an independently extracted setup-learning package initializes and runs without third-party Python packages.
- A synthetic local run with 2,000 capabilities and 20,000 activities measured approximately 0.14 ms per targeted context read and 0.30 ms per turn save in-process; CLI startup raised a context read to about 63 ms. These numbers exclude model generation and host/tool latency; no end-to-end speedup is claimed.
- **Fresh installed-host/model conversations for the 44 behavior scenarios have not been completed.** Prompt behavior and end-to-end seamlessness remain experimental. Claude's plugin validation CLI was unavailable; package/schema checks ran programmatically instead.
- Markdown imports preserve original bytes and explicit metadata. Historical cycles/test prose remain legacy notes, not invented verified assessment records. Old active prompts retain references and require inspection before resuming.
- Summary publication is recoverable by retrying the same snapshot ID, not an atomic SQLite-plus-file transaction. Exports aren't synchronized back; imported prose may contain old keys.
- Unknown future SQLite schemas are refused. Already-applied grade corrections, deletion/reset and derived-data cleanup require explicit maintenance; automated historical rollback is not implemented.
- Local storage isn't encrypted; model-provider processing is separate. No production vault was modified during development.

See [architecture and schema](https://github.com/loselen/learn-anything/blob/v1.4.0-experimental.4/docs/sqlite-memory.md) and [full validation results](https://github.com/loselen/learn-anything/blob/v1.4.0-experimental.4/evals/results-sqlite.md) in the tagged source.
