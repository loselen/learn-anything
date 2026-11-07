---
name: update-learning
description: Upgrade learning memory or migrate an older Markdown learning vault to SQLite without rewriting the original notes. Use for update, upgrade or migration requests. Replaces update-vault. For a new folder use setup-learning.
license: MIT
compatibility: Python 3.10+ with SQLite and local write access; Markdown import additionally requires PyYAML.
---

# Update learning

1. Find the learning folder and read its rules. This skill requires the matching setup-learning package's runtime/assets. If absent, ask before installing that exact version; an explicit installation request suffices. Keep the installed version if declined. Never silently fetch stable/main or guess replacement runtime files.
2. For a Markdown vault, follow [migration](references/migration.md): dry run, initialize an empty destination database, import in one transaction, validate, and only then switch the rules. Preserve user edits and all original files. Never treat imported prose as newly verified retrieval.
3. For existing SQLite memory, back up with `backup NEW_PATH` first. Check the schema version against setup-learning's runtime. This experimental release supports schema 1 only; refuse unknown versions rather than applying guessed SQL migrations.
4. Copy the matching runtime (`memory.py`, `legacy.py`, `schema.sql`) from setup-learning to `.learning/`, comparing existing copies before replacement. Merge new `AGENTS.md` rules around owner edits; ask if a conflict needs a choice. Don't rerun `init` or rebuild notes.
5. Run `optimize` to add compatible indexes, then `check` and `context`. Advance the rules' template version only after success. Report the version, kept files and any unresolved legacy prompt briefly. Don't export or refresh `My Summary.md`.
