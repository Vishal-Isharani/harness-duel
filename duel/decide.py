"""Who won each task, and is the overall result more than luck?

Per task, the first clear difference decides the winner:
  1. hidden tests passed (does it do what was asked?)
  2. new lint issues      (does it follow the team's conventions?)
  3. cost                 (only if it differs by 10% or more)
Otherwise the task is a tie.

Overall, a sign test: if the change did nothing, each decisive task would be a
coin flip. BETTER/WORSE means the wins would happen by luck less than 5% of the time.
"""
from __future__ import annotations

from math import comb
from statistics import mean

ALPHA = 0.05


def summarize(runs: list[dict]) -> dict:
    """Average the runs of one harness on one task."""
    costs = [r["cost"] for r in runs]
    return {
        "pass_rate": mean(r["tests_passed"] / r["tests_total"] for r in runs),
        "lint": mean(r["new_lint"] for r in runs),
        "cost": None if None in costs else mean(costs),
        "errors": sum(1 for r in runs if r["error"]),
    }


def duel(base: dict, cand: dict) -> tuple[str, str]:
    """Return (winner, reason). winner is "candidate", "baseline" or "tie"."""
    if cand["pass_rate"] != base["pass_rate"]:
        winner = "candidate" if cand["pass_rate"] > base["pass_rate"] else "baseline"
        return winner, f"tests {base['pass_rate']:.0%} vs {cand['pass_rate']:.0%}"
    if abs(cand["lint"] - base["lint"]) >= 0.5:
        winner = "candidate" if cand["lint"] < base["lint"] else "baseline"
        return winner, f"new lint issues {base['lint']:.1f} vs {cand['lint']:.1f}"
    if base["cost"] and cand["cost"] is not None:
        change = cand["cost"] / base["cost"] - 1
        if abs(change) >= 0.10:
            return ("candidate" if change < 0 else "baseline"), f"cost {change:+.0%}"
    return "tie", "no clear difference"


def chance(wins: int, n: int) -> float:
    """Chance of `wins` or more heads in n fair coin flips."""
    return sum(comb(n, k) for k in range(wins, n + 1)) / 2 ** n


def verdict(duels: list[dict]) -> dict:
    wins = sum(d["winner"] == "candidate" for d in duels)
    losses = sum(d["winner"] == "baseline" for d in duels)
    n = wins + losses
    p_better, p_worse = (chance(wins, n), chance(losses, n)) if n else (1.0, 1.0)
    broke = [d["task"] for d in duels if d["winner"] == "baseline" and d["reason"].startswith("tests")]
    summary = f"candidate won {wins}, baseline won {losses}, ties {len(duels) - n}"

    if p_worse < ALPHA:
        result = "WORSE"
    elif p_better < ALPHA and not broke:
        result = "BETTER"
    else:
        result = "NO CLEAR DIFFERENCE"
    if p_better < ALPHA and broke:  # safety rule: never BETTER if it passed fewer tests anywhere
        summary += f"; not BETTER because it passed fewer hidden tests on: {', '.join(broke)}"
    return {"verdict": result, "summary": summary, "wins": wins, "losses": losses,
            "ties": len(duels) - n, "p_better": p_better}
