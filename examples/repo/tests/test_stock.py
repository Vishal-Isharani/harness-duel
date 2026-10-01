import pytest

from inventory import Inventory, InventoryError


def test_add_and_quantity():
    inv = Inventory()
    inv.add("apple", 3)
    inv.add("apple", 2)
    assert inv.quantity("apple") == 5
    assert inv.quantity("pear") == 0


def test_negative_quantity_rejected():
    with pytest.raises(InventoryError):
        Inventory().add("apple", -1)
