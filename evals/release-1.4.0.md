# 1.4.0

Learning memory moves from Markdown notes to one local SQLite database. Less bookkeeping between activities, more reliable progress.

## Changes

- **SQLite memory:** your agent reads a small, targeted context and saves each turn in one transaction. Progress, review schedules and map classes are derived from evidence, not rewritten by hand.
- **Readable summaries:** ask "summarize me" for a narrative `my-summary.md` with a progress graph per topic. It updates only when you ask.
- **Migration from 1.x vaults:** lessons, statuses, schedules, prerequisites, map goals, outcomes, own-words notes and archived lessons are imported. Original files are kept untouched.
- **Activities everywhere:** make-activity is shared by goal checks, placement, teaching and testing.
- **Optional extras:** explore-next for discovery and opt-in personalization; one-way Obsidian export.

## Install

```sh
npx skills add loselen/learn-anything
```

Or download the individual `.skill` assets.

## Upgrading from 1.3.x

1. Back up your vault.
2. Install the new skills and remove the retired `setup-obsidian`, `update-vault` and `ask-obsidian` folders.
3. Ask your agent: "Migrate my learning vault to SQLite." It previews the import, imports in one transaction, and leaves your Markdown in place.

Python 3.10+ with SQLite is enough. PyYAML is needed only for the migration.

## Limits

- Local files aren't encrypted; model-provider processing is separate.
- SQLite can't prove that an activity really tested transfer or that a key was honestly checked; those remain tutor assertions.
- Exports are one-way snapshots.
