---
name: create-map
description: Builds a personalized topic map, a small ordered prerequisite graph of nodes from the learner's current ability (from check-me) to their confirmed goal (from clarify-me), and saves it to SQLite. Use after check-me, or when a map needs nodes added.
---

# create-map

Build the shortest path of teachable nodes from where the learner is to the goal.

Based on: Gagné's learning hierarchies (1968), Cognitive Task Analysis (Clark et al. 2008; Tofel-Grehl & Feldon 2013), 4C/ID whole-task sequencing (van Merriënboer & Kirschner 2018), revised Bloom's taxonomy (Anderson & Krathwohl 2001), Knowledge Space Theory's outer fringe, knowledge components (Koedinger et al. 2012).

> **Database:** run the bundled script from the learner's project root (the folder the chat started in); it keeps data in `./.learn/learn.db`. `${CLAUDE_SKILL_DIR}` is this skill's folder; Claude Code fills it in, and other agents should use the path of the folder containing this SKILL.md.

## Inputs

- the confirmed **goal** from clarify-me
- the **baseline** summary from check-me (solid / shaky / not yet / misconceptions)

## Procedure

1. **Root.** Put the goal at the top as a whole task.

2. **Decompose backward.** For the goal, and then for each new node, ask: "What must the learner already be able to do to perform this?" Also ask the expert questions people forget:
   - "What decisions, cues and checks does an expert use here?"
   - "What errors do beginners commonly make here?"

   Turn the hidden decisions into nodes or keep them in a node's title.

3. **Stop decomposing** a branch when it reaches something check-me marked **solid**. Don't put solid things on the map.

4. **Size each node right.** A node:
   - has one clear ability, stated as "can [verb] ..."
   - can be taught in one short lesson (about 5–20 minutes of chat)
   - will need at most 3 outcomes; if more, split it; if it can't be checked on its own, merge it

5. **Include the gaps.** Shaky items become short nodes. Misconceptions get their own node or are named in the title of the node that fixes them.

6. **Order.** Sort so every node comes after its prerequisites. Put "why it works" nodes just before the procedures that rely on them. Every few nodes, include a small whole-task node that combines the previous ones, so it never becomes a pile of fragments. The final node is the goal itself.

7. **Keep it small:** about 5–15 nodes. If you need more, the goal is too far. Go back to clarify-me and lower it.

8. **Show the map** as a short numbered path, then ask: "Does this path look right, or is there anything you already know or want to skip?" Adjust once.

9. **Save** after the learner agrees:

   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/db.py" new-map '{"goal": "<goal statement>", "baseline": "<check-me summary>"}'
   ```

   Then add all nodes in one call. `key` is any short label you choose; `requires` lists keys of prerequisite nodes in this same call (or ids of existing nodes):

   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/db.py" add-nodes '{"map_id": 1, "nodes": [
     {"key": "a", "title": "Can ...", "requires": []},
     {"key": "b", "title": "Can ...", "requires": ["a"]}
   ]}'
   ```

   Each node gets its creation date automatically. Pass the JSON on stdin with a heredoc if it contains quotes that are hard to escape.

## Changing the map later

If teaching reveals a missing prerequisite, add it with `add-nodes` (use the existing node's id in `requires` where it applies) and tell the learner briefly why.

## Pitfalls

- Following textbook order instead of what the goal needs.
- Nodes too big ("learn calculus") or too tiny (one definition).
- Re-teaching what the learner already showed is solid.
- A huge map that overwhelms the learner.
