# Contributing to learn-anything

Conventions for AI agents and humans editing this repository.

## Layout

| Path | Contents |
|---|---|
| `skills/<name>/SKILL.md` | One skill per folder, in the [Agent Skills](https://agentskills.io) format |
| `skills/setup-obsidian/assets/` | Starter vault files. The vault's `AGENTS.md` holds its rules; `CLAUDE.md` only imports it. |
| `.claude-plugin/marketplace.json` | Lets Claude Code install the repo as a plugin |

`setup-obsidian` runs once, to set up a vault, and `update-vault` brings an older vault up to date. The other skills check for the vault's `AGENTS.md` and save to it.
| `docs/` | README banner and badges (text drawn as outlines, so they render the same everywhere) |

## Rules

1. Keep each `SKILL.md` short. Cut before you add.
2. Frontmatter may only use `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`. `name` must match the folder name.
3. Write for any agent. Don't assume a specific product.
4. `map-topic` runs the pipeline: `clarify-goal` → draft graph → `check-level` → final map. `teach-me` teaches after it, and `test-me` tests what was taught.
5. Use the shared vocabulary everywhere:
   - Node statuses: solid, shaky, ready next, not yet (Mermaid classes `solid`, `shaky`, `next`, `notyet`).
   - Knowledge kinds: procedure, principle, concept, structure, facts.
   - Lesson `status`: planned → learning → review → solid.
6. README and banner follow the loselen design system: "loselen" always lowercase, sentence case, as few words as possible, Blue 500 `#4A68E0` as the only accent, and no other brand names unless install steps need them.
7. On release, bump `Template version:` in `skills/setup-obsidian/assets/AGENTS.md` along with `marketplace.json`. `update-vault` relies on it.
8. If you rename a section, property or skill, update every skill, the vault `AGENTS.md`, the templates and the README.

## Check before committing

```sh
pip install skills-ref
for d in skills/*/; do agentskills validate "$d"; done
claude plugin validate .                     # Claude Code plugin
npx skills add . --list                      # should find 9 skills
```
