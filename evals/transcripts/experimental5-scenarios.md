# Experimental.5 scenario attempt record

Date: 2026-11-07. Host: Claude Code, configured model `claude-opus-5-5`. Version tested: `1.4.0-experimental.5`. Each scenario had a separate disposable folder with skill archives extracted into `.claude/skills/`; the runner did not modify installed user skills or production notes.

## Results

| Scenarios | Result | Evidence |
|---|---|---|
| 1–2 | Blocked/incomplete | Nonzero host exit; no completed verdict; weekly-limit response |
| 3 | Incomplete; not accepted | Synthetic goal-check transcript and self-reported checks were written, but host exit was nonzero and the full setup/exercise contract was not met |
| 4–51 | Blocked/incomplete | Nonzero host exit; no completed verdict; weekly-limit response |

**Accepted passes: 0 of 51.** No conversational acceptance pass rate or complete scenario coverage is claimed. The failures above are blocked test execution/coverage, not 51 demonstrated product defects.

Exact host response:

```text
You've hit your weekly limit · resets 9am (Asia/Jakarta)
```

Representative blocked session: scenario 1, ID `17cb7c17-5ba5-40ce-b15d-f07a40d36608`, host exit 1, no completed verdict. The initial host connectivity probe had succeeded before the usage limit interrupted scenario execution.

## Partial scenario 3 artifact

Session ID: `32edf909-4fe5-4758-8f8c-cf3762893c27`. This was a single-agent scripted roleplay, not a real learner conversation or independent evaluation. Selected synthetic messages:

- Learner: “I want to get better at statistics.”
- Tutor: offered three concrete performances: reading statistical reports, running an analysis, or passing an introductory course.
- Learner: selected reading confidence intervals in work reports.
- Tutor: confirmed the concrete goal in a separate message before giving a task.
- Tutor warm-up: “A poll reports that 52% of voters support a plan, with a margin of error of ±3 percentage points. What range of support values is the poll consistent with?”
- Learner: “49% to 55%.”
- Tutor goal task: evaluate a headline claiming a treatment is proven to help when its reported confidence interval includes zero.
- After an incorrect synthetic answer, the tutor gave one hint to check where zero lies in the interval.

The partial artifact suggests the intended easy-first separation, but does not remove the failed/incomplete host result or establish acceptance. It is retained only as evidence of what executed before the blocker.

## Reproduction and disposition

The scratch runner and raw artifacts are retained locally:

- Runner: `/tmp/opencode/experimental5-release-scenarios.py`
- Built packages, prompts, event logs and per-case results: `/tmp/opencode/experimental5-acceptance-b8njomud/`
- Aggregate: `results.json` within that folder; individual records: `scenario-NN/result.json`

The runner used fresh non-persisted sessions, strict MCP configuration, disabled nonessential telemetry, a per-case budget cap, and only local file/shell tools for synthetic scratch fixtures. It did not install dependencies or run network operations inside test sessions.

The release owner was informed that all 91 automated tests and package checks passed while fresh-host testing was blocked. They explicitly selected **Publish prerelease**, with the validation gap disclosed and stable/latest unchanged. Rerun the full scenario suite when host capacity permits; do not convert blocked rows to passes without new evidence.
