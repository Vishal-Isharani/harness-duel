"""One run = one harness attempting one task in a fresh copy of the repo."""
from __future__ import annotations

import hashlib
import json
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path

from .config import Harness, Suite, Task

HIDDEN_DIR = "tests/hidden_duel"
SKIP = shutil.ignore_patterns("__pycache__", ".pytest_cache", ".ruff_cache")


def sh(cmd: list[str], cwd: Path, timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False)


def count_lint(path: Path) -> int:
    """Number of ruff issues, using the repo's own ruff config (= the team's conventions)."""
    out = sh([sys.executable, "-m", "ruff", "check", "--output-format", "json",
              "--exit-zero", "--no-cache", "."], path).stdout
    return len(json.loads(out or "[]"))


def run_agent(suite: Suite, harness: Harness, task: Task, ws: Path, seed: str) -> tuple[float | None, str | None]:
    """Run the agent in the workspace. Returns (cost in USD, error)."""
    if harness.agent == "demo":
        # Offline stand-in for an agent: copies the good or the sloppy solution at random.
        rng = random.Random(hashlib.sha256(seed.encode()).hexdigest())
        variant = "good" if rng.random() < harness.demo_quality else "bad"
        shutil.copytree(suite.root / "demo" / variant, ws, dirs_exist_ok=True)
        return round(harness.demo_cost * rng.uniform(0.8, 1.2), 4), None

    cmd = ["claude", "-p", task.prompt, "--output-format", "json"]
    cmd += ["--model", harness.model] if harness.model else []
    try:
        res = sh(cmd + harness.args, ws, task.timeout)
    except subprocess.TimeoutExpired:
        return None, "timeout"
    (ws.parent / "agent.json").write_text(res.stdout)
    try:
        cost = json.loads(res.stdout).get("total_cost_usd")
    except json.JSONDecodeError:
        cost = None
    return cost, None if res.returncode == 0 else f"exit code {res.returncode}"


def run_hidden_tests(task: Task, ws: Path) -> tuple[int, int]:
    """Copy the hidden tests in (only now, after the agent is done) and run them."""
    shutil.rmtree(ws / HIDDEN_DIR, ignore_errors=True)
    shutil.copytree(task.hidden, ws / HIDDEN_DIR)
    out = sh([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", HIDDEN_DIR], ws).stdout
    (ws.parent / "hidden_tests.txt").write_text(out)
    summary = out.strip().splitlines()[-1] if out.strip() else ""  # e.g. "1 failed, 2 passed in 0.02s"
    passed = sum(int(n) for n in re.findall(r"(\d+) passed", summary))
    failed = sum(int(n) for n in re.findall(r"(\d+) (?:failed|errors?)\b", summary))
    return passed, max(passed + failed, 1)  # nothing ran counts as a failure


def run_once(suite: Suite, task: Task, harness: Harness, side: str, run: int,
             out: Path, lint_before: int) -> dict:
    folder = out / task.id / f"{side}-{run}"
    ws = folder / "workspace"
    shutil.copytree(suite.repo, ws, ignore=SKIP)
    if harness.files:
        shutil.copytree(harness.files, ws, dirs_exist_ok=True)
    git = ["git", "-c", "user.name=duel", "-c", "user.email=duel@localhost"]
    for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "before agent"]):
        sh(git + args, ws)

    cost, error = run_agent(suite, harness, task, ws, f"{harness.name}/{task.id}/{run}")
    sh(git + ["add", "-A"], ws)
    (folder / "diff.patch").write_text(sh(git + ["diff", "--cached", "HEAD"], ws).stdout)
    new_lint = max(0, count_lint(ws) - lint_before)  # before the hidden tests are added
    passed, total = run_hidden_tests(task, ws)

    result = {"task": task.id, "harness": harness.name, "run": run, "tests_passed": passed,
              "tests_total": total, "new_lint": new_lint, "cost": cost, "error": error}
    (folder / "result.json").write_text(json.dumps(result, indent=2))
    return result
