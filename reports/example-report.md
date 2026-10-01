# Harness duel: `baseline` vs `candidate`

## Verdict: NO CLEAR DIFFERENCE

Candidate won 0, baseline won 3, ties 3. 6 tasks, 1 run(s) per task per harness.
Chance of this many candidate wins if the change did nothing: 100.0%.

| Task | Winner | Why | Tests | New lint | Cost | Errors |
|---|---|---|---|---|---|---|
| `fix-zero-add` | baseline | cost +33% | 100% → 100% | 0.0 → 0.0 | $0.076 → $0.101 | 0 → 0 |
| `low-stock` | tie | no clear difference | 100% → 100% | 0.0 → 0.0 | $0.079 → $0.084 | 0 → 0 |
| `remove-stock` | baseline | cost +14% | 75% → 75% | 0.0 → 0.0 | $0.080 → $0.091 | 0 → 0 |
| `to-csv` | tie | no clear difference | 100% → 100% | 0.0 → 0.0 | $0.085 → $0.079 | 0 → 0 |
| `total-units` | tie | no clear difference | 100% → 100% | 0.0 → 0.0 | $0.083 → $0.084 | 0 → 0 |
| `transfer` | baseline | cost +20% | 100% → 100% | 0.0 → 0.0 | $0.097 → $0.116 | 0 → 0 |

Columns show baseline → candidate, averaged over runs.
Evidence for every run (`diff.patch`, `hidden_tests.txt`, `result.json`) is in this folder.
