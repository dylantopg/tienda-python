from typing import Any
from escpos.printer import Usb
from src.inventory.models import Sale


def print_sale_ticket(sale: Sale, total: float) -> None:
    """Imprime un ticket de venta en una impresora USB genérica usando python-escpos.

    Args:
        sale (Sale): Objeto de venta con los ítems vendidos.
        total (float): Total de la venta.
    """
    # VID y PID genéricos, reemplazar si es necesario
    try:
        p = Usb(0x04b8, 0x0202)
        p.set(align='center', font='a', width=2, height=2)
        p.text("TIENDA NUEVA\n")
        p.set(align='left', font='a', width=1, height=1)
        p.text(f"Cliente: {sale.client_id}\n")
        p.text("-----------------------------\n")
        p.text("Producto      Cant  Precio  Total\n")
        p.text("-----------------------------\n")
        for item in sale.items:
            name = item.product.name[:10].ljust(10)
            qty = str(item.quantity).rjust(4)
            price = f"{item.unit_price:.2f}".rjust(7)
            subtotal = f"{item.total:.2f}".rjust(7)
            p.text(f"{name}{qty}{price}{subtotal}\n")
        p.text("-----------------------------\n")
        p.text(f"TOTAL:         ${total:.2f}\n")
        p.text("\nGracias por su compra!\n\n")
        p.cut()
    except Exception as e:
        # Aquí podrías loggear el error o mostrar un mensaje en la GUI
        print(f"Error al imprimir el ticket: {e}") 