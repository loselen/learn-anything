# learn-anything

**Agent skills that turn your AI assistant into a one-on-one teacher.**

Tell your agent *"I want to learn X"*. Instead of dumping an explanation, it acts like a good tutor:

1. **Finds out what you actually want.** "Learn Python" might really mean "automate my weekly spreadsheet report". If the goal is too far away, it scopes it down to a first milestone you can reach.
2. **Checks where you are now.** It asks a few short questions and has you solve things, rather than trusting "I know the basics".
3. **Draws a map.** It builds a short path of topics from what you already know to your goal, skipping what you've shown you know.
4. **Teaches one topic at a time.** Each topic starts with clear outcomes ("by the end you'll be able to …"). The agent teaches in small steps, and every step ends with a short activity. It checks your answers, gives hints instead of answers, and moves on only when you've shown you can do it.

It all happens in normal chat. Your progress is saved in a small local SQLite database, so you can pick up later.

> **Status: 0.1.0, the first release.** Expect rough edges and fixes in upcoming versions. Feedback and issues are welcome.

## The skills

| Skill | What it does | Built on |
| --- | --- | --- |
| `clarify-me` | Turns "I want to learn X" into one observable, reachable goal; lowers it if it's too far | Backward design, goal-setting theory, proximal subgoals |
| `check-me` | Diagnoses current ability with a short adaptive set of questions | Knowledge Space Theory, adaptive testing, misconception diagnosis |
| `create-map` | Builds a personalized prerequisite map from current level to goal and saves it | Gagné's learning hierarchies, cognitive task analysis, 4C/ID |
| `teach-me` | Sets outcomes for a topic, teaches it in small steps with worked examples | Rosenshine's principles, worked examples, one-on-one tutoring research |
| `test-me` | Designs an activity per step, evaluates attempts, gives hints, decides when an outcome is met | Formative assessment, hinge questions, feedback research, mastery criteria |

Each `SKILL.md` lists the research it follows.

## Requirements

- An AI coding agent that supports [Agent Skills](https://agentskills.io), such as Claude Code, Codex or Cursor.
- `python3` with SQLite 3.37 or newer. Check with `python3 -c "import sqlite3; print(sqlite3.sqlite_version)"`. The database script uses only the Python standard library, so nothing else needs installing.

## Install

### 1. Add the skills

With the [`skills`](https://github.com/vercel-labs/skills) tool, from the project folder where you want to learn:

```bash
npx skills add loselen/learn-anything
```

Pick your agent when asked, or pass it directly, e.g. `npx skills add loselen/learn-anything -a claude-code`. Add `-g` to install for your user instead of one project. Install all five skills; they hand off to each other.

### 2. Add the flow to your agent instructions

The skills tool installs skills only, so you need to tell your agent when to use them. Paste this into your project's agent instruction file: `AGENTS.md` for most agents, `CLAUDE.md` for Claude Code.

```markdown
# Learning flow

When the user says they want to learn something ("I want to learn X", "teach me X", "help me get better at X"), act as their one-on-one teacher in a normal teacher–student conversation and follow these steps in order. Use each skill by name.

1. **clarify-me**: find what they really want to achieve and confirm one reachable goal. If the goal is too far, lower it to a first milestone.
2. **check-me**: diagnose their current level against that goal.
3. **create-map**: build a personalized map from the check-me result to the clarify-me goal, and save it.
4. **teach-me**: teach the map one node at a time. For each node, set the expected outcomes first, then teach in small steps, ending each step with an activity from **test-me**. Record and evaluate every attempt, and continue until the node's outcomes are met, then move to the next node.

Hand off between steps in the conversation without announcing skill names to the learner.

If the user comes back to continue learning, use **teach-me** to find their saved map and continue where they left off.
```

### 3. Start learning

Open your agent in that folder and say:

```
I want to learn X
```

## Where your progress is saved

Everything is stored in `.learn/learn.db`, a SQLite file in the folder where you run the agent. Add `.learn/` to your `.gitignore` if you don't want it committed.

What's saved:

- **maps**: your goal and where you started
- **nodes**: the topics on the map, their order and prerequisites, and the date each was created
- **outcomes**: what you should be able to do for each topic, and the date you met it
- **attempts**: each activity, your answer, and how it was judged

There are no spaced-repetition reviews. The only dates saved are when a topic is created and when an outcome is met.

The skills read and write the database through a bundled script, `scripts/db.py`. You can run it yourself too, e.g. `python3 .claude/skills/teach-me/scripts/db.py status` to list your maps. The exact path depends on your agent.

## Repository layout

```
skills/
  clarify-me/SKILL.md
  check-me/SKILL.md
  create-map/SKILL.md   scripts/db.py
  teach-me/SKILL.md     scripts/db.py
  test-me/SKILL.md      scripts/db.py
```

`scripts/db.py` is the same file in each skill that uses the database, so each skill still works if it's installed on its own. Keep the copies identical when changing it.

## License

[MIT](LICENSE)
