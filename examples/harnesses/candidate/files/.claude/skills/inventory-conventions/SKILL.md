---
name: inventory-conventions
description: Use when adding or changing methods on Inventory in src/inventory.
---

# Adding an Inventory method

1. Put shared checks (SKU exists, enough stock) in one private helper and call it
   before any state change, so failures never leave partial updates.
2. Raise `UnknownSku` / `OutOfStock` / `InventoryError`. Put the message in a
   variable first (`msg = ...; raise X(msg)`), which our ruff config requires.
3. Return lists of SKUs sorted alphabetically unless told otherwise.
4. Add a test in `tests/` for each rule in the request, then run pytest and ruff.
