import json
from pathlib import Path

import pytest

from duel.cli import evaluate, main

EX = Path(__file__).resolve().parent.parent / "examples"
DEMO = ["--baseline", str(EX / "harnesses/demo-baseline"),
        "--candidate", str(EX / "harnesses/demo-candidate"), "--suite", str(EX)]


def test_demo_candidate_is_detected_as_better(tmp_path):
    result = evaluate(EX, EX / "harnesses/demo-baseline", EX / "harnesses/demo-candidate", 3, tmp_path)
    assert result["verdict"] == "BETTER"


def test_same_harness_on_both_sides_shows_no_difference(tmp_path):
    h = EX / "harnesses/demo-baseline"
    result = evaluate(EX, h, h, 2, tmp_path)
    assert result["verdict"] == "NO CLEAR DIFFERENCE" and result["ties"] == 6


def only_run_dir(out: Path) -> Path:
    (run,) = out.iterdir()
    return run


def test_tasks_subset_runs_only_those_and_report_says_so(tmp_path):
    evaluate(EX, EX / "harnesses/demo-baseline", EX / "harnesses/demo-candidate", 1, tmp_path,
             tasks=["to-csv"])
    run = only_run_dir(tmp_path)
    data = json.loads((run / "report.json").read_text())
    assert [r["task"] for r in data["tasks"]] == ["to-csv"]
    assert data["selected_tasks"] == ["to-csv"]
    assert "1 of 6 selected" in (run / "report.md").read_text()


def test_full_run_has_no_subset_line(tmp_path):
    evaluate(EX, EX / "harnesses/demo-baseline", EX / "harnesses/demo-candidate", 1, tmp_path)
    run = only_run_dir(tmp_path)
    assert json.loads((run / "report.json").read_text())["selected_tasks"] is None
    assert "selected with `--tasks`" not in (run / "report.md").read_text()


def test_tasks_flag_trims_spaces_and_ignores_duplicates_and_empties(tmp_path):
    main(["evaluate", *DEMO, "--runs", "1", "--out", str(tmp_path), "--tasks", " to-csv , to-csv ,"])
    data = json.loads((only_run_dir(tmp_path) / "report.json").read_text())
    assert [r["task"] for r in data["tasks"]] == ["to-csv"]


@pytest.mark.parametrize("value", ["", " , ", "to-csv,nope"])
def test_bad_tasks_flag_exits_3_before_anything_runs(tmp_path, value):
    out = tmp_path / "runs"
    assert main(["evaluate", *DEMO, "--out", str(out), "--tasks", value]) == 3
    assert not out.exists()
