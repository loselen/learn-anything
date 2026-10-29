---
name: update-vault
description: Update a learn-anything vault to the latest rules, templates and folders, keeping the user's notes and edits. Use when the user asks to update, upgrade or sync their learning vault, or after the skills were updated and the vault still has old files. For a new vault, use setup-obsidian.
license: MIT
compatibility: Requires write access to the vault folder, through local files or the Obsidian CLI. Without it, list the changes for the user to make.
---

# Update vault

Bring a vault set up earlier up to date. Notes are never deleted or rewritten.

## Steps

1. **Find the vault.** Ask for the folder, or use the current one. If its root `AGENTS.md` doesn't start with `# Learning vault rules`, it isn't a learn-anything vault. Offer `setup-obsidian` and stop.
2. **Update the skills.** Fetch the latest of all learn-anything skills from `github.com/loselen/learn-anything`, for example `npx skills add loselen/learn-anything`, or `claude plugin update learn-anything` in Claude Code. Then re-read this file and continue with the updated skills. If the update fails, say so and continue with the installed ones.
3. **Compare versions.** The vault's `AGENTS.md` has a `Template version: X.Y.Z` line. The latest is the same line in `../setup-obsidian/assets/AGENTS.md`. If they match, say the vault is up to date and stop. No line means a vault from before versions: treat it as unknown.
4. **Find the user's edits.** Compare each vault file with the latest in `../setup-obsidian/assets/`: `AGENTS.md`, `CLAUDE.md`, `Dashboard.base`, and the 3 templates in `Templates/`. To tell a user edit from an old default, also read the same files at the vault's version: `https://raw.githubusercontent.com/loselen/learn-anything/v<version>/skills/setup-obsidian/assets/<file>`. If that can't be read, treat every difference from the latest as a possible edit.
   - Same as the old default: update it without asking.
   - Differs from the old default: it holds user edits.
5. **Find structural changes.** Read the latest `AGENTS.md` for new or renamed folders, skills, templates, properties and sections. Adapt the vault to them:
   - Add what is new: folders, templates, rules, skill rows.
   - Keep what is old. Never delete, move or empty an existing folder or note. Leave renamed or retired things in place and list them at the end.
   - Notes: only add a property or section the new rules need. Never edit existing content.
6. **Ask before touching user edits.** If step 4 found any, show them in a few lines per file, then ask in one message which to keep, or whether to overwrite everything to match the latest. Wait for the answer. To keep an edit, apply the new changes around it. Don't ask about anything else.
7. **Apply.** Update the files, set `Template version:` to the latest, and add what step 5 found.
8. **Confirm** in a few lines: the old and new version, what changed, what was kept, and anything left behind for the user to review.

Without write access, give the user the list of changes instead.
