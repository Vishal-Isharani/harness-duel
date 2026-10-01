from .errors import InventoryError, OutOfStock, UnknownSku


class Inventory:
    def __init__(self) -> None:
        self._items: dict[str, int] = {}

    def add(self, sku: str, qty: int) -> None:
        if qty <= 0:
            msg = "quantity must be positive"
            raise InventoryError(msg)
        self._items[sku] = self._items.get(sku, 0) + qty

    def quantity(self, sku: str) -> int:
        return self._items.get(sku, 0)

    def _check_available(self, sku: str, qty: int) -> None:
        if sku not in self._items:
            raise UnknownSku(sku)
        if qty > self._items[sku]:
            msg = f"only {self._items[sku]} of {sku} in stock"
            raise OutOfStock(msg)

    def remove(self, sku: str, qty: int) -> None:
        self._check_available(sku, qty)
        self._items[sku] -= qty
        if self._items[sku] == 0:
            del self._items[sku]

    def transfer(self, sku: str, qty: int, to: "Inventory") -> None:
        self._check_available(sku, qty)
        self.remove(sku, qty)
        to.add(sku, qty)

    def skus(self) -> list[str]:
        return sorted(self._items)

    def total_units(self) -> int:
        return sum(self._items.values())

    def low_stock(self, threshold: int) -> list[str]:
        if threshold < 0:
            msg = "threshold must not be negative"
            raise InventoryError(msg)
        return [sku for sku in self.skus() if self._items[sku] < threshold]

    def to_csv(self) -> str:
        rows = ["sku,quantity"] + [f"{sku},{self._items[sku]}" for sku in self.skus()]
        return "\n".join(rows) + "\n"
