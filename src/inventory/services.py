import sqlite3
from typing import List, Optional
from .models import Product, Sale, SaleItem, ProductPriceHistory
from datetime import datetime

class InventoryRepository:
    """Repositorio para persistencia de productos e historial de precios en SQLite."""
    def __init__(self, db_path: str = "inventory.db") -> None:
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self) -> None:
        cur = self.conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS products (
            barcode TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            purchase_price REAL,
            retail_price REAL,
            wholesale_price REAL,
            quantity INTEGER
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_barcode TEXT,
            retail_price REAL,
            wholesale_price REAL,
            timestamp TEXT
        )''')
        self.conn.commit()

    def save_product(self, product: Product) -> None:
        cur = self.conn.cursor()
        cur.execute('''REPLACE INTO products (barcode, name, description, purchase_price, retail_price, wholesale_price, quantity)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (product.barcode, product.name, product.description, product.purchase_price, product.retail_price, product.wholesale_price, product.quantity))
        self.conn.commit()

    def save_price_history(self, history: ProductPriceHistory) -> None:
        cur = self.conn.cursor()
        cur.execute('''INSERT INTO price_history (product_barcode, retail_price, wholesale_price, timestamp)
            VALUES (?, ?, ?, ?)''',
            (history.product_barcode, history.retail_price, history.wholesale_price, history.timestamp.isoformat()))
        self.conn.commit()

    def get_all_products(self) -> List[Product]:
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM products')
        rows = cur.fetchall()
        products = []
        for row in rows:
            product = Product(
                barcode=row[0], name=row[1], description=row[2], purchase_price=row[3],
                retail_price=row[4], wholesale_price=row[5], quantity=row[6]
            )
            product.price_history = self.get_price_history(product.barcode)
            products.append(product)
        return products

    def get_product_by_barcode(self, barcode: str) -> Optional[Product]:
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM products WHERE barcode = ?', (barcode,))
        row = cur.fetchone()
        if row:
            product = Product(
                barcode=row[0], name=row[1], description=row[2], purchase_price=row[3],
                retail_price=row[4], wholesale_price=row[5], quantity=row[6]
            )
            product.price_history = self.get_price_history(product.barcode)
            return product
        return None

    def get_products_by_name(self, name: str) -> List[Product]:
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM products WHERE name LIKE ?', (f'%{name}%',))
        rows = cur.fetchall()
        products = []
        for row in rows:
            product = Product(
                barcode=row[0], name=row[1], description=row[2], purchase_price=row[3],
                retail_price=row[4], wholesale_price=row[5], quantity=row[6]
            )
            product.price_history = self.get_price_history(product.barcode)
            products.append(product)
        return products

    def get_price_history(self, barcode: str) -> List[ProductPriceHistory]:
        cur = self.conn.cursor()
        cur.execute('SELECT product_barcode, retail_price, wholesale_price, timestamp FROM price_history WHERE product_barcode = ? ORDER BY timestamp DESC', (barcode,))
        rows = cur.fetchall()
        return [ProductPriceHistory(product_barcode=row[0], retail_price=row[1], wholesale_price=row[2], timestamp=datetime.fromisoformat(row[3])) for row in rows]

