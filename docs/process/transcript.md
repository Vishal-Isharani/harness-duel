# Agent session: `--tasks` option for harness-duel

- Agent: Claude Code v2.1.285 (Opus 5.5)
- Task: add a `--tasks` option that runs only the listed task ids
- What I checked and where the agent was wrong: [HAND_CHECKS.md](HAND_CHECKS.md)
- Prompts with notes: [PROMPTS.md](PROMPTS.md)

Unedited export from Claude Code (`/export`), wrapped so the terminal layout is preserved.

~~~text
 ▐▛███▛█   Claude Code v2.1.285
▝▜██████▀  Opus 5.5 · Claude Pro
 ▝▝   ▝▝   ~/Projects/ninja tech/harness-duel

  Get to finished work sooner with Opus 5.5. Switch anytime with /model.
  1 more notice hidden

⏺ cc-plugin-agents-md: no CLAUDE.md found; AGENTS.md loaded: 
  /Users/vishalisharani/Projects/ninja tech/harness-duel/AGENTS.md

❯ Read AGENTS.md, README.md, duel/config.py and duel/cli.py. Explain how tasks  
  are loaded and how CLI options reach evaluate(). Don't write any code.        

  Read 3 files (ctrl+o to expand)

⏺ I read all four files (AGENTS.md was already loaded) and made no changes.

  How tasks are loaded (duel/config.py)

  load_suite(path) at duel/config.py:49:

  1. It resolves the suite folder (examples unless you pass --suite).
  2. It finds tasks with sorted(root.glob("tasks/*/task.toml")). Each subfolder
     of tasks/ that has a task.toml is one task, and tasks are ordered by folder
     name.
  3. Each task.toml becomes a Task:
     - id is the folder name, not a field in the toml.
     - prompt is data["prompt"].strip(). It's required, so a missing prompt
       raises KeyError.
     - hidden is <task folder>/hidden. It's only a path here; nothing checks
       that it exists. Per AGENTS.md, the runner copies it in only after the
       agent finishes.
     - timeout is data.get("timeout", 600).
  4. If no tasks are found, it raises SystemExit("No tasks found in …/tasks").
  5. It returns Suite(root, root / "repo", tasks).

  Harnesses load the same way through load_harness (config.py:35), which reads
  harness.toml and adds files/ if that folder exists.

  How CLI options reach evaluate() (duel/cli.py)

  main() at cli.py:69 sets up argparse with one subcommand, evaluate, which
  takes these options:

  ┌─────────────┬────────────┬──────────────────────┐
  │    Flag     │  Default   │ evaluate() parameter │
  ├─────────────┼────────────┼──────────────────────┤
  │ --baseline  │ required   │ base_dir             │
  ├─────────────┼────────────┼──────────────────────┤
  │ --candidate │ required   │ cand_dir             │
  ├─────────────┼────────────┼──────────────────────┤
  │ --suite     │ "examples" │ suite_dir            │
  ├─────────────┼────────────┼──────────────────────┤
  │ --runs      │ 3 (int)    │ runs                 │
  ├─────────────┼────────────┼──────────────────────┤
  │ --out       │ "runs"     │ out_root             │
  └─────────────┴────────────┴──────────────────────┘

  They're passed by position at cli.py:79: evaluate(args.suite, args.baseline, 
  args.candidate, args.runs, args.out). main then turns the verdict into an exit
  code with EXIT_CODES (0 = BETTER, 1 = WORSE, 2 = NO CLEAR DIFFERENCE).

  Inside evaluate() (cli.py:41):
  - suite_dir goes to load_suite, and the two harness folders go to
    load_harness.
  - out_root gets a timestamped subfolder.
  - count_lint(suite.repo) runs once to get the starting lint count, so only
    lint the agent adds is counted.
  - It loops over every task in suite.tasks. For each run index 0…runs-1, it
    runs the baseline and then the candidate through run_once. The two sides
    alternate within each run index.
  - Each task's results go through summarize, then duel picks the winner.
    verdict(rows) applies the sign test, and report.md and report.json are
    written.

  Things to keep in mind

  - There's no task filtering yet. Every task under tasks/ runs, and the CLI has
    no option to pick a subset. Since this branch is feature/tasks-filter, the
    obvious places to add one are a new argparse option, a new evaluate()
    parameter, and filtering suite.tasks (either in load_suite or right after
    it's called).
  - Filtering changes the verdict. The sign test counts decisive tasks, so
    running fewer tasks means the candidate needs more consistent wins to get a
    verdict (with 4 or fewer, it can never get one). Any filter should be clear
    that a subset gives a weaker verdict.
  - Arguments are positional. evaluate() is called by position, and the
    end-to-end tests probably call it directly. Adding a parameter is safest as
    a keyword argument with a default.

✻ Cooked for 17s · done 10:01 AM

❯ I want a --tasks option that takes comma-separated task ids and runs only     
  those tasks. Propose a plan: which files change, how errors are handled, and  
  what the report shows. Plan only.                                             

  Ran 1 shell command (ctrl+o to expand)

⏺ Updated plan
  ⎿  /plan to preview

⏺ User answered Claude's questions:
  ⎿  · Input errors (an unknown or empty --tasks, or 'No tasks found') currently
     exit with code 1, the same code as a WORSE verdict, so a CI gate could 
     mistake a typo for a result. Which exit code should input errors use? → New
     code 3 (Recommended)

⏺ Updated plan
  ⎿  /plan to preview

⏺ Updated plan
  ⎿  /plan to preview

⏺ Updated plan
  ⎿  /plan to preview

⏺ Updated plan
  ⎿  /plan to preview
  ⎿  User rejected Claude's plan:
     ╭─────────────────────────────────────────────────────────────────────────╮
     │ Plan: --tasks option for duel evaluate                                  │
     │                                                                         │
     │ Context                                                                 │
     │                                                                         │
     │ Today evaluate runs every task under <suite>/tasks/. We want --tasks    │
     │ a,b to run only those                                                   │
     │ task ids (useful for cheap reruns / debugging one task). The sign test  │
     │ gets weaker with fewer                                                  │
     │ tasks, so the report must say clearly that a subset was run.            │
     │                                                                         │
     │ Files that change                                                       │
     │                                                                         │
     │ 1. duel/config.py — load_suite(path, only: list[str] | None = None).    │
     │    - After globbing, if only is given, keep tasks whose id is in only.  │
     │    - Order stays the suite's sorted order (not the order typed), so     │
     │      runs are reproducible.                                             │
     │    - Filtering lives here because this is where task ids are known; the │
     │      existing                                                           │
     │      "No tasks found" check stays as is.                                │
     │ 2. duel/cli.py                                                          │
     │    - main: ev.add_argument("--tasks", help="comma-separated task ids to │
     │      run (default: all)").                                              │
     │      Parse: split on ,, strip whitespace, drop empty pieces, dedupe     │
     │      keeping first occurrence.                                          │
     │    - evaluate(..., out_root, tasks: list[str] | None = None) — new      │
     │      keyword arg with default                                           │
     │      so the existing positional calls in tests/test_end_to_end.py keep  │
     │      working. Passes it to                                              │
     │      load_suite(suite_dir, only=tasks).                                 │
     │    - report(...) gets the selection info and prints the subset line     │
     │      (see below).                                                       │
     │    - report.json gets "selected_tasks": [...] (or null when all tasks   │
     │      ran).                                                              │
     │ 3. README.md — one line under "Using it on your own team → Run"         │
     │    documenting --tasks,                                                 │
     │    with the warning that a subset weakens the verdict (≤4 decisive      │
     │    tasks can never reach one);                                          │
     │    exit code 3 = input error.                                           │
     │ 4. Tests — new tests/test_config.py + additions to                      │
     │    tests/test_end_to_end.py.                                            │
     │                                                                         │
     │ decide.py is untouched: decision order and sign test don't change.      │
     │                                                                         │
     │ Error handling                                                          │
     │                                                                         │
     │ All validation happens before any agent run or output folder is         │
     │ created.                                                                │
     │                                                                         │
     │ ┌────────────────────┬───────────────────────────────────────────────── │
     │ ───┐                                                                    │
     │ │       Input        │                     Behaviour                    │
     │   │                                                                     │
     │ ├────────────────────┼───────────────────────────────────────────────── │
     │ ───┤                                                                    │
     │ │ --tasks omitted    │ all tasks (current behaviour)                    │
     │   │                                                                     │
     │ ├────────────────────┼───────────────────────────────────────────────── │
     │ ───┤                                                                    │
     │ │ --tasks            │ runs those 2                                     │
     │   │                                                                     │
     │ │ to-csv,transfer    │                                                  │
     │   │                                                                     │
     │ ├────────────────────┼───────────────────────────────────────────────── │
     │ ───┤                                                                    │
     │ │ --tasks " to-csv , │ whitespace stripped, empties dropped, duplicate  │
     │   │                                                                     │
     │ │  to-csv ,"         │ ignored → 1 task                                 │
     │   │                                                                     │
     │ ├────────────────────┼───────────────────────────────────────────────── │
     │ ───┤                                                                    │
     │ │ --tasks "" or      │ error: --tasks given but no task ids in it       │
     │   │                                                                     │
     │ │ --tasks ","        │                                                  │
     │   │                                                                     │
     │ ├────────────────────┼───────────────────────────────────────────────── │
     │ ───┤                                                                    │
     │ │                    │ error listing all unknown ids and the available  │
     │   │                                                                     │
     │ │ --tasks            │ ones: Unknown task id(s): nope. Available:       │
     │   │                                                                     │
     │ │ to-csv,nope        │ fix-zero-add, low-stock, ... — nothing runs (no  │
     │   │                                                                     │
     │ │                    │ silent partial run)                              │
     │   │                                                                     │
     │ └────────────────────┴───────────────────────────────────────────────── │
     │ ───┘                                                                    │
     │                                                                         │
     │ Exit code 3 for input errors (decided). Today SystemExit("msg") exits 1 │
     │ (= WORSE), so a CI gate                                                 │
     │ could read a typo as a verdict. Instead:                                │
     │ - config.py defines class InputError(Exception). load_suite raises it   │
     │   for unknown ids and                                                   │
     │   for the existing "No tasks found" case (this changes the old exit     │
     │   code from 1 to 3).                                                    │
     │ - main raises it for an empty --tasks, catches InputError, prints       │
     │   error: <msg> to                                                       │
     │   stderr and returns 3. EXIT_CODES stays the verdict map; add           │
     │   EXIT_INPUT_ERROR = 3.                                                 │
     │ - evaluate() called directly (as the tests do) just lets InputError     │
     │   propagate.                                                            │
     │ - README: add 3 input error next to the 0/1/2 exit codes.               │
     │                                                                         │
     │ What the report shows                                                   │
     │                                                                         │
     │ - Full run: unchanged.                                                  │
     │ - Subset run, an extra line under the summary in report.md:             │
     │ ▎ Tasks: 2 of 6 selected with --tasks (to-csv, transfer). A subset      │
     │ gives a weaker verdict;                                                 │
     │ ▎ run the full suite before rolling a change out.                       │
     │ - The task table only lists the tasks that ran (as now, since rows come │
     │   from the run).                                                        │
     │ - report.json: "selected_tasks": ["to-csv", "transfer"], null for a     │
     │   full run.                                                             │
     │ - Console final line unchanged; the subset note is in the report.       │
     │                                                                         │
     │ Order of work (per AGENTS.md)                                           │
     │                                                                         │
     │ 1. Wait for plan approval (approval is not permission to implement).    │
     │ 2. Write tests first, run uv run pytest -q, show they fail:             │
     │    - load_suite(EX, only=["transfer","to-csv"]) → ids                   │
     │      ["to-csv","transfer"] (sorted order).                              │
     │    - unknown id → InputError whose message names the unknown id and     │
     │      lists the available ones.                                          │
     │    - suite with no tasks → InputError.                                  │
     │    - main([... "--tasks", " ,"]) and main([... "--tasks", "nope"]) →    │
     │      return 3, no run folder created.                                   │
     │    - end-to-end demo with tasks=["to-csv"] → report.md contains "1 of 6 │
     │      selected",                                                         │
     │      report.json selected_tasks == ["to-csv"], only one row.            │
     │    - existing end-to-end tests unchanged (full run, no subset line).    │
     │ 3. Implement, run uv run pytest -q, paste full output.                  │
     │                                                                         │
     │ Verification                                                            │
     │                                                                         │
     │ - uv run pytest -q (full output pasted).                                │
     │ - Manual: uv run duel evaluate --baseline                               │
     │   examples/harnesses/demo-baseline --candidate                          │
     │   examples/harnesses/demo-candidate --tasks to-csv,transfer             │
     │   → 2 tasks run, report shows the subset line; --tasks nope → error, no │
     │   run folder, echo $? prints 3.                                         │
     ╰─────────────────────────────────────────────────────────────────────────╯

⏺ Understood, I'll wait. I won't change anything until you've reviewed the plan
  and told me to go ahead. The plan is in
  ~/.claude/plans/read-agents-md-readme-md-duel-config-py-vivid-storm.md. Here's
  the short version:

  Files that change
  - duel/config.py:
    - load_suite(path, only=None) keeps only the task ids you pass, in the
      suite's sorted order.
    - It adds a new InputError exception, which it raises for unknown task ids
      and for "No tasks found".
  - duel/cli.py:
    - It adds the --tasks flag. The value is split on commas, spaces are
      trimmed, and empty entries and duplicates are dropped.
    - evaluate() gets a new tasks=None keyword argument, so the existing test
      calls keep working.
    - main turns an InputError into exit code 3.
  - README.md: documents --tasks, warns that running a subset weakens the
    verdict, and adds exit code 3.
  - Tests: a new tests/test_config.py, plus additions to
    tests/test_end_to_end.py.
  - decide.py doesn't change.

  Error handling
  - All checks run before any agent runs or any output folder is created.
  - An empty --tasks (like "" or ",") is an error.
  - If any id is unknown, the error lists every unknown id and the available
    ones, and nothing runs.
  - These errors exit with code 3, as you chose. That includes the existing "No
    tasks found" error, which currently exits 1.

  What the report shows
  - report.md gets an extra line on subset runs, for example: "Tasks: 2 of 6
    selected with --tasks (…). A subset gives a weaker verdict; run the full
    suite before rolling a change out."
  - report.json gets "selected_tasks", which is null when every task ran.
  - The task table lists only the tasks that ran.
  - A full run produces the same report as today.

  Order of work (per AGENTS.md, once you approve): I'll write the tests first
  and show you they fail, then implement and paste the full uv run pytest -q
  output.

✻ Brewed for 54s · done 10:04 AM

❯ Plan approved. Write the tests only, run them, show me they fail, and stop.   

  Read 1 file (ctrl+o to expand)

⏺ Write(tests/test_config.py)
  ⎿  Wrote 27 lines to tests/test_config.py
      1 from pathlib import Path
      2 
      3 import pytest
      4 
      5 from duel import config
      6 from duel.config import load_suite
      7 
      8 EX = Path(__file__).resolve().parent.parent / "examples"
      9 
     … +17 lines (ctrl+o to expand)

⏺ Update(tests/test_end_to_end.py)
  ⎿  Added 6 lines, removed 1 line
       1 +import json                                                    
       2  from pathlib import Path
       3  
       3 -from duel.cli import evaluate                                  
       4 +import pytest                                                  
       5  
       6 +from duel.cli import evaluate, main                            
       7 +                                                               
       8  EX = Path(__file__).resolve().parent.parent / "examples"
       9 +DEMO = ["--baseline", str(EX / "harnesses/demo-baseline"),     
      10 +        "--candidate", str(EX / "harnesses/demo-candidate"), "-
         +-suite", str(EX)]                                              
      11  
      12  
      13  def test_demo_candidate_is_detected_as_better(tmp_path):

  Ran 1 shell command (ctrl+o to expand)

⏺ I wrote the tests and ran them. The 9 new tests fail and the 9 existing tests
  still pass. I haven't touched duel/ yet.

  Tests added
  - tests/test_config.py (new):
    - Passing only=[...] keeps just those tasks, in the suite's sorted order.
    - An unknown id raises InputError, and the message names the bad id and
      lists the available ones.
    - A suite with no tasks raises InputError.
  - tests/test_end_to_end.py:
    - A subset run of only to-csv produces 1 report row, selected_tasks == 
      ["to-csv"] in the JSON, and "1 of 6 selected" in report.md.
    - A full run has selected_tasks set to null and no subset line.
    - --tasks " to-csv , to-csv ," runs just to-csv.
    - --tasks values of "", " , " and "to-csv,nope" make main return 3 and
      create no output folder.

  uv run pytest -q output (in the middle, pytest itself cut about 1,900
  characters of the argparse traceback):
  FFF.........FFFFFF                                                       
  [100%]
  ...
  E       TypeError: load_suite() got an unexpected keyword argument 'only'
  E       AttributeError: module 'duel.config' has no attribute 'InputError'
  E       AttributeError: module 'duel.config' has no attribute 'InputError'
  E       TypeError: evaluate() got an unexpected keyword argument 'tasks'
  E       KeyError: 'selected_tasks'
  duel: error: unrecognized arguments: --tasks  to-csv , to-csv ,      
  (SystemExit: 2)
  duel: error: unrecognized arguments: --tasks                         
  (SystemExit: 2)
  duel: error: unrecognized arguments: --tasks  ,                      
  (SystemExit: 2)
  duel: error: unrecognized arguments: --tasks to-csv,nope             
  (SystemExit: 2)
  =========================== short test summary info 
  ============================
  FAILED tests/test_config.py::test_only_keeps_selected_tasks_in_suite_order - 
  ...
  FAILED tests/test_config.py::test_unknown_task_id_names_it_and_lists_available
  FAILED tests/test_config.py::test_suite_without_tasks_is_an_input_error - 
  Att...
  FAILED 
  tests/test_end_to_end.py::test_tasks_subset_runs_only_those_and_report_says_so
  FAILED tests/test_end_to_end.py::test_full_run_has_no_subset_line - 
  KeyError:...
  FAILED tests/test_end_to_end.py::test_tasks_flag_trims_spaces_and_ignores_dupl
  icates_and_empties
  FAILED 
  tests/test_end_to_end.py::test_bad_tasks_flag_exits_3_before_anything_runs[]
  FAILED 
  tests/test_end_to_end.py::test_bad_tasks_flag_exits_3_before_anything_runs[ , 
  ]
  FAILED tests/test_end_to_end.py::test_bad_tasks_flag_exits_3_before_anything_r
  uns[to-csv,nope]
  9 failed, 9 passed in 12.61s

  Each test fails because the feature doesn't exist yet, not because of a
  mistake in the test:
  - only isn't a parameter of load_suite yet.
  - InputError doesn't exist yet.
  - evaluate() doesn't accept tasks yet.
  - report.json has no selected_tasks key yet.
  - argparse rejects --tasks because the flag isn't defined yet.

  I've stopped here. Tell me when you want me to implement.

✻ Crunched for 39s · done 10:06 AM

❯ Now implement it. Then run uv run pytest -q and show me the full output.      

⏺ Update(duel/config.py)
  ⎿  Added 9 lines, removed 2 lines
      46      )
      47  
      48  
      49 -def load_suite(path: str | Path) -> Suite:                     
      49 +def load_suite(path: str | Path, only: list[str] | None = None)
         + -> Suite:                                                     
      50 +    """Load the suite's tasks; `only` keeps just those task ids
         + (in suite order)."""                                          
      51      root = Path(path).resolve()
      52      tasks = []
      53      for file in sorted(root.glob("tasks/*/task.toml")):
     ...
      55          tasks.append(Task(file.parent.name, data["prompt"].stri
          p(), file.parent / "hidden",
      56                            data.get("timeout", 600)))
      57      if not tasks:
      57 -        raise SystemExit(f"No tasks found in {root / 'tasks'}")
      58 +        raise InputError(f"No tasks found in {root / 'tasks'}")
      59 +    if only is not None:                                       
      60 +        known = [t.id for t in tasks]                          
      61 +        unknown = [i for i in only if i not in known]          
      62 +        if unknown:                                            
      63 +            raise InputError(f"Unknown task id(s): {', '.join(u
         +nknown)}. Available: {', '.join(known)}")                      
      64 +        tasks = [t for t in tasks if t.id in only]             
      65      return Suite(root, root / "repo", tasks)

⏺ Update(duel/config.py)
  ⎿  Added 4 lines
       6  from pathlib import Path
       7  
       8  
       9 +class InputError(Exception):                                   
      10 +    """Bad input (suite or task selection); `duel` exits with c
         +ode 3, never a verdict code."""                                
      11 +                                                               
      12 +                                                               
      13  @dataclass
      14  class Harness:
      15      name: str
  Ran 2 shell commands (ctrl+o to expand)

⏺ Update(duel/config.py)
  ⎿  Added 1 line
      34      root: Path
      35      repo: Path
      36      tasks: list[Task]
      37 +    total_tasks: int  # tasks in the suite before any `only` se
         +lection                                                        
      38  
      39  
      40  def load_harness(path: str | Path) -> Harness:

⏺ Update(duel/config.py)
  ⎿  Added 1 line
      61                            data.get("timeout", 600)))
      62      if not tasks:
      63          raise InputError(f"No tasks found in {root / 'tasks'}")
      64 +    total = len(tasks)                                         
      65      if only is not None:
      66          known = [t.id for t in tasks]
      67          unknown = [i for i in only if i not in known]

