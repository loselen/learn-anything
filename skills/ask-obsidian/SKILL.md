---
name: ask-obsidian
description: Answer questions about what's in the user's Obsidian vault ("what did I write about X", "what's due", "why do I keep failing Y", "what have I learned about Z") by narrowing with search, properties and links before reading. Use whenever the user asks about their vault or notes.
license: MIT
compatibility: Works best with file access to the vault or the Obsidian CLI (Obsidian 1.12+). Without access, it coaches the user through searches in Obsidian.
---

# Ask Obsidian

Narrow first, then read. Never read the whole vault.

## Access

| Access | How |
|---|---|
| Obsidian CLI (app running) | `obsidian search query="…"`, `obsidian read file="Note"`, `obsidian backlinks file="Note"`. Check `obsidian help` for the full list. |
| Files | Search the Markdown files directly. |
| None | Tell the user which searches to run in Obsidian. |

If the vault has an `AGENTS.md` at its root, read it first. It tells you where things live.

## Steps

1. **Classify** the question. Finding a note → search. Status → properties. Relationships → links. Summary → start at a hub note, such as a map note.
2. **Narrow** with search operators: `path:Lessons`, `tag:#topic`, `section:(term1 term2)`, `[status:review]`.
3. **Follow links** one or two hops: prerequisites, backlinks.
4. **Read** only the sections you need.
5. **Answer** with a `[[link]]` on every claim. If the vault doesn't contain the answer, say so.
