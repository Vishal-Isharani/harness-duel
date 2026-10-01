import os

from .errors import InventoryError


class Inventory:
    def __init__(self) -> None:
        self._items: dict[str, int] = {}

    def add(self, sku: str, qty: int) -> None:
        if qty < 0:
            msg = "quantity must be positive"
            raise InventoryError(msg)
        self._items[sku] = self._items.get(sku, 0) + qty

    def quantity(self, sku: str) -> int:
        return self._items.get(sku, 0)

    def remove(self, sku, qty):
        if sku not in self._items:
            raise KeyError("unknown sku " + sku)
        self._items[sku] -= qty
        if self._items[sku] < 0:
            raise InventoryError("not enough stock")
        print("removed", sku)

    def transfer(self, sku, qty, to):
        to.add(sku, qty)
        self.remove(sku, qty)

    def skus(self):
        return list(self._items)

    def total_units(self) -> int:
        return sum(self._items.values())

    def low_stock(self, threshold):
        return [s for s in self._items if self._items[s] <= threshold]

    def to_csv(self):
        return "sku,quantity\n" + "\n".join(f"{k},{v}" for k, v in self._items.items())
