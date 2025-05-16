from typing import Optional, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ProductPriceHistory:
    """Historial de precios de un producto."""
    product_barcode: str
    retail_price: float
    wholesale_price: float
    timestamp: datetime

@dataclass
class Product:
    """Representa un producto en el inventario."""
    barcode: str
    name: str
    description: Optional[str] = None
    purchase_price: float = 0.0
    retail_price: float = 0.0
    wholesale_price: float = 0.0
    quantity: int = 0
    price_history: List[ProductPriceHistory] = field(default_factory=list)
    
    def refill(self, amount: int) -> None:
        """Agrega cantidad al inventario."""
        if amount < 0:
            raise ValueError("La cantidad a agregar debe ser positiva.")
        self.quantity += amount

    def update(self, **kwargs) -> None:
        """Actualiza los campos del producto con validación básica y registra historial de precios si cambian."""
        price_changed = False
        old_retail = self.retail_price
        old_wholesale = self.wholesale_price
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        if ("retail_price" in kwargs and kwargs["retail_price"] != old_retail) or ("wholesale_price" in kwargs and kwargs["wholesale_price"] != old_wholesale):
            price_changed = True
        if price_changed:
            self.price_history.append(ProductPriceHistory(
                product_barcode=self.barcode,
                retail_price=self.retail_price,
                wholesale_price=self.wholesale_price,
                timestamp=datetime.now()
            ))

@dataclass
class SaleItem:
    """Representa un ítem de venta (producto y cantidad)."""
    product: Product
    quantity: int
    unit_price: float

    @property
    def total(self) -> float:
        """Calcula el total del ítem de venta."""
        return self.quantity * self.unit_price

@dataclass
class Sale:
    """Representa una venta con múltiples ítems."""
    client_id: str
    items: List[SaleItem] = field(default_factory=list)

    def add_item(self, item: SaleItem) -> None:
        """Agrega un ítem a la venta."""
        self.items.append(item)

    def remove_item(self, index: int) -> None:
        """Elimina un ítem de la venta por índice."""
        if 0 <= index < len(self.items):
            del self.items[index]

    def total(self) -> float:
        """Calcula el total a pagar de la venta."""
        return sum(item.total for item in self.items)

    def clear(self) -> None:
        """Elimina todos los ítems de la venta."""
        self.items.clear() 