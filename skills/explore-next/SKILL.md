---
name: explore-next
description: Choose a useful next learning activity, explore a nearby application, or resume saved work. Use for “what next”, “surprise me”, “explore”, or a small learning session. Keeps the chosen goal and one active task; hands teaching and review to their existing skills.
license: MIT
---

# Explore next

Read [selection policy](references/selection.md) before recommending and [learner state](references/learner-state.md) before writing evidence. With a vault, follow its rules too.

1. Resume an unanswered active task before selecting another. Otherwise use the learner's chosen mode (continue, explore, review), consented topics and optional adjustable budget. Ask one cheap preference if these are unknown; never invent consent or difficulty from timing.
2. Gather candidates from the saved action, due review, repair, chosen goal's ready frontier, saved questions, nearby applications, and the [verified starter catalog](references/catalog.json). Search existing capabilities by ID/outcome before creating notes. The catalog is a small starting point, not a complete curriculum.
3. Apply hard eligibility before scoring. Use `scripts/select.py` with a JSON snapshot when execution is available; otherwise apply the same documented rules. Return a few understandable choices with plain reasons. Unknown prerequisites call for a bridge, diagnostic or clearly labeled preview, never a bypass.
4. Start only the learner's selected task. Use teach-me for practice/repair or test-me for due retrieval if installed; alone, give one checked activity, wait, and preserve hint/reveal distinctions. Reading or saving a preview is not an attempt. After feedback, mark the answered unit finished (or explicitly skipped) and decrement the batch count; leave a hint-only interaction active. Rebuild candidates after every answer; repeated misconceptions prioritize eligible repair instead of following an old queue.
5. Use a small batch with a clear endpoint. When it ends, close with actual evidence and a saved next action. Another batch is optional. A budget guides selection; learner-chosen sustained work may exceed it.

Save the policy version, candidate snapshot/digest, exclusions, feature scores, selected unit/version and reason in `## Recommendations` in `Sessions/Current.md`, without raw learner answers. The helper returns a digest; retain the exact input snapshot in a session-linked local file for replay. No remote logging. Without a vault keep this in the chat context and explain persistence limits.
