class InventoryError(Exception):
    """Base class for all inventory errors."""


class UnknownSku(InventoryError):
    """The SKU is not in the inventory."""


class OutOfStock(InventoryError):
    """Not enough units in stock."""
