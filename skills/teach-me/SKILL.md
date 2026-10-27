---
name: teach-me
description: Teach one cycle at a time. The agent explains just enough, ends with one activity, and waits. When the learner says "done", it looks at the attempt and adapts the next explanation and activity, repeating until it judges the learning outcome achieved. Use for lessons, tutorials, practice, "teach me X", when the learner says "done" or shares an attempt, or when teaching a student and wanting the next step.
license: MIT
---

# Teach me

Based on Bloom's mastery learning, Merrill's first principles of instruction, self-determination theory (Ryan & Deci) and the information-gap theory of curiosity (Loewenstein; Kang et al.).

```
explain just enough → one activity → wait for "done"
        ↑                                    │
        └────────── adapt to the attempt ────┘
            until the outcome is achieved
```

## Rules

- Each message holds one explanation and **one** activity. Never write ahead.
- Stop after the activity. Give no answer until the learner says done.
- If the learner says "done" without sharing their work, read it from `### My attempt` in the vault note, or ask for it.
- Ask in one direction per message. Don't combine an open question with a next-lesson offer or confirmation. Wait for the answer first.
- If they ask for help mid-attempt, give the smallest hint that could work.

## Start

State the outcome as something observable ("can write a recursive function that walks a folder tree"). If the pipeline ran, use its reachable goal and level check.

## Each cycle

**Explanation.** Only what the next activity needs. Open with a question or puzzle the learner can almost answer, and ask them to guess before you explain. A wrong guess made while curious still helps memory. In the first cycle, show a worked example of the whole task. In later cycles, open with brief feedback on the attempt: what worked, what didn't, and why.

**Activity.** One task, matched to the kind of knowledge:

| Kind | Activity |
|---|---|
| procedure | Do it on a new case (coding: build something; math: solve a problem) |
| principle | Predict an outcome, or find a bug |
| concept | Classify an example |
| structure | Label the parts |
| facts | Recall them |

**Adapt** the next cycle to the attempt:

| Attempt | Next cycle |
|---|---|
| Correct and confident | Move on, or make it harder |
| Correct with a hint | Similar activity, less help |
| Same mistake repeated | Name the wrong rule, show where it breaks, explain it a different way |
| Missing a prerequisite | Step back and teach that first |
| Works only in the familiar form | Same idea, new surface |

## Keep the learner motivated

- **Start with a quick win** just above their level, doable with about one hint.
- **Alternate stretch and consolidation.** After a hard cycle, give one where they use what they just learned at a comfortable level. Never two hard cycles in a row.
- **Make progress visible.** Name what they can do now that they couldn't before, with evidence.
- **Offer small choices**: one of two problems, a project theme, the next ready-next node.
- **End each session on a win plus an open question** that the next session will answer. Don't also ask whether to continue. Offer the next lesson in the next message.

Adapt to how they seem, too:

| Signal | Likely meaning | Next cycle |
|---|---|---|
| Fast, correct, flat | Too easy | Harder, or offer a choice |
| Asks "why" or "what if" | Curious | Follow the question briefly |
| Long pauses, then progress | Productive struggle | Don't rescue too early |
| Gives up, "I'm bad at this" | Too far | Step back to a smaller task they can win |
| Correct but slower each session | Tiring | Shorter cycle, consolidation, or a break |

When unsure, ask how it feels.

## When the outcome is achieved

Judge from the evidence across cycles. Before you call it, give one final activity unlike anything practiced. If they handle it, say so, summarize what they can now do, and offer the next milestone.

## With a learning vault

If the user has a learning vault (a folder whose root `AGENTS.md` starts with `# Learning vault rules`), follow its rules and save each cycle as it happens:

- When a cycle starts, append `## Cycle N · YYYY-MM-DD` to the lesson note with `### Explanation`, `### Activity` and an empty `### My attempt`. On cycle 1, set `status: learning`.
- When the learner says done, read `### My attempt`, then append `### Analysis`. End the analysis by judging the outcome: met or not yet, with the evidence.
- If you judge it met, do all of this in the same turn as the analysis, without asking:
  - Set the lesson `status: review`, `last_reviewed` to today and `next_review` 3 days out.
  - In the map note's `## Outcomes`, set the matching row to `met YYYY-MM-DD`. If no row matches, add one.
  - Regenerate the map's node classes as the vault rules say.
- Never wait for the learner to say the outcome is met. Never end a turn that judged it met with the vault unchanged.
