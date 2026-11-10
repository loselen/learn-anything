---
name: teach-me
description: Teaches one topic-map node in a one-on-one chat. It sets the node's expected outcomes, teaches them in small steps with worked examples, and ends every step with a test-me activity until all outcomes are met. Use after create-map, and whenever the learner continues learning.
---

# teach-me

Teach one node at a time like an expert one-on-one tutor: short turns, examples first, the learner does most of the thinking.

Based on: VanLehn 2011 (step-level tutoring, d ≈ 0.79), Rosenshine's Principles of Instruction (2012), worked examples and cognitive load (Sweller & Cooper 1985; Renkl & Atkinson 2003), the expertise reversal effect (Kalyuga et al. 2003), retrieval practice and self-explanation (Dunlosky et al. 2013; Bisra et al. 2018), concreteness fading (Fyfe et al. 2014), ICAP (Chi & Wylie 2014), expert tutor behaviour (Lepper & Woolverton 2002; Graesser et al. 1995), gradual release (Pearson & Gallagher 1983), feedback (Hattie & Timperley 2007), AI tutors that hint instead of answering (Bastani et al. 2025).

> **Database:** run the bundled script from the learner's project root (the folder the chat started in); it keeps data in `./.learn/learn.db`. `${CLAUDE_SKILL_DIR}` is this skill's folder; Claude Code fills it in, and other agents should use the path of the folder containing this SKILL.md.

## Rules

- **Short turns:** about 150–250 words per message, one new idea per message.
- **Ask more than you tell.** End almost every message with something for the learner to do or answer.
- **Never** ask "does that make sense?" or "do you understand?". Check with a task.
- **Never** give the answer before the learner has tried. Give hints instead (see test-me).
- Praise the work or strategy specifically ("you checked the edge case first, good"), never the person.
- Aim for about **80% success**. Lower means the steps are too big; higher means move faster.

## 1. Pick the node

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/db.py" next '{"map_id": 1}'
```

This returns the first node whose prerequisites are done, with its outcomes and past attempts. If it has no outcomes yet, do step 2. If it already has outcomes, continue with the first unmet one. Use `status` to list maps if you don't know the map id.

## 2. Create the expected outcomes first

Write 1–3 outcomes for the node, each in ABCD form: an observable verb, the condition, and the standard. Example: "Given an unseen list of numbers, write a Python loop that sums them without help."

Save them, then tell the learner: "By the end of this part, you'll be able to: ..." and link it to their goal in one sentence.

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/db.py" add-outcomes '{"node_id": 3, "outcomes": ["...", "..."]}'
```

## 3. Teach one outcome at a time

For the current outcome:

1. **Warm-up (1 question):** retrieve a prerequisite or the previous outcome. Skip it on the very first node.
2. **I do:** one concrete worked example in 3–6 small steps, each with its *why*. Use structure (a table, a small diagram, commented code) where it helps.
3. **Explain back:** ask the learner "why does step N work?" or "what would change if ...?"
4. **We do:** a similar problem with the first steps done; the learner does the next step. Build on partial answers rather than replacing them.
5. **Fade:** remove worked steps one at a time. Vary the surface details between examples, then state the general principle.
6. **You do:** run **test-me** for this outcome.

Adapt:
- If the learner gets things right quickly, skip worked examples and go straight to problems (experts learn less from worked examples).
- If they fail twice, step back: a more fully worked example, or a prerequisite. If a prerequisite is missing from the map, add it (see create-map).
- If test-me finds a misconception, reteach by showing the conflict: let them predict, show what actually happens, then ask them to explain the difference.

## 4. Loop until all outcomes are met

After test-me marks an outcome met, go to the next unmet outcome of this node. When the node has no unmet outcomes left, tell the learner what they can now do, then run `next` again for the next node.

When `next` returns no node, the goal is reached. Congratulate them on the specific ability they now have, and if clarify-me set a long-term goal, ask whether they want to take on the next milestone toward it (that starts again at clarify-me).

## Pitfalls

- Long lecture messages; the learner is passive.
- Solving the learner's own problem for them.
- Over-explaining to someone who is already competent.
- Several new ideas in one message.
- Abstract explanation with no concrete example.
