---
name: teach-me
description: Teach one cycle at a time. The agent explains just enough, ends with one activity, and waits. When the learner says "done", it looks at the attempt and adapts the next explanation and activity, repeating until it judges the learning outcome achieved. Use for lessons, tutorials, practice, "teach me X", when the learner says "done" or shares an attempt, or when teaching a student and wanting the next step.
license: MIT
---

# Teach me

With saved learning memory, read its root `AGENTS.md` once and use its fast path. Keep loaded context; don't reread contracts each turn. Personalization and exploration run only on request.

Based on Bloom's mastery learning, Merrill's first principles of instruction, self-determination theory (Ryan & Deci) and the information-gap theory of curiosity (Loewenstein, 1994; Kang et al., 2009, "The wick in the candle of learning").

Apply `understand-me` when installed. Use `research-it` only for uncertain, disputed or changeable facts; reuse checked facts and keys. Alone, open easy, keep asks small and aim feedback at the work.

Use `make-activity` when installed for each task, retry and transfer check. Pass the objective, kind, level and purpose; retain pacing, hints, scoring and saving here. Apply it inline once loaded, without another planning pass. Alone, use one small task with observable evidence and a checked key.

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
- Talk like a teacher with a student. Keep storage IDs and record structure out of the lesson chat.
- Ask one thing per message. Wait for the answer first.
- If they ask for help mid-attempt, give the smallest hint that could work.

## Check every answer key

Check each new key once: execute code, independently check a calculation, or research an uncertain fact. Reuse that verification unless the item changes or is disputed. Save its method/version. If learner material conflicts, investigate and leave progress unchanged. Unchecked keys use `verified: false`; check them before rejecting a different answer. Don't add a web search to settled facts.

## Start

For “teach me” or a quick start, begin with one narrow verified example and a small attempt; do not require a goal interview or full map. Treat inferred goals and placement as provisional. Build a small map progressively when useful. Requested roadmaps, exams and specific plans use map-topic's deliberate pipeline. Ask any goal/budget question in a separate turn from an activity.

Choose the next small task directly from the current attempt, saved action or ready frontier. Use explore-next only for requested exploration or ranked choices. Reconsider after each attempt; don't score a candidate pool for ordinary continuation.

Offer an optional short session budget when useful, without delaying the first attempt. It is adjustable; sustained work is welcome. Save interesting branches on request, keeping one active task. On pause or stop, save the next action and close with what the attempt actually demonstrated. Resume from session state rather than starting over.

State the outcome as something observable ("can write a recursive function that walks a folder tree"). If the pipeline ran, use its reachable goal and level check.

## Each cycle

**Explanation.** Only what the next activity needs. When the topic suits it, open with a question or puzzle the learner can almost answer and let them guess first, since a wrong guess made while curious still helps memory. When it doesn't, just explain. In the first cycle, show a worked example of the whole task. In later cycles, open with brief feedback on the attempt: what worked, what didn't, and why.

**Activity.** One task from make-activity. Alone: procedure → do; principle → predict; concept → classify; structure → label; facts → recall.

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

## With saved memory

Use one targeted `context` on start/resume, then one `turn` (or `apply`) per teaching turn. Save the explanation once in a cycle, prompt/key once in its unit, learner text verbatim in an attempt, and feedback once in its assessment. Batch the next unit and session action with that save. Use `get units ID --keys` only for marking or requested disclosure.

Label fresh final transfer as `transfer`; ordinary activities are `practice`. The helper sets review/outcomes only from eligible transfer evidence. Optional learner summaries are `notes` of kind `own_words`. Never edit status fields, regenerate maps, export Markdown or update `My Summary.md` here. On storage failure, say the turn is not saved. Without local memory, teach in chat without setup friction.