class SaleRepository:
    """Repositorio para persistencia de ventas (básico, solo estructura)."""
    def __init__(self, db_path: str = "inventory.db") -> None:
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self) -> None:
        cur = self.conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT,
            timestamp TEXT
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER,
            product_barcode TEXT,
            quantity INTEGER,
            unit_price REAL,
            FOREIGN KEY(sale_id) REFERENCES sales(id)
        )''')
        self.conn.commit()

    def save_sale(self, sale: Sale, timestamp: datetime) -> int:
        cur = self.conn.cursor()
        cur.execute('INSERT INTO sales (client_id, timestamp) VALUES (?, ?)', (sale.client_id, timestamp.isoformat()))
        sale_id = cur.lastrowid
        for item in sale.items:
            cur.execute('''INSERT INTO sale_items (sale_id, product_barcode, quantity, unit_price) VALUES (?, ?, ?, ?)''',
                        (sale_id, item.product.barcode, item.quantity, item.unit_price))
        self.conn.commit()
        return sale_id

    def get_sales_summary(self, start_date: datetime, end_date: datetime) -> List[dict]:
        cur = self.conn.cursor()
        cur.execute('''SELECT s.id, s.client_id, s.timestamp, si.product_barcode, si.quantity, si.unit_price
                       FROM sales s
                       JOIN sale_items si ON s.id = si.sale_id
                       WHERE s.timestamp BETWEEN ? AND ?
                       ORDER BY s.timestamp''',
                    (start_date.isoformat(), end_date.isoformat()))
        rows = cur.fetchall()
        summary = []
        for row in rows:
            summary.append({
                'sale_id': row[0],
                'client_id': row[1],
                'timestamp': row[2],
                'product_barcode': row[3],
                'quantity': row[4],
                'unit_price': row[5],
                'total': row[4] * row[5]
            })
        return summary

class InventoryService:
    """Servicio para gestionar el inventario de productos con persistencia."""
    def __init__(self, repository: Optional[InventoryRepository] = None) -> None:
        self.repository = repository or InventoryRepository()
        self.products: List[Product] = self.repository.get_all_products()

    def add_product(self, product: Product) -> None:
        if self.get_product_by_barcode(product.barcode):
            raise ValueError(f"El producto con código {product.barcode} ya existe.")
        self.products.append(product)
        self.repository.save_product(product)
        if product.price_history:
            for h in product.price_history:
                self.repository.save_price_history(h)

    def refill_product(self, barcode: str, amount: int) -> None:
        product = self.get_product_by_barcode(barcode)
        if not product:
            raise ValueError(f"Producto con código {barcode} no encontrado.")
        product.refill(amount)
        self.repository.save_product(product)

    def edit_product(self, barcode: str, **kwargs) -> None:
        product = self.get_product_by_barcode(barcode)
        if not product:
            raise ValueError(f"Producto con código {barcode} no encontrado.")
        old_retail = product.retail_price
        old_wholesale = product.wholesale_price
        product.update(**kwargs)
        self.repository.save_product(product)
        # Guardar historial si cambió precio
        if ("retail_price" in kwargs and kwargs["retail_price"] != old_retail) or ("wholesale_price" in kwargs and kwargs["wholesale_price"] != old_wholesale):
            history = ProductPriceHistory(
                product_barcode=product.barcode,
                retail_price=product.retail_price,
                wholesale_price=product.wholesale_price,
                timestamp=datetime.now()
            )
            self.repository.save_price_history(history)
            product.price_history.insert(0, history)

    def get_product_by_barcode(self, barcode: str) -> Optional[Product]:
        return self.repository.get_product_by_barcode(barcode)

    def get_products_by_name(self, name: str) -> List[Product]:
        return self.repository.get_products_by_name(name)

    def get_inventory_table(self) -> List[dict]:
        return [p.__dict__ for p in self.products]

class SaleService:
    """Servicio para gestionar el proceso de ventas."""
    def __init__(self, inventory_service: InventoryService, repository: Optional[SaleRepository] = None) -> None:
        self.inventory_service = inventory_service
        self.repository = repository or SaleRepository()
        self.current_sale: Optional[Sale] = None

    def start_sale(self, client_id: str) -> None:
        self.current_sale = Sale(client_id=client_id)

    def add_item(self, barcode: str, quantity: int, unit_price: float) -> None:
        if not self.current_sale:
            raise ValueError("No hay venta iniciada.")
        product = self.inventory_service.get_product_by_barcode(barcode)
        if not product:
            raise ValueError("Producto no encontrado.")
        if quantity > product.quantity:
            raise ValueError("No hay suficiente inventario.")
        item = SaleItem(product=product, quantity=quantity, unit_price=unit_price)
        self.current_sale.add_item(item)
        product.quantity -= quantity
        self.inventory_service.repository.save_product(product)

    def remove_item(self, index: int) -> None:
        if not self.current_sale:
            raise ValueError("No hay venta iniciada.")
        item = self.current_sale.items[index]
        item.product.quantity += item.quantity
        self.current_sale.remove_item(index)
        self.inventory_service.repository.save_product(item.product)

    def cancel_sale(self) -> None:
        if not self.current_sale:
            return
        for item in self.current_sale.items:
            item.product.quantity += item.quantity
            self.inventory_service.repository.save_product(item.product)
        self.current_sale = None

    def finalize_sale(self) -> float:
        if not self.current_sale:
            raise ValueError("No hay venta iniciada.")
        total = self.current_sale.total()
        timestamp = datetime.now()
        sale_id = self.repository.save_sale(self.current_sale, timestamp)
        self.current_sale = None
        return total

    def get_items(self) -> List[SaleItem]:
        if not self.current_sale:
            return []
        return self.current_sale.items

    def get_total(self) -> float:
        if not self.current_sale:
            return 0.0
        return self.current_sale.total()

    def get_sales_summary(self, start_date: datetime, end_date: datetime) -> List[dict]:
        return self.repository.get_sales_summary(start_date, end_date) 