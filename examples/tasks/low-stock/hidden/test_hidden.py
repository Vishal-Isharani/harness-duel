import pytest

from inventory import Inventory, InventoryError


def _inv():
    inv = Inventory()
    inv.add("pear", 1)
    inv.add("apple", 2)
    inv.add("fig", 10)
    return inv


def test_below_threshold_sorted():
    assert _inv().low_stock(5) == ["apple", "pear"]


def test_threshold_is_exclusive():
    assert _inv().low_stock(2) == ["pear"]


def test_negative_threshold():
    with pytest.raises(InventoryError):
        _inv().low_stock(-1)
