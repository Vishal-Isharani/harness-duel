"""`duel evaluate`: run both harnesses on every task, decide, write the report."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from .config import load_harness, load_suite
from .decide import duel, summarize, verdict
from .runner import count_lint, run_once

EXIT_CODES = {"BETTER": 0, "WORSE": 1, "NO CLEAR DIFFERENCE": 2}


def money(x: float | None) -> str:
    return "n/a" if x is None else f"${x:.3f}"


def report(base: str, cand: str, rows: list[dict], result: dict, runs: int) -> str:
    lines = [
        f"# Harness duel: `{base}` vs `{cand}`", "",
        f"## Verdict: {result['verdict']}", "",
        f"{result['summary'].capitalize()}. {len(rows)} tasks, {runs} run(s) per task per harness.",
        f"Chance of this many candidate wins if the change did nothing: {result['p_better']:.1%}.", "",
        "| Task | Winner | Why | Tests | New lint | Cost | Errors |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        b, c = r["base"], r["cand"]
        lines.append(
            f"| `{r['task']}` | {r['winner']} | {r['reason']} | {b['pass_rate']:.0%} → {c['pass_rate']:.0%} "
            f"| {b['lint']:.1f} → {c['lint']:.1f} | {money(b['cost'])} → {money(c['cost'])} "
            f"| {b['errors']} → {c['errors']} |")
    lines += ["", "Columns show baseline → candidate, averaged over runs.",
              "Evidence for every run (`diff.patch`, `hidden_tests.txt`, `result.json`) is in this folder.", ""]
    return "\n".join(lines)


def evaluate(suite_dir: str, base_dir: str, cand_dir: str, runs: int, out_root: str) -> dict:
    suite = load_suite(suite_dir)
    base, cand = load_harness(base_dir), load_harness(cand_dir)
    out = Path(out_root) / datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    out.mkdir(parents=True)
    lint_before = count_lint(suite.repo)

    rows = []
    for task in suite.tasks:
        results = {"base": [], "cand": []}
        for i in range(runs):
            for side, harness in (("base", base), ("cand", cand)):
                r = run_once(suite, task, harness, "baseline" if side == "base" else "candidate",
                             i, out, lint_before)
                results[side].append(r)
                print(f"{task.id} {harness.name} #{i}: tests {r['tests_passed']}/{r['tests_total']}, "
                      f"new lint {r['new_lint']}" + (f", error: {r['error']}" if r["error"] else ""))
        b, c = summarize(results["base"]), summarize(results["cand"])
        winner, reason = duel(b, c)
        rows.append({"task": task.id, "base": b, "cand": c, "winner": winner, "reason": reason})

    result = verdict(rows)
    (out / "report.md").write_text(report(base.name, cand.name, rows, result, runs))
    (out / "report.json").write_text(json.dumps({"verdict": result, "tasks": rows}, indent=2))
    print(f"\nVERDICT: {result['verdict']} ({result['summary']})\nReport: {out / 'report.md'}")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="duel", description="Did the harness change make the agent better?")
    sub = parser.add_subparsers(dest="command", required=True)
    ev = sub.add_parser("evaluate", help="compare a baseline and a candidate harness")
    ev.add_argument("--baseline", required=True, help="baseline harness folder")
    ev.add_argument("--candidate", required=True, help="candidate harness folder")
    ev.add_argument("--suite", default="examples", help="folder with repo/ and tasks/ (default: examples)")
    ev.add_argument("--runs", type=int, default=3, help="runs per task per harness (default: 3)")
    ev.add_argument("--out", default="runs", help="output folder (default: runs)")
    args = parser.parse_args(argv)
    result = evaluate(args.suite, args.baseline, args.candidate, args.runs, args.out)
    return EXIT_CODES[result["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
