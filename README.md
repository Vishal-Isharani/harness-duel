# harness-duel

**Did that change to the harness make the coding agent better, or not?**

A harness is everything around the model that shapes how a coding agent works: AGENTS.md /
CLAUDE.md, skills, MCP config, the model, the agent itself. `harness-duel` answers the question
with the simplest evidence that holds up: run the **baseline** and the **candidate** harness on
the same tasks, see **who wins each task**, and check whether the result is more than luck.

```
VERDICT: BETTER (candidate won 6, baseline won 0, ties 0)
Chance of this many candidate wins if the change did nothing: 1.6%.
```

## Quick start (offline, no API key, about 30 seconds)

Requires [uv](https://docs.astral.sh/uv/) and Python 3.11+.

```bash
git clone <this repo> && cd harness-duel
uv sync
uv run duel evaluate \
  --baseline examples/harnesses/demo-baseline \
  --candidate examples/harnesses/demo-candidate
```

The demo harnesses stand in for a real agent. They copy a known-good or a known-sloppy solution
into the repo at random: the baseline picks the good one 30% of the time, the candidate 90%.
Everything after that is real: git workspaces, the hidden tests, ruff and the decision. That
makes the demo a check on the tool itself, because we know the right answer is BETTER.

## Real example: Claude Code

Requires [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) installed and logged in.

```bash
uv run duel evaluate \
  --baseline examples/harnesses/baseline \
  --candidate examples/harnesses/candidate \
  --runs 1
```

- **baseline**: a two-line AGENTS.md.
- **candidate**: AGENTS.md with the team's conventions and a "before you finish" checklist, plus
  an `inventory-conventions` skill.
- **tasks** (`examples/tasks`): 6 small requests on an inventory library: a bug fix, new
  methods, a CSV export and a transfer that must not leave partial updates.

That is 12 agent runs (6 tasks × 1 run × 2 harnesses), which keeps the example cheap. The report
is written to `runs/<timestamp>/report.md`. See "How many runs per task?" below for what one run
per task costs you in certainty.

> ⚠️ The example harnesses pass `--dangerously-skip-permissions`, because headless runs cannot
> answer permission prompts. Run in a container or VM, or replace it with `--allowedTools`.

Exit codes, so it can gate a harness change in CI: `0` BETTER, `1` WORSE, `2` NO CLEAR DIFFERENCE.

## How it decides

**1. One run.** For each run, the tool:
- copies the repo into a fresh folder, adds the harness files (AGENTS.md, skills…) and commits;
- runs the agent with the task's request;
- counts the **new lint issues** the agent introduced, using the repo's own ruff config, which is
  where the team's conventions live;
- copies in the **hidden tests** and runs them. They're added only after the agent finishes, so
  the agent can never see or edit them. They're written from the request, so they check
  "does it do what the business asked".

**2. One task.** Each harness gets 3 runs per task, and the averages are compared in a fixed
order. The first clear difference decides the task:

| Order | What | Counts as different when |
|---|---|---|
| 1 | Hidden tests passed | any difference |
| 2 | New lint issues | half an issue or more on average |
| 3 | Cost per run | 10% or more |

Otherwise the task is a **tie**.

**3. The verdict: a sign test.** If the change did nothing, each decisive task would be a coin
flip. The tool asks how likely the observed wins would be under that coin flip, leaving ties out:

- **BETTER**: the candidate's wins would happen by luck less than 5% of the time;
- **WORSE**: the same, for the baseline;
- **NO CLEAR DIFFERENCE**: anything else.

**Safety rule:** a candidate that passes fewer hidden tests on any task is never called BETTER,
however many other tasks it wins.

**What this means in practice:** the sign test needs clear, consistent wins. With 6 decisive
tasks the candidate must win all 6, with 10 at least 9, and with 4 or fewer it can never reach a
verdict. The report says how many wins would have been needed. On a small suite, NO CLEAR
DIFFERENCE is common, and that's the honest answer.

## How many runs per task?

Agents are random, so one run can be unlucky. The tool averages the runs of each harness on a
task before deciding who won it (`--runs`, default 3).

The offline demo shows the effect. The candidate produces the good solution 90% of the time and
the baseline 30%:

| `--runs` | Result |
|---|---|
| 1 | NO CLEAR DIFFERENCE: the candidate lost 2 of 6 tasks by bad luck |
| 3 | BETTER: the candidate won 6 of 6 |

Use `--runs 1` for a cheap first look, and the default 3 before rolling a change out.

## Using it on your own team

1. **Repo:** put a snapshot of your project in `repo/`, with your lint config.
2. **Tasks:** one folder per task in `tasks/`, each with:
   - `task.toml`: the request, written like a ticket;
   - `hidden/`: the tests that decide whether it was done.

   Recently merged PRs make good tasks: the parent commit is the repo, the ticket is the prompt,
   and the PR's tests are the hidden tests.
3. **Harnesses:** a folder each with a `harness.toml` (agent, model, args) and a `files/` folder
   copied into the repo before the agent runs. Change one thing per candidate.
4. **Run:** `uv run duel evaluate --suite <your folder> --baseline … --candidate …`

## Development

```bash
uv run pytest -q
```

The tests cover:
- the per-task decision order and margins;
- the sign test numbers;
- the safety rule;
- a false-alarm check: when every task is a coin flip, BETTER or WORSE must stay rare;
- two end-to-end demo runs: a better candidate is detected, and the same harness on both sides
  gives NO CLEAR DIFFERENCE.

## Known limitations

- **Small suites need consistent wins.** 6 tasks means the candidate must win all of them to be
  called BETTER. More tasks make the tool more sensitive.
- **The size of a win doesn't count, only the direction.** A task won by 1 test counts the same as
  one won by 10. That keeps it simple and robust, but it throws away information.
- **Conventions = ruff rules.** Anything a linter can't express, such as naming or architecture,
  is not measured.
- **No isolation from the user's own `~/.claude` config** during runs.
- **One real agent adapter** (Claude Code), run one at a time.

## Layout

```
duel/          config · runner (one run) · decide (task winner + sign test) · cli (report)
examples/      repo/ · tasks/ (6) · harnesses/ (demo + real) · demo/ (good and sloppy solutions)
tests/         decision tests + end-to-end demo tests
docs/          ONE_PAGER.md · process/ (agent session, prompts, hand checks)
```
