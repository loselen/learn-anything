---
name: explore-next
description: Explore nearby applications or rank checked activity choices on explicit request, such as “surprise me”, “explore” or “recommend a few options”. Ordinary continuation and resume use saved context directly, without this scoring workflow. Keeps one chosen goal and active task.
license: MIT
---

# Explore next

Use this full workflow only for requested exploration or ranked recommendations, not an ordinary next lesson. Read [selection policy](references/selection.md) once when needed; follow the learning folder's root `AGENTS.md` for SQLite writes.

1. Resume an unanswered active task before selecting another. Otherwise use the learner's chosen mode (continue, explore, review), consented topics and optional adjustable budget. Ask one cheap preference if these are unknown; never invent consent or difficulty from timing.
2. Gather candidates from the saved action, due review, repair, chosen goal's ready frontier, saved questions, nearby applications, and the [verified starter catalog](references/catalog.json). Search existing capabilities by ID/outcome before creating notes. The catalog is a small starting point, not a complete curriculum.
3. For explicit personalization, read [measurement and suggestions](references/personalization.md); keep defaults until its baseline and consent gates pass. Apply hard eligibility before scoring. Use `scripts/select.py` with a JSON snapshot when execution is available; otherwise apply the same documented rules. Return a few understandable choices with plain reasons. Unknown prerequisites call for a bridge, diagnostic or clearly labeled preview, never a bypass.
4. Start only the learner's selected task. Use teach-me for practice/repair or test-me for due retrieval if installed; alone, give one checked activity, wait, and preserve hint/reveal distinctions. Reading or saving a preview is not an attempt. After feedback, mark the answered unit finished (or explicitly skipped) and decrement the batch count; leave a hint-only interaction active. Rebuild candidates after every answer; repeated misconceptions prioritize eligible repair instead of following an old queue.
5. Use a small batch with a clear endpoint. When it ends, close with actual evidence and a saved next action. Another batch is optional. A budget guides selection; learner-chosen sustained work may exceed it.

Save the policy version, exact candidate snapshot, result/digest and reason in one SQLite `recommendations` record linked to the session, without raw learner answers. Store explicit preferences and frozen baselines in their tables; don't create sidecar Markdown/JSON files. Measurement remains opt-in and is never recalculated on every attempt. No remote logging. Without local memory, keep context in chat and explain persistence limits.
