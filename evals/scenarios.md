# Behavior scenarios

Run each scenario in a fresh agent session, in a scratch copy of a learning vault (run `Set up my learning vault` in an empty folder first). Record agent, model, date, and pass or fail with one line of notes per scenario in the pull request.

## 1. Test one question at a time
Setup: two lesson notes with `status: review` and `next_review` yesterday.
Learner: "Test me." Then answer: a correct answer, "idk", a wrong answer, a wrong answer.
Pass: the first reply holds exactly one question and no answers. Each later reply holds feedback and at most one new question. After the two misses in a row, the next question is the easiest left. The test note has `### Q1`, `### Q2`... under both `## My answers` and `## Results`, and a `### Summary`.

## 2. Reviews after the first pass
Setup: one lesson with `status: solid`, `interval: 7`, `next_review` yesterday.
Learner: "What's due?" then "Test me", and answer correctly.
Pass: the lesson shows in the dashboard's "Due for review" view. After the test it has `interval: 30` and `next_review` 30 days out.

## 3. Goal check opens easy
Learner: "I want to get better at statistics."
Pass: the goal question offers 2 or 3 example answers. The first task is easier than the goal task. No message holds both a goal question and a task.

## 4. Known nodes become solid
Learner: "Teach me the chain rule." Answer every power-rule item correctly with no hint.
Pass: the power-rule lesson note has `status: solid`, `interval: 30`, a `## Level checks` entry, and the map node has class `solid`.

## 5. Daunted learner
Learner: during a lesson, answer "idk", then "skip", then "I'm bad at this".
Pass: the next activity is smaller than the last. Feedback talks about the work, not the person. No message stacks more than one question.

## 6. Checked answer keys
Learner: "Teach me recursion in Python." Do the first predict-the-output activity.
Pass: when the agent can run code, the key in the `> [!success]- Answer` callout matches the code's real output.

## 7. Installed alone
Setup: install only `teach-me`.
Learner: "Teach me binary search."
Pass: no error about missing skills. The lesson opens with a task the learner can likely do and gives one activity per message.

## 8. Update asks first
Setup: a vault whose `Template version:` is older than the latest.
Learner: "Update my learning vault."
Pass: the agent asks once before running any install or update command, and the vault's notes are unchanged afterwards.
