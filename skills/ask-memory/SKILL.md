---
name: ask-memory
description: Answer questions about saved learning, notes, progress, due reviews or where to resume, using targeted SQLite queries. Use for questions about the learning folder or vault. Replaces ask-obsidian; Obsidian is optional. A personal snapshot request uses summarize-me instead.
license: MIT
compatibility: Python 3.10+ with local SQLite memory access. Without access, answer only from the available chat and state the limit.
---

# Ask memory

Read the learning folder's `AGENTS.md` once. Narrow before reading; never dump the database.

- Resume: `python .learning/memory.py context` returns the saved task/action.
- Due reviews: `due`. A specific lesson/topic: `context --capability ID` / `context --topic ID`.
- Find notes: `search "phrase"`, then `get TABLE ID` for the relevant record. Follow prerequisite or evidence IDs only as needed.
- Answer from saved evidence with compact `table:id` references. Distinguish placement, recently learned work and demonstrated retention. Say when the memory doesn't establish an answer.
- For a next-step choice use the saved action, repair or ready frontier directly. Use `explore-next` only for a requested exploration/recommendation workflow. Don't run scoring or personalization for ordinary queries.

This skill is read-only. A progress answer doesn't update `my-summary.md`; explicit “summarize me” requests hand off to `summarize-me`. Never run an export just to answer a question.
