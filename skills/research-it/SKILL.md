---
name: research-it
description: Decide whether a question needs research, then research it in two tiers, primary sources first and secondary sources only when the primary ones fall short. Use this skill whenever the user asks a factual question you cannot answer confidently from memory, asks about anything that may have changed since your training data (laws, prices, people in office, product versions, statistics, recent events), asks you to "look it up", "check", "verify", "find sources", "research", or "fact-check", or whenever you notice yourself about to guess. Also use it when the user asks for evidence, citations, or "what does the data say". In a learning vault, load it at the start of every session; step 1 decides whether a search is needed. Skip it for opinions, creative writing and facts you know with certainty.
license: MIT
---

# research-it

A three-step flow for answering questions accurately. You answer from memory when you can, go to primary sources when you can't, and add secondary sources only when the primary ones leave a gap.

## Step 1: Decide whether to research

Ask yourself two questions before you search anything.

1. Can I recall the answer?
2. Am I sure the answer is correct and still current?

If both answers are yes, answer directly and stop. Searching a settled fact (the boiling point of water, the year of the French Revolution) wastes the user's time.

Treat the answer as "not sure" and move to Step 2 if any of these apply:

- The fact can change over time: who holds an office, current law, prices, version numbers, statistics, company status.
- The question names something you only half recognize.
- You would need to pull a specific number, date, quote, or legal wording out of vague memory.
- The user's question contradicts what you remember, and you can't tell who is wrong.
- A wrong answer would cost the user something real: health, money, legal standing, safety.

Be honest with yourself here. A confident tone does not equal a correct answer.

## Step 2: Research primary sources

A primary source is the original record of the thing itself, produced by the people or bodies who made, measured, or decided it.

| Topic | Primary sources |
|---|---|
| Law and policy | The statute, regulation, court ruling, or official gazette text |
| Science and medicine | The original peer-reviewed study, trial registry entry, dataset |
| Statistics | The national statistics office, central bank, or agency that collected the data |
| Companies | Annual reports, regulatory filings (SEC, stock exchange), official press releases |
| Products and software | Official documentation, changelogs, release notes, spec sheets |
| Events and statements | Official transcripts, government announcements, the speaker's own published words |
| History | Original documents, archives, first-hand accounts |

How to search:

1. Write short queries that point at the source itself, for example "UU 27 2022 pelindungan data pribadi pasal 4" or "BPS inflation September 2026".
2. Open the page and read the relevant part. Snippets cut off context and often mislead.
3. Prefer official domains (.gov, .go.id, .int, journal sites, the company's own site).

Then judge what you found. Primary sources are **enough** when:

- They answer the question directly.
- You can read and interpret them without guessing.
- They are current, or the user asked about the period they cover.

If they pass all three, answer now. Primary sources are **not enough** when:

- You found nothing, or only part of the answer.
- The source has poor interpretability: dense legal language, raw data with no method notes, a study whose result needs field expertise to read, technical jargon you can't resolve with confidence.
- Two primary sources conflict and you can't settle which one applies.

In those cases, go to Step 3.

## Step 3: Add secondary sources

A secondary source interprets, summarizes, or analyzes primary sources. Good ones include review articles and meta-analyses, academic textbooks, reputable news outlets reporting on the primary record, law firm and expert commentary, and reports from established research institutions.

Use secondary sources to fill the specific gap you named in Step 2. If the primary source was hard to read, find an expert explanation of that same source. If the primary search came up empty, find who has reported or analyzed the topic and trace their claims back to an original where possible.

Avoid content farms, anonymous forums, SEO listicles, and AI-generated summary sites. Use them only when nothing else exists, and flag them when you do.

## Answering

Build the answer from everything you gathered, with the primary sources as the anchor.

- Lead with the direct answer.
- Mark which claims rest on primary sources and which on secondary interpretation. A short note works: "According to the regulation itself..." versus "Legal commentators read this as...".
- When a secondary source disagrees with a primary one, trust the primary source and mention the disagreement.
- State what you could not confirm. Leave gaps visible instead of filling them with guesses.
- Cite every source you relied on.

## Example

User asks: "What's the maximum fine under Indonesia's personal data protection law?"

1. You remember the law exists (UU 27/2022) but not the exact figure. Not sure, so research.
2. Search the law's text on an official government site. You find the article on administrative fines and read it. The text states the fine as a percentage of annual revenue, which answers the question, so you stop here and answer with the article number.
3. If the article had pointed to an implementing regulation you couldn't find, you would search for legal commentary explaining how the fine applies, then answer, labeling which part came from the law and which from commentators.

## With a learning vault

If the user has a learning vault (a folder whose root `AGENTS.md` starts with `# Learning vault rules`), follow its rules and save what you relied on:

- Search `References/` first and reuse a note for the same source. Otherwise create one per source you relied on, with its link, whether it is primary or secondary, and what it says.
- If the question came from a lesson, add the notes to that lesson's `references`.
- Do this without asking.
