from inventory import Inventory


def test_empty():
    inv = Inventory()
    assert inv.total_units() == 0
    assert inv.skus() == []


def test_totals_and_order():
    inv = Inventory()
    inv.add("pear", 2)
    inv.add("apple", 3)
    assert inv.total_units() == 5
    assert inv.skus() == ["apple", "pear"]
