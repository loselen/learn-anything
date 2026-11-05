---
name: teach-me
description: Teach one cycle at a time. The agent explains just enough, ends with one activity, and waits. When the learner says "done", it looks at the attempt and adapts the next explanation and activity, repeating until it judges the learning outcome achieved. Use for lessons, tutorials, practice, "teach me X", when the learner says "done" or shares an attempt, or when teaching a student and wanting the next step.
license: MIT
---

# Teach me

Read [the shared state contract](references/learner-state.md) before placement, evidence, scheduling or session writes. With a vault, also follow its rules.

Based on Bloom's mastery learning, Merrill's first principles of instruction, self-determination theory (Ryan & Deci) and the information-gap theory of curiosity (Loewenstein, 1994; Kang et al., 2009, "The wick in the candle of learning").

Load `understand-me` and `research-it` first if you haven't this session and they are installed. If not, still open easy, keep each ask small, aim feedback at the work, and check facts you are unsure of.

```
explain just enough → one activity → wait for the attempt
        ↑                                    │
        └────────── adapt to the attempt ────┘
            until the outcome is achieved
```

## Rules

- Each message holds one explanation and **one** activity. Never write ahead.
- Stop after the activity. Don't add "say done when you're ready" or any similar prompt. Give no answer until the learner shares an attempt or requests disclosure; record disclosure as exposure.
- If the learner says "done" without sharing their work, ask for it.
- Talk like a teacher with a student. Don't show cycle numbers or section labels in chat. That structure belongs in the vault note.
- Ask one thing per message. Wait for the answer first.
- If they ask for help mid-attempt, give the smallest hint that could work.

## Check every answer key

Before you save or use a key, check it: run code if you can execute it, solve a calculation a second way, and run facts through `research-it`. Record how the key was verified and its version. If learner material conflicts with a checked key, investigate; quarantine disputed items and leave affected state unchanged. If you can't check a key, mark it `unverified` in its callout, and re-check before marking a different answer wrong.

## Start

For “teach me” or a quick start, begin with one narrow verified example and a small attempt; do not require a goal interview or full map. Treat inferred goals and placement as provisional. Build a small map progressively when useful. Requested roadmaps, exams and specific plans use map-topic's deliberate pipeline. Ask any goal/budget question in a separate turn from an activity.

When choosing a next activity, use explore-next if installed; otherwise offer a ready next task or saved action with a plain reason. Reconsider after each attempt instead of following a stale queue.

Offer an optional short session budget when useful, without delaying the first attempt. It is adjustable; sustained work is welcome. Save interesting branches on request, keeping one active task. On pause or stop, save the next action and close with what the attempt actually demonstrated. Resume from session state rather than starting over.

State the outcome as something observable ("can write a recursive function that walks a folder tree"). If the pipeline ran, use its reachable goal and level check.

## Each cycle

**Explanation.** Only what the next activity needs. When the topic suits it, open with a question or puzzle the learner can almost answer and let them guess first, since a wrong guess made while curious still helps memory. When it doesn't, just explain. In the first cycle, show a worked example of the whole task. In later cycles, open with brief feedback on the attempt: what worked, what didn't, and why.

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
- **Close with evidence**: optional own-words summary, a saved next action, and a satisfying stop. Offer continuation without pressure; an early stop needs no invented success.

Adapt to how they seem, too:

| Signal | Likely meaning | Next cycle |
|---|---|---|
| Says “too easy” | Wants more challenge | Harder, or offer a choice |
| Asks "why" or "what if" | Curious | Follow the question briefly |
| Requests time | Wants space | Let the attempt continue |
| Gives up, "I'm bad at this" | Too far | Step back to a smaller task they can win |
| Requests a shorter session | Less time | Consolidation or a saved stopping point |

When unsure, ask how it feels.

## When the outcome is achieved

Judge from the evidence across cycles. Before you call it, give one final activity unlike anything practiced. If they handle it independently without hints or disclosure, say so, then ask for one or two sentences on the idea in their own words. Skipping is fine. After they reply, name what they can now do and save the next action. Close there or offer optional continuation.

## With a learning vault

If the user has a learning vault (a folder whose root `AGENTS.md` starts with `# Learning vault rules`), follow its rules and save each cycle as it happens:

- When a cycle starts, append `## Cycle N · YYYY-MM-DD` to the lesson note with `### Explanation`, `### Activity` and an empty `### My attempt`. On cycle 1, set `status: learning`.
- Put the activity's answer in a collapsed `> [!success]- Answer` callout under `### Activity`, in chat only if explicitly requested.
- When the learner shares their attempt in chat, copy it verbatim under `### My attempt` of the current cycle before anything else.
- Then append `### Analysis`. End the analysis by judging the outcome: met or not yet, with the evidence.
- If you judge it met, do all of this in the same turn as the analysis, without asking:
  - Clear `repair`, set the lesson `status: review`, `interval: 3`, `last_reviewed` to today and `next_review` 3 days out.
  - In the map note's `## Outcomes`, set the matching row to `met YYYY-MM-DD`. If no row matches, add one.
  - Regenerate the map's node classes as the vault rules say.
- When the learner gives their own-words summary, append it verbatim under `## In my words`.
- Never wait for the learner to say the outcome is met. Never end a turn that judged it met with the vault unchanged.