⏺ Update(duel/config.py)
  ⎿  Added 1 line, removed 1 line
      68          if unknown:
      69              raise InputError(f"Unknown task id(s): {', '.join(u
          nknown)}. Available: {', '.join(known)}")
      70          tasks = [t for t in tasks if t.id in only]
      71 -    return Suite(root, root / "repo", tasks)                   
      71 +    return Suite(root, root / "repo", tasks, total)            

⏺ Update(duel/cli.py)
  ⎿  Added 2 lines, removed 1 line
       7  from datetime import datetime
       8  from pathlib import Path
       9  
      10 -from .config import load_harness, load_suite                   
      10 +from .config import InputError, load_harness, load_suite       
      11  from .decide import duel, summarize, verdict
      12  from .runner import count_lint, run_once
      13  
      14  EXIT_CODES = {"BETTER": 0, "WORSE": 1, "NO CLEAR DIFFERENCE": 2
          }
      15 +EXIT_INPUT_ERROR = 3  # bad --suite/--tasks; kept apart so CI n
         +ever reads a typo as a verdict                                 
      16  
      17  
      18  def money(x: float | None) -> str:

⏺ Update(duel/cli.py)
  ⎿  Added 7 lines, removed 1 line
      19      return "n/a" if x is None else f"${x:.3f}"
      20  
      21  
      22 -def report(base: str, cand: str, rows: list[dict], result: dict
         -, runs: int) -> str:                                           
      22 +def report(base: str, cand: str, rows: list[dict], result: dict
         +, runs: int,                                                   
      23 +           selected: list[str] | None = None, total: int = 0) -
         +> str:                                                         
      24      lines = [
      25          f"# Harness duel: `{base}` vs `{cand}`", "",
      26          f"## Verdict: {result['verdict']}", "",
      27          f"{result['summary'].capitalize()}. {len(rows)} tasks, 
          {runs} run(s) per task per harness.",
      28          f"Chance of this many candidate wins if the change did 
          nothing: {result['p_better']:.1%}.", "",
      29 +    ]                                                          
      30 +    if selected is not None:                                   
      31 +        lines += [f"Tasks: {len(selected)} of {total} selected 
         +with `--tasks` ({', '.join(selected)}). "                      
      32 +                  "A subset gives a weaker verdict; run the ful
         +l suite before rolling a change out.", ""]                     
      33 +    lines += [                                                 
      34          "| Task | Winner | Why | Tests | New lint | Cost | Erro
          rs |",
      35          "|---|---|---|---|---|---|---|",
      36      ]

⏺ Update(duel/cli.py)
  ⎿  Added 4 lines, removed 2 lines
      45      return "\n".join(lines)
      46  
      47  
      48 -def evaluate(suite_dir: str, base_dir: str, cand_dir: str, runs
         -: int, out_root: str) -> dict:                                 
      49 -    suite = load_suite(suite_dir)                              
      48 +def evaluate(suite_dir: str, base_dir: str, cand_dir: str, runs
         +: int, out_root: str,                                          
      49 +             tasks: list[str] | None = None) -> dict:          
      50 +    suite = load_suite(suite_dir, only=tasks)                  
      51 +    selected = None if tasks is None else [t.id for t in suite.
         +tasks]                                                         
      52      base, cand = load_harness(base_dir), load_harness(cand_dir)
      53      out = Path(out_root) / datetime.now().astimezone().strftime
          ("%Y%m%d-%H%M%S")
      54      out.mkdir(parents=True)

⏺ Update(duel/cli.py)
  ⎿  Added 4 lines, removed 2 lines
      69          rows.append({"task": task.id, "base": b, "cand": c, "wi
          nner": winner, "reason": reason})
      70  
      71      result = verdict(rows)
      72 -    (out / "report.md").write_text(report(base.name, cand.name,
         - rows, result, runs))                                          
      73 -    (out / "report.json").write_text(json.dumps({"verdict": res
         -ult, "tasks": rows}, indent=2))                                
      72 +    (out / "report.md").write_text(report(base.name, cand.name,
         + rows, result, runs,                                           
      73 +                                          selected, suite.total
         +_tasks))                                                       
      74 +    (out / "report.json").write_text(json.dumps(               
      75 +        {"verdict": result, "selected_tasks": selected, "tasks"
         +: rows}, indent=2))                                            
      76      print(f"\nVERDICT: {result['verdict']} ({result['summary']}
          )\nReport: {out / 'report.md'}")
      77      return result
      78  

⏺ Update(duel/cli.py)
  ⎿  Added 11 lines, removed 1 line
       86      ev.add_argument("--suite", default="examples", help="folde
           r with repo/ and tasks/ (default: examples)")
       87      ev.add_argument("--runs", type=int, default=3, help="runs 
           per task per harness (default: 3)")
       88      ev.add_argument("--out", default="runs", help="output fold
           er (default: runs)")
       89 +    ev.add_argument("--tasks", help="comma-separated task ids 
          +to run (default: all)")                                       
       90      args = parser.parse_args(argv)
       90 -    result = evaluate(args.suite, args.baseline, args.candidat
          -e, args.runs, args.out)                                       
       91 +    try:                                                      
       92 +        tasks = None                                          
       93 +        if args.tasks is not None:                            
       94 +            tasks = list(dict.fromkeys(t.strip() for t in args
          +.tasks.split(",") if t.strip()))                              
       95 +            if not tasks:                                     
       96 +                raise InputError("--tasks given but no task id
          +s in it")                                                     
       97 +        result = evaluate(args.suite, args.baseline, args.cand
          +idate, args.runs, args.out, tasks)                            
       98 +    except InputError as e:                                   
       99 +        print(f"error: {e}", file=sys.stderr)                 
      100 +        return EXIT_INPUT_ERROR                               
      101      return EXIT_CODES[result["verdict"]]
      102  
      103  

⏺ I've finished the code changes in config.py and cli.py. Next I'll update the
  README, then run the tests.

⏺ Update(README.md)
  ⎿  Added 2 lines, removed 1 line
      53  > ⚠️ The example harnesses pass `--dangerously-skip-permissions
          `, because headless runs cannot
      54  > answer permission prompts. Run in a container or VM, or repla
          ce it with `--allowedTools`.
      55  
      56 -Exit codes, so it can gate a harness change in CI: `0` BETTER, 
         -`1` WORSE, `2` NO CLEAR DIFFERENCE.                            
      56 +Exit codes, so it can gate a harness change in CI: `0` BETTER, 
         +`1` WORSE, `2` NO CLEAR DIFFERENCE,                            
      57 +`3` input error (no tasks found, or a bad `--tasks`).          
      58  
      59  ## How it decides
      60  

⏺ Update(README.md)
  ⎿  Added 4 lines
      121     copied into the repo before the agent runs. Change one thin
           g per candidate.
      122  4. **Run:** `uv run duel evaluate --suite <your folder> --base
           line … --candidate …`
      123  
      124 +   Add `--tasks to-csv,transfer` to run only those task ids, f
          +or a cheap rerun or to debug one task.                        
      125 +   A subset gives a weaker verdict (with 4 or fewer decisive t
          +asks it can never reach one), and                             
      126 +   the report says so. Run the full suite before rolling a cha
          +nge out.                                                      
      127 +                                                              
      128  ## Development
      129  
      130  ```bash

  Ran 2 shell commands (ctrl+o to expand)

⏺ Update(duel/cli.py)
  ⎿  Added 2 lines, removed 2 lines
      28          f"Chance of this many candidate wins if the change did 
          nothing: {result['p_better']:.1%}.", "",
      29      ]
      30      if selected is not None:
      31 -        lines += [f"Tasks: {len(selected)} of {total} selected 
         -with `--tasks` ({', '.join(selected)}). "                      
      32 -                  "A subset gives a weaker verdict; run the ful
         -l suite before rolling a change out.", ""]                     
      31 +        lines += [(f"Tasks: {len(selected)} of {total} selected
         + with `--tasks` ({', '.join(selected)}). "                     
      32 +                   "A subset gives a weaker verdict; run the fu
         +ll suite before rolling a change out."), ""]                   
      33      lines += [
      34          "| Task | Winner | Why | Tests | New lint | Cost | Erro
          rs |",
      35          "|---|---|---|---|---|---|---|",

  Ran 1 shell command (ctrl+o to expand)

⏺ --tasks is implemented and all 18 tests pass: the 9 new ones and the 9 that
  were already there.

  Full output of uv run pytest -q:
  ..................                                                       
  [100%]
  18 passed in 13.49s

  What changed
  - duel/config.py:
    - New InputError exception.
    - load_suite(path, only=None) now raises InputError for "No tasks found" (it
      used to call SystemExit). It also raises it for unknown ids, naming each
      unknown id and listing the available ones. Otherwise it keeps only the
      selected tasks, in the suite's sorted order.
    - Suite has a new total_tasks field, so the report can say "N of M".
  - duel/cli.py:
    - New --tasks flag. Spaces are trimmed, empty entries and duplicates are
      dropped, and a value with no ids left is an InputError.
    - evaluate() takes a new keyword argument, tasks=None. The selection is
      checked before the output folder is created, so a bad --tasks leaves
      nothing behind.
    - main catches InputError, prints error: … to stderr and returns 3
      (EXIT_INPUT_ERROR).
    - On a subset run, report.md gets the "Tasks: N of M selected with --tasks
      (…)" line with the warning that the verdict is weaker. report.json has a
      new selected_tasks key, which is null when every task ran.
  - README.md: documents --tasks and the subset warning, and adds exit code 3.

  Things to know
  - Exit code change: a suite with no tasks now exits 3 instead of 1. This is
    what we agreed in the plan, but any CI script that relied on the old code
    will see the difference.
  - Lint fix: ruff flagged one issue in my first version (an unparenthesized
    implicit string concatenation in the report line, rule ISC004). I fixed it,
    and ruff check duel tests now passes.

  Nothing is committed. reports/ was already untracked before I started and I
  haven't touched it.

✻ Worked for 1m 7s · done 10:08 AM

※ recap: You asked for a --tasks option that runs only the listed task ids, and it's built, with all 18 tests and ruff passing. Next, you review the uncommitted changes and tell me whether to commit them. (disable recaps in /config)

❯ Summarize what you changed and which edge cases are covered. Anything you're  
  unsure about?                                                                 

⏺ What changed

  duel/config.py
  - New InputError exception for bad input.
  - load_suite(path, only=None):
    - Keeps only the requested task ids, in the suite's sorted order (not the
      order you typed them).
    - Raises InputError for unknown ids, naming each one and listing the
      available ids.
    - "No tasks found" now raises InputError instead of SystemExit, so its exit
      code goes from 1 to 3.
  - Suite has a new total_tasks field so the report can say "N of M".

  duel/cli.py
  - New --tasks option, parsed in main.
  - evaluate() takes a new keyword argument, tasks=None.
  - main turns any InputError into error: … on stderr and exit code 3.
  - On a subset run, report.md gets one extra line with the weaker-verdict
    warning.
  - report.json gets a selected_tasks key, which is null for a full run.

  README.md: documents --tasks with the subset warning, and adds exit code 3.

  Tests: a new tests/test_config.py and 6 new tests in tests/test_end_to_end.py.

  Edge cases covered by tests

  ┌──────────────────────────────────┬──────────────────────────────────────┐
  │               Case               │               Expected               │
  ├──────────────────────────────────┼──────────────────────────────────────┤
  │ only=["transfer","to-csv"]       │ runs to-csv, then transfer (suite    │
  │                                  │ order)                               │
  ├──────────────────────────────────┼──────────────────────────────────────┤
  │ Unknown id mixed with a valid    │ InputError naming the bad id and     │
  │ one                              │ listing the available ones           │
  ├──────────────────────────────────┼──────────────────────────────────────┤
  │ Suite with an empty tasks/       │ InputError                           │
  │ folder                           │                                      │
  ├──────────────────────────────────┼──────────────────────────────────────┤
  │ --tasks " to-csv , to-csv ,"     │ spaces trimmed, duplicate and empty  │
  │                                  │ entry dropped, 1 task runs           │
  ├──────────────────────────────────┼──────────────────────────────────────┤
  │ --tasks "", " , ", "to-csv,nope" │ exit code 3, no output folder        │
  │                                  │ created                              │
  ├──────────────────────────────────┼──────────────────────────────────────┤
  │ Subset run                       │ 1 row, selected_tasks == ["to-csv"], │
  │                                  │  "1 of 6 selected" in report.md      │
  ├──────────────────────────────────┼──────────────────────────────────────┤
  │ Full run                         │ selected_tasks is null, no subset    │
  │                                  │ line                                 │
  ├──────────────────────────────────┼──────────────────────────────────────┤
  │ Existing calls to evaluate()     │ still pass unchanged                 │
  │ without tasks                    │                                      │
  └──────────────────────────────────┴──────────────────────────────────────┘

  What I'm unsure about

  1. Some bad input still exits with code 1, the same code as WORSE. A task.toml
     with no prompt (a KeyError), a missing harness.toml (a FileNotFoundError),
     or an invalid TOML file all end in an uncaught exception. Python exits
     with code 1 in that case, so CI could read it as WORSE. My change fixed
     this for empty suites and bad --tasks, not for every kind of bad input.
     Fixing it would mean turning those errors into InputError too. That's a
     small change, but it's outside the plan you approved, so I didn't do it.
  2. I didn't run the real command. The plan's verification step included
     running uv run duel evaluate … --tasks nope; echo $? by hand. The tests
     call main() directly, so the parsing and exit-code logic is covered, but
     the installed duel command and sys.exit weren't. I can run it now if you
     want.
  3. "No tasks found" through main isn't tested end to end. The test checks that
     load_suite raises InputError, and other tests check that main turns
     InputError into 3. No single test runs the whole path for an empty suite.
  4. Smaller behaviors I chose without asking:
     - Task ids are case-sensitive, so To-CSV is reported as unknown.
     - Ids run and appear in the report in suite order, whatever order you typed
       them in.
     - A value starting with - (e.g. --tasks -foo) gets an argparse error with
       exit code 2, not 3. Task ids don't normally start with -, so I left it.
  5. total_tasks is a required field on Suite. Nothing in the repo builds a
     Suite directly, but any outside code that does would now break. Giving it a
     default value would avoid that, if you care.

  The new end-to-end tests use the random demo harnesses, but they only check
  which tasks ran and what the report says, never the verdict, so they shouldn't
  be flaky.

  Nothing is committed.

✻ Churned for 20s · done 10:12 AM
~~~