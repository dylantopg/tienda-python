from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt
from src.inventory.services import InventoryService, SaleService

class SaleWindow(QDialog):
    """Ventana para registrar una venta."""
    def __init__(self, inventory_service: InventoryService, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Registrar Venta")
        self.inventory_service = inventory_service
        self.sale_service = SaleService(inventory_service)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()

        # Cliente
        client_layout = QHBoxLayout()
        client_layout.addWidget(QLabel("ID Cliente:"))
        self.client_input = QLineEdit()
        client_layout.addWidget(self.client_input)
        start_btn = QPushButton("Iniciar venta")
        start_btn.clicked.connect(self._start_sale)
        client_layout.addWidget(start_btn)
        layout.addLayout(client_layout)

        # Buscar producto
        search_layout = QHBoxLayout()
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Código de barras")
        search_btn = QPushButton("Buscar por código")
        search_btn.clicked.connect(self._search_by_barcode)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Buscar por nombre")
        name_btn = QPushButton("Buscar por nombre")
        name_btn.clicked.connect(self._search_by_name)
        search_layout.addWidget(self.barcode_input)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(self.name_input)
        search_layout.addWidget(name_btn)
        layout.addLayout(search_layout)

        # Info producto seleccionado
        self.selected_label = QLabel("")
        layout.addWidget(self.selected_label)

        # Unidades y agregar item
        item_layout = QHBoxLayout()
        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("Unidades")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Precio unitario")
        add_item_btn = QPushButton("Agregar item de venta")
        add_item_btn.clicked.connect(self._add_item)
        item_layout.addWidget(self.qty_input)
        item_layout.addWidget(self.price_input)
        item_layout.addWidget(add_item_btn)
        layout.addLayout(item_layout)

        # Tabla de items de venta
        self.items_table = QTableWidget(0, 4)
        self.items_table.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio unitario", "Total"])
        layout.addWidget(self.items_table)

        # Botones de control
        btn_layout = QHBoxLayout()
        remove_btn = QPushButton("Eliminar item")
        remove_btn.clicked.connect(self._remove_item)
        finish_btn = QPushButton("Finalizar venta")
        finish_btn.clicked.connect(self._finalize_sale)
        cancel_btn = QPushButton("Cancelar venta")
        cancel_btn.clicked.connect(self._cancel_sale)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(finish_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        # Total
        self.total_label = QLabel("Total: $0.00")
        layout.addWidget(self.total_label)

        self.setLayout(layout)
        self.selected_product = None

    def _start_sale(self) -> None:
        client_id = self.client_input.text().strip()
        if not client_id:
            QMessageBox.warning(self, "Atención", "Ingrese el ID del cliente.")
            return
        self.sale_service.start_sale(client_id)
        self._refresh_items()
        self.selected_label.setText("")
        self.selected_product = None

    def _search_by_barcode(self) -> None:
        barcode = self.barcode_input.text().strip()
        product = self.inventory_service.get_product_by_barcode(barcode)
        if product:
            self.selected_product = product
            price_info = self._get_latest_price_info(product)
            self.selected_label.setText(f"{product.name} (Stock: {product.quantity})\n{price_info}")
            self.price_input.setText(str(product.retail_price))
        else:
            QMessageBox.warning(self, "No encontrado", "Producto no encontrado.")

    def _search_by_name(self) -> None:
        name = self.name_input.text().strip().lower()
        matches = self.inventory_service.get_products_by_name(name)
        if matches:
            product = matches[0]
            self.selected_product = product
            price_info = self._get_latest_price_info(product)
            self.selected_label.setText(f"{product.name} (Stock: {product.quantity})\n{price_info}")
            self.price_input.setText(str(product.retail_price))
        else:
            QMessageBox.warning(self, "No encontrado", "No hay coincidencias.")

    def _get_latest_price_info(self, product) -> str:
        if product.price_history:
            latest = product.price_history[0]
            return f"Precio Detal: {latest.retail_price} | Precio Mayor: {latest.wholesale_price} (Actualizado: {latest.timestamp:%Y-%m-%d %H:%M})"
        return f"Precio Detal: {product.retail_price} | Precio Mayor: {product.wholesale_price}"

    def _add_item(self) -> None:
        if not self.selected_product:
            QMessageBox.warning(self, "Atención", "Seleccione un producto.")
            return
        try:
            quantity = int(self.qty_input.text())
            unit_price = float(self.price_input.text())
            self.sale_service.add_item(self.selected_product.barcode, quantity, unit_price)
            self._refresh_items()
            self.qty_input.clear()
            self.price_input.setText(str(self.selected_product.retail_price))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _refresh_items(self) -> None:
        items = self.sale_service.get_items()
        self.items_table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.items_table.setItem(row, 0, QTableWidgetItem(item.product.name))
            self.items_table.setItem(row, 1, QTableWidgetItem(str(item.quantity)))
            self.items_table.setItem(row, 2, QTableWidgetItem(str(item.unit_price)))
            self.items_table.setItem(row, 3, QTableWidgetItem(str(item.total)))
        self.total_label.setText(f"Total: ${self.sale_service.get_total():.2f}")

    def _remove_item(self) -> None:
        row = self.items_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atención", "Seleccione un item para eliminar.")
            return
        self.sale_service.remove_item(row)
        self._refresh_items()

    def _finalize_sale(self) -> None:
        try:
            total = self.sale_service.finalize_sale()
            # Refrescar inventario en la ventana principal
            if hasattr(self.parent(), '_refresh_table'):
                self.parent()._refresh_table()
            QMessageBox.information(self, "Venta finalizada", f"Total a pagar: ${total:.2f}")
            self._reset_form()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _cancel_sale(self) -> None:
        self.sale_service.cancel_sale()
        self._reset_form()

    def _reset_form(self) -> None:
        self.client_input.clear()
        self.barcode_input.clear()
        self.name_input.clear()
        self.selected_label.setText("")
        self.qty_input.clear()
        self.price_input.clear()
        self.items_table.setRowCount(0)
        self.total_label.setText("Total: $0.00")
        self.selected_product = None 