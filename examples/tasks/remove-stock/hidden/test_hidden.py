import pytest

from inventory import Inventory, OutOfStock, UnknownSku


def test_remove_some():
    inv = Inventory()
    inv.add("apple", 5)
    inv.remove("apple", 2)
    assert inv.quantity("apple") == 3


def test_unknown_sku():
    with pytest.raises(UnknownSku):
        Inventory().remove("pear", 1)


def test_out_of_stock_leaves_stock_unchanged():
    inv = Inventory()
    inv.add("apple", 2)
    with pytest.raises(OutOfStock):
        inv.remove("apple", 5)
    assert inv.quantity("apple") == 2


def test_zero_units_disappear():
    inv = Inventory()
    inv.add("apple", 2)
    inv.remove("apple", 2)
    assert "apple" not in inv.skus()
