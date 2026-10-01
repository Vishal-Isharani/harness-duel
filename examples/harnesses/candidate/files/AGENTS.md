# inventory

Small Python stock-keeping library. Code in `src/inventory`, tests in `tests/`.

## Before you finish
1. `python -m pytest -q` passes.
2. `ruff check .` reports no issues. Fix them; don't silence them.

## Conventions
- Raise the errors from `inventory/errors.py` (`InventoryError`, `UnknownSku`, `OutOfStock`),
  never builtin exceptions.
- Validate first, then change state: a failed operation must leave every inventory unchanged.
- Type hints on every function, including the return type. No `print()`.
