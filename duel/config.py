"""Inputs: a suite (an example repo + tasks) and two harnesses to compare."""
from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


class InputError(Exception):
    """Bad input (suite or task selection); `duel` exits with code 3, never a verdict code."""


@dataclass
class Harness:
    name: str
    agent: str  # "claude-code", or "demo" for the offline stand-in
    model: str | None
    args: list[str]
    files: Path | None  # copied into the repo before the agent starts (AGENTS.md, skills, ...)
    demo_quality: float  # demo only: chance of producing the good solution
    demo_cost: float  # demo only: average cost per run in USD


@dataclass
class Task:
    id: str
    prompt: str
    hidden: Path  # tests that decide the task; the agent never sees them
    timeout: int


@dataclass
class Suite:
    root: Path
    repo: Path
    tasks: list[Task]
    total_tasks: int  # tasks in the suite before any `only` selection


def load_harness(path: str | Path) -> Harness:
    root = Path(path).resolve()
    data = tomllib.loads((root / "harness.toml").read_text())
    return Harness(
        name=data.get("name", root.name),
        agent=data.get("agent", "claude-code"),
        model=data.get("model"),
        args=data.get("args", []),
        files=root / "files" if (root / "files").is_dir() else None,
        demo_quality=data.get("demo_quality", 0.5),
        demo_cost=data.get("demo_cost", 0.10),
    )


def load_suite(path: str | Path, only: list[str] | None = None) -> Suite:
    """Load the suite's tasks; `only` keeps just those task ids (in suite order)."""
    root = Path(path).resolve()
    tasks = []
    for file in sorted(root.glob("tasks/*/task.toml")):
        data = tomllib.loads(file.read_text())
        tasks.append(Task(file.parent.name, data["prompt"].strip(), file.parent / "hidden",
                          data.get("timeout", 600)))
    if not tasks:
        raise InputError(f"No tasks found in {root / 'tasks'}")
    total = len(tasks)
    if only is not None:
        known = [t.id for t in tasks]
        unknown = [i for i in only if i not in known]
        if unknown:
            raise InputError(f"Unknown task id(s): {', '.join(unknown)}. Available: {', '.join(known)}")
        tasks = [t for t in tasks if t.id in only]
    return Suite(root, root / "repo", tasks, total)
