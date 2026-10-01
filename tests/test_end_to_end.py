from pathlib import Path

from duel.cli import evaluate

EX = Path(__file__).resolve().parent.parent / "examples"


def test_demo_candidate_is_detected_as_better(tmp_path):
    result = evaluate(EX, EX / "harnesses/demo-baseline", EX / "harnesses/demo-candidate", 3, tmp_path)
    assert result["verdict"] == "BETTER"


def test_same_harness_on_both_sides_shows_no_difference(tmp_path):
    h = EX / "harnesses/demo-baseline"
    result = evaluate(EX, h, h, 2, tmp_path)
    assert result["verdict"] == "NO CLEAR DIFFERENCE" and result["ties"] == 6
