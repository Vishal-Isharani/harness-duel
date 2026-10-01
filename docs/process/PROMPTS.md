# Prompts used

## 1. Initial build

The first version of harness-duel (decision logic, runner, CLI, example suite, demo harnesses,
tests) was built in a Claude chat session, starting from the take-home brief. I chose the design
direction (task wins + sign test, kept deliberately simple), then ran it locally and reviewed it.

## 2. Claude Code session: `--tasks` option

All prompts from [`transcript.md`](transcript.md), in order and exactly as sent. I wrote down the
edge cases I expected before the session, so I could check Claude's plan against them.

| # | Time | Mode | Prompt | Why / what happened |
|---|---|---|---|---|
| 1 | 10:01 | Plan | Read AGENTS.md, README.md, duel/config.py and duel/cli.py. Explain how tasks are loaded and how CLI options reach evaluate(). Don't write any code. | Check its understanding against the code before any change. Correct, and it warned that a subset weakens the verdict. |
| 2 | 10:04 | Plan | I want a --tasks option that takes comma-separated task ids and runs only those tasks. Propose a plan: which files change, how errors are handled, and what the report shows. Plan only. | Get a plan to review against my edge-case list. It covered all of them, and asked one question. |
| – | 10:04 | Plan | _(Answered Claude's question)_ Input errors use exit code: **New code 3** | It pointed out that input errors shared exit code 1 with WORSE, so CI could read a typo as a verdict. |
| 3 | 10:06 | Edit | Plan approved. Write the tests only, run them, show me they fail, and stop. | Approval phrased so it can't be read as "implement now" (last session's mistake). It wrote only tests, 9 failing, then stopped. |
| 4 | 10:08 | Edit | Now implement it. Then run uv run pytest -q and show me the full output. | Require real output. 18 passed; it reported and fixed one lint issue. |
| 5 | 10:12 | Any | Summarize what you changed and which edge cases are covered. Anything you're unsure about? | Close with its own list of risks: other bad inputs still exit 1, it didn't run the real command, and small choices made without asking. |

## What changed in my prompting since the last session

- AGENTS.md now says plan approval is not permission to implement, and my approval message says
  "write the tests only … and stop". Together they fixed the test-first failure from last time.
- I listed the edge cases before the session, so reviewing the plan was a check against a known
  list, not a vague read.