import pytest

from inventory import Inventory, OutOfStock, UnknownSku


def test_transfer_moves_units():
    a, b = Inventory(), Inventory()
    a.add("apple", 5)
    a.transfer("apple", 3, b)
    assert (a.quantity("apple"), b.quantity("apple")) == (2, 3)


def test_unknown_sku():
    with pytest.raises(UnknownSku):
        Inventory().transfer("pear", 1, Inventory())


def test_failed_transfer_changes_nothing():
    a, b = Inventory(), Inventory()
    a.add("apple", 1)
    with pytest.raises(OutOfStock):
        a.transfer("apple", 5, b)
    assert (a.quantity("apple"), b.quantity("apple")) == (1, 0)
