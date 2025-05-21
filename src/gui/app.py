from PySide6.QtWidgets import QApplication
import sys
from src.inventory.services import InventoryService
from src.gui.main_window import MainWindow

def main() -> None:
    """Punto de entrada para la aplicación GUI de inventario."""
    app = QApplication(sys.argv)
    inventory_service = InventoryService()
    window = MainWindow(inventory_service)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 