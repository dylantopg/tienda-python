from typing import Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QMessageBox, QInputDialog, QTabWidget, QFileDialog, QDateEdit, QToolBar
)
from PySide6.QtCore import Qt, QDate
from src.inventory.models import Product
from src.inventory.services import InventoryService
from src.gui.sale_window import SaleWindow
import pandas as pd
from datetime import datetime

class MainWindow(QMainWindow):
    """Ventana principal para la gestión de inventario y ventas."""
    def __init__(self, inventory_service: InventoryService) -> None:
        super().__init__()
        self.setWindowTitle("Gestión de Inventario y Ventas")
        self.inventory_service = inventory_service
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configura los widgets de la ventana principal con tabs."""
        tabs = QTabWidget()
        # Tab Inventario
        self.inventory_tab = QWidget()
        self._setup_inventory_tab()
        tabs.addTab(self.inventory_tab, "Inventario")
        # Tab Ventas
        self.sales_tab = SaleWindow(self.inventory_service, self)
        tabs.addTab(self.sales_tab, "Ventas")
        self.setCentralWidget(tabs)
        # Botón exportar CSV en un QToolBar
        export_btn = QPushButton("Exportar resumen a CSV")
        export_btn.clicked.connect(self._export_csv)
        toolbar = QToolBar("Exportar")
        toolbar.addWidget(export_btn)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

    def _setup_inventory_tab(self) -> None:
        layout = QVBoxLayout()
        # Tabla de inventario
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Código", "Nombre", "Descripción", "Compra", "Venta Detal", "Venta Mayor", "Cantidad"
        ])
        layout.addWidget(self.table)
        # Controles para agregar producto
        form_layout = QHBoxLayout()
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Código de barras")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre")
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Descripción (opcional)")
        self.purchase_input = QLineEdit()
        self.purchase_input.setPlaceholderText("Precio compra")
        self.retail_input = QLineEdit()
        self.retail_input.setPlaceholderText("Precio detal")
        self.wholesale_input = QLineEdit()
        self.wholesale_input.setPlaceholderText("Precio mayor")
        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("Cantidad")
        form_layout.addWidget(self.barcode_input)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.desc_input)
        form_layout.addWidget(self.purchase_input)
        form_layout.addWidget(self.retail_input)
        form_layout.addWidget(self.wholesale_input)
        form_layout.addWidget(self.qty_input)
        layout.addLayout(form_layout)
        # Botones
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Agregar producto")
        add_btn.clicked.connect(self._add_product)
        refill_btn = QPushButton("Refill producto")
        refill_btn.clicked.connect(self._refill_product)
        edit_btn = QPushButton("Editar producto")
        edit_btn.clicked.connect(self._edit_product)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(refill_btn)
        btn_layout.addWidget(edit_btn)
        layout.addLayout(btn_layout)
        self.inventory_tab.setLayout(layout)
        self._refresh_table()

    def _refresh_table(self) -> None:
        """Actualiza la tabla de inventario."""
        data = self.inventory_service.get_inventory_table()
        self.table.setRowCount(len(data))
        for row, prod in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(str(prod["barcode"])))
            self.table.setItem(row, 1, QTableWidgetItem(prod["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(prod.get("description") or ""))
            self.table.setItem(row, 3, QTableWidgetItem(str(prod["purchase_price"])))
            self.table.setItem(row, 4, QTableWidgetItem(str(prod["retail_price"])))
            self.table.setItem(row, 5, QTableWidgetItem(str(prod["wholesale_price"])))
            self.table.setItem(row, 6, QTableWidgetItem(str(prod["quantity"])))

    def _add_product(self) -> None:
        """Agrega un producto al inventario desde los campos de entrada."""
        try:
            product = Product(
                barcode=self.barcode_input.text(),
                name=self.name_input.text(),
                description=self.desc_input.text() or None,
                purchase_price=float(self.purchase_input.text()),
                retail_price=float(self.retail_input.text()),
                wholesale_price=float(self.wholesale_input.text()),
                quantity=int(self.qty_input.text())
            )
            self.inventory_service.add_product(product)
            self._refresh_table()
            self._clear_inputs()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _refill_product(self) -> None:
        """Permite hacer refill de un producto seleccionado."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atención", "Seleccione un producto en la tabla.")
            return
        barcode = self.table.item(row, 0).text()
        amount, ok = QInputDialog.getInt(self, "Refill", "Cantidad a agregar:", 1, 1)
        if ok:
            try:
                self.inventory_service.refill_product(barcode, amount)
                self._refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _edit_product(self) -> None:
        """Permite editar los datos de un producto seleccionado."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atención", "Seleccione un producto en la tabla.")
            return
        barcode = self.table.item(row, 0).text()
        try:
            kwargs = {}
            if self.name_input.text():
                kwargs["name"] = self.name_input.text()
            if self.desc_input.text():
                kwargs["description"] = self.desc_input.text()
            if self.purchase_input.text():
                kwargs["purchase_price"] = float(self.purchase_input.text())
            if self.retail_input.text():
                kwargs["retail_price"] = float(self.retail_input.text())
            if self.wholesale_input.text():
                kwargs["wholesale_price"] = float(self.wholesale_input.text())
            if self.qty_input.text():
                kwargs["quantity"] = int(self.qty_input.text())
            self.inventory_service.edit_product(barcode, **kwargs)
            self._refresh_table()
            self._clear_inputs()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _clear_inputs(self) -> None:
        """Limpia los campos de entrada."""
        self.barcode_input.clear()
        self.name_input.clear()
        self.desc_input.clear()
        self.purchase_input.clear()
        self.retail_input.clear()
        self.wholesale_input.clear()
        self.qty_input.clear()

    def _export_csv(self) -> None:
        # Pedir fechas
        start_date, ok1 = self._get_date("Fecha inicial")
        if not ok1:
            return
        end_date, ok2 = self._get_date("Fecha final")
        if not ok2:
            return
        # Pedir ruta de archivo
        path, _ = QFileDialog.getSaveFileName(self, "Guardar CSV", "resumen.csv", "CSV Files (*.csv)")
        if not path:
            return
        # Inventario
        inventory = self.inventory_service.get_inventory_table()
        df_inv = pd.DataFrame(inventory)
        # Ventas
        sales = self.sales_tab.sale_service.get_sales_summary(start_date, end_date)
        df_sales = pd.DataFrame(sales)
        # Guardar a Excel (CSV multi-sheet no existe, así que usamos Excel)
        excel_path = path if path.endswith(".xlsx") else path + ".xlsx"
        with pd.ExcelWriter(excel_path) as writer:
            df_inv.to_excel(writer, sheet_name="Inventario", index=False)
            df_sales.to_excel(writer, sheet_name="Ventas", index=False)

    def _get_date(self, title: str) -> tuple[datetime, bool]:
        dlg = QDateEdit()
        dlg.setCalendarPopup(True)
        dlg.setDate(QDate.currentDate())
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(f"Seleccione {title.lower()}:")
        msg.layout().addWidget(dlg)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        result = msg.exec()
        if result == QMessageBox.Ok:
            qdate = dlg.date()
            return datetime(qdate.year(), qdate.month(), qdate.day()), True
        return datetime.now(), False 