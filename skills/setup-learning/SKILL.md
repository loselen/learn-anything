---
name: setup-learning
description: Set up local SQLite learning memory, with optional Obsidian export. Use when someone asks to create, connect or set up a learning folder or vault. Replaces setup-obsidian; no Obsidian app is required.
license: MIT
compatibility: Python 3.10+ with SQLite and write access to a local folder. PyYAML is needed only to import old Markdown.
---

# Set up learning

1. Use the requested learning folder; ask only if its location is unknown. Never use this repository as a personal learning folder unless explicitly requested.
2. If `.learning/memory.sqlite3` exists, read its `AGENTS.md`, run `context`, and stop; offer `update-learning` only if outdated. For an existing Markdown learning vault, use `update-learning` instead.
3. Run `python <this-skill>/scripts/memory.py --root PATH init`. It refuses existing rules or memory, creates the database, installs the small runtime in `.learning/`, and copies `AGENTS.md` and `CLAUDE.md`. No lesson files, templates, exports or summary are generated.
4. If unrelated rules already exist, preserve them. Use `init --database-only`, then merge the learning rules with permission; don't overwrite custom rules. The runtime is still installed.
5. Confirm briefly and begin the requested learning task. Don't require a map or goal interview for a quick start.

Normal turns follow the installed rules. Read [the API](references/api.md) when constructing the first write. Obsidian is an explicit `export` to a new folder, not required setup. Without local execution, teach in chat and state the persistence limitation rather than handing over many files.
