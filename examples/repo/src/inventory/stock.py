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
