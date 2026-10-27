---
name: setup-obsidian
description: Set up an Obsidian vault for learn-anything, once. Creates the folders, the agent rules (AGENTS.md), the templates and the review dashboard. Use only when the user asks to set up, create or connect a learning vault. After setup, the other learning skills use the vault on their own.
license: MIT
compatibility: Requires write access to the vault folder, through local files or the Obsidian CLI. Without it, give the user the files to copy.
---

# Set up Obsidian

Run once per vault. After that, the other skills read the vault's `AGENTS.md` and work in it directly.

## Steps

1. **Find the vault.** Ask for the folder, or use the current one if it holds a `.obsidian/` folder.
2. **Check for an earlier setup.** If the root `AGENTS.md` already starts with `# Learning vault rules`, the vault is ready. Say so and stop.
3. **Don't overwrite.** If an `AGENTS.md`, `CLAUDE.md` or template already exists with other content, show the user and ask before changing it. Offer to append the learning rules instead.
4. **Create the folders**: `Maps/`, `Lessons/`, `Tests/`, `Sources/`, `Templates/`, `Archive/`.
5. **Copy the files** from `assets/`:

   | File | Goes to |
   |---|---|
   | `AGENTS.md` | vault root |
   | `CLAUDE.md` | vault root (imports `AGENTS.md`) |
   | `Dashboard.base` | vault root |
   | `map-template.md`, `lesson-template.md`, `test-template.md` | `Templates/` |

6. **Confirm** in 1 line, and suggest a first step: "Your vault is ready. What do you want to learn?"

Without write access, give the user these files and the folder list to create.
