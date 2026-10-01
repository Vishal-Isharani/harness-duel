# Hand checks and agent mistakes

Session: adding a `--tasks` option to `duel evaluate`. Built with Claude Code (Opus 5.5).
Full session: [`transcript.md`](transcript.md). Times are from the session.

## What I checked during the session

| # | Time | What I checked | How | Result |
|---|---|---|---|---|
| 1 | 10:01 | Claude's explanation of how tasks are loaded and how CLI options reach `evaluate()` | Compared with `config.py` and `cli.py` | ✔ Correct (`load_suite()`, `main()` → `evaluate()` by position). Unprompted, it warned that running fewer tasks weakens the sign test |
| 2 | 10:04 | Plan covers the edge cases I listed beforehand: typo in an id, spaces, empty value, report saying which tasks ran, no changes to `decide.py`/`runner.py` | Read the plan against my list | ✔ All covered without prompting. Unknown ids give an error listing the valid ones, and nothing runs |
| 3 | 10:04 | A design question Claude raised | Answered it | ✔ **Real flaw in my tool:** input errors exited with code 1, the same as a WORSE verdict, so a CI gate could read a typo as "the change is worse". I chose a separate exit code 3 |
| 4 | 10:06 | Test-first after "Plan approved" | Read its actions and output | ✔ It wrote only tests, showed 9 failing for the right reasons (missing parameter, missing class, unknown flag), and did not touch `duel/`. Last session it skipped this; the AGENTS.md rule I added after that session worked |
| 5 | 10:08 | Implementation and test output | Read the diff and the pytest output | ✔ 18 passed. Only `config.py`, `cli.py`, `README.md` and tests changed |
| 6 | 10:08 | Lint | Its own report | ⚠ It introduced a ruff issue (ISC004) in the report line, caught it and fixed it |
| 7 | 10:12 | Its own list of open risks | Read the summary | ✔ Honest and useful (see below) |

## Where the agent was wrong or incomplete

1. **Didn't run its own manual verification.** Its plan said it would run `duel evaluate --tasks nope; echo $?` by hand; it only ran the tests. It said so when asked.
2. **Left other bad inputs on exit code 1.** A missing `harness.toml`, a `task.toml` without a prompt, or invalid TOML still crash with exit code 1 (= WORSE). It flagged this itself, but only fixed the cases in the plan.
3. **Made small choices without asking:** task ids are case-sensitive, and tasks run in suite order rather than typed order.
4. **Introduced a lint issue**, then fixed it itself.

## My checks after the session

<!-- Run these now and paste the REAL output. Delete any row you didn't do. -->

| # | Command | Expected | What I saw |
|---|---|---|---|
| 8 | `git diff --stat` | only `duel/config.py`, `duel/cli.py`, `README.md`, tests | _paste_ |
| 9 | `uv run duel evaluate --baseline examples/harnesses/demo-baseline --candidate examples/harnesses/demo-candidate --tasks low-stock,to-csv` | 2 tasks run, `NO CLEAR DIFFERENCE (candidate won 2, baseline won 0, ties 0)`, report has the "2 of 6 selected" line | _paste_ |
| 10 | `uv run duel evaluate --baseline examples/harnesses/demo-baseline --candidate examples/harnesses/demo-candidate --tasks low-stok; echo $?` | error listing valid ids, then `3` | _paste_ |

## Follow-ups (not done)

- Turn every bad-input error (missing `harness.toml`, missing prompt, invalid TOML) into exit code 3.
- An end-to-end test for an empty suite through the command line.