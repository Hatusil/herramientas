"""Transform handler. R0: <80 lines."""
from __future__ import annotations
from typing import TYPE_CHECKING

from core.constants import COLORS

if TYPE_CHECKING:
    from tools.pdf_tool.ui.main_ui import PDFToolUI


def rotate_pages(ui: PDFToolUI) -> None:
    """Rotate PDF pages."""
    if not ui.files:
        ui.status_label.configure(text="Seleccione un PDF primero", text_color=COLORS.get("warning", "orange"))
        return
    rotate_var = getattr(ui, "rotate_var", None)
    degrees = int(rotate_var.get()) if rotate_var else 90
    rotate_entry = getattr(ui, "rotate_pages", None)
    pages = None
    if rotate_entry and rotate_entry.get().strip():
        pages = [int(p) for p in rotate_entry.get().split(",")]
    ui.status_label.configure(text="Procesando...", text_color="blue")
    ui.process_async("rotate", ui.files, {"degrees": degrees, "pages": pages})


def reorder_pages(ui: PDFToolUI) -> None:
    """Reorder PDF pages."""
    if not ui.files:
        ui.status_label.configure(text="Seleccione un PDF primero", text_color=COLORS.get("warning", "orange"))
        return
    reorder_input = getattr(ui, "reorder_input", None)
    order_str = reorder_input.get().strip() if reorder_input else ""
    if not order_str:
        ui.status_label.configure(text="Ingrese el orden de paginas", text_color=COLORS.get("warning", "orange"))
        return
    try:
        new_order = [int(p) for p in order_str.split(",")]
    except ValueError:
        ui.status_label.configure(text="Orden invalido", text_color="red")
        return
    ui.status_label.configure(text="Procesando...", text_color="blue")
    ui.process_async("reorder", ui.files, {"new_order": new_order})
