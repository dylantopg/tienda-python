import pytest
from src.inventory.models import Product
from src.inventory.services import InventoryService

def test_add_and_get_product() -> None:
    """Prueba agregar y obtener un producto."""
    service = InventoryService()
    product = Product(
        barcode="123",
        name="Coca Cola",
        purchase_price=1.0,
        retail_price=1.5,
        wholesale_price=1.2,
        quantity=10
    )
    service.add_product(product)
    assert service.get_product_by_barcode("123") is product

def test_refill_product() -> None:
    """Prueba el refill de un producto existente."""
    service = InventoryService()
    product = Product(barcode="123", name="Coca Cola", quantity=5)
    service.add_product(product)
    service.refill_product("123", 10)
    assert product.quantity == 15

    with pytest.raises(ValueError):
        service.refill_product("999", 5)

    with pytest.raises(ValueError):
        service.refill_product("123", -5)

def test_edit_product() -> None:
    """Prueba editar los campos de un producto."""
    service = InventoryService()
    product = Product(barcode="123", name="Coca Cola", quantity=5)
    service.add_product(product)
    service.edit_product("123", name="Pepsi", retail_price=2.0)
    assert product.name == "Pepsi"
    assert product.retail_price == 2.0

    with pytest.raises(ValueError):
        service.edit_product("999", name="Fanta")

def test_get_inventory_table() -> None:
    """Prueba la obtención de la tabla de inventario."""
    service = InventoryService()
    p1 = Product(barcode="1", name="A", quantity=2)
    p2 = Product(barcode="2", name="B", quantity=3)
    service.add_product(p1)
    service.add_product(p2)
    table = service.get_inventory_table()
    assert isinstance(table, list)
    assert any(row["barcode"] == "1" for row in table)
    assert any(row["barcode"] == "2" for row in table) 