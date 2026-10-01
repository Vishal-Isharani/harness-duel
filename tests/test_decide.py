import random

from duel.decide import chance, duel, verdict


def side(pass_rate=1.0, lint=0.0, cost=0.10):
    return {"pass_rate": pass_rate, "lint": lint, "cost": cost}


def test_tests_decide_first_even_if_candidate_is_messier():
    assert duel(side(0.5, lint=0), side(1.0, lint=9))[0] == "candidate"


def test_lint_decides_when_tests_are_equal():
    assert duel(side(lint=3), side(lint=0))[0] == "candidate"
    assert duel(side(lint=0.2), side(lint=0))[0] == "tie"  # below the 0.5 margin


def test_cost_only_counts_when_it_differs_by_10_percent():
    assert duel(side(cost=0.10), side(cost=0.12))[0] == "baseline"
    assert duel(side(cost=0.10), side(cost=0.105))[0] == "tie"


def test_sign_test_numbers():
    assert chance(6, 6) == 1 / 64  # 6 of 6: 1.6%, counts as BETTER
    assert chance(5, 6) == 7 / 64  # 5 of 6: 11%, could be luck
    assert chance(4, 4) == 1 / 16  # 4 of 4: 6.25%, so 4 tasks can never reach 5%


def d(task, winner, reason="tests 0% vs 100%"):
    return {"task": task, "winner": winner, "reason": reason}


def test_verdicts():
    assert verdict([d(f"t{i}", "candidate") for i in range(6)])["verdict"] == "BETTER"
    assert verdict([d(f"t{i}", "baseline") for i in range(6)])["verdict"] == "WORSE"
    assert verdict([d(f"t{i}", "tie", "no clear difference") for i in range(6)])["verdict"] == "NO CLEAR DIFFERENCE"


def test_safety_rule_blocks_better_when_a_task_regressed_on_tests():
    duels = [d(f"t{i}", "candidate", "new lint issues 3.0 vs 0.0") for i in range(9)]
    duels.append(d("t9", "baseline", "tests 100% vs 50%"))
    result = verdict(duels)
    assert result["verdict"] == "NO CLEAR DIFFERENCE" and "t9" in result["summary"]


def test_false_alarm_rate_when_the_change_does_nothing():
    """If each task is a coin flip, BETTER or WORSE should come up at most ~5% of the time each."""
    rng = random.Random(0)
    alarms = 0
    for _ in range(2000):
        duels = [d(f"t{i}", rng.choice(["candidate", "baseline"])) for i in range(10)]
        alarms += verdict(duels)["verdict"] != "NO CLEAR DIFFERENCE"
    assert alarms / 2000 <= 0.05 * 2
