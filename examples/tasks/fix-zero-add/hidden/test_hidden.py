import pytest

from inventory import Inventory, InventoryError


def test_zero_is_rejected():
    with pytest.raises(InventoryError):
        Inventory().add("apple", 0)


def test_negative_still_rejected():
    with pytest.raises(InventoryError):
        Inventory().add("apple", -2)


def test_positive_still_works():
    inv = Inventory()
    inv.add("apple", 1)
    assert inv.quantity("apple") == 1
