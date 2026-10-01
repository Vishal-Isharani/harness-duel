from inventory import Inventory


def test_empty():
    assert Inventory().to_csv() == "sku,quantity\n"


def test_sorted_rows():
    inv = Inventory()
    inv.add("pear", 2)
    inv.add("apple", 3)
    assert inv.to_csv() == "sku,quantity\napple,3\npear,2\n"
