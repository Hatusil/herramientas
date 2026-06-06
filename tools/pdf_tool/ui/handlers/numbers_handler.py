"""Page numbers handler. R0: <80 lines."""
from __future__ import annotations
from typing import TYPE_CHECKING

from core.constants import COLORS

if TYPE_CHECKING:
    from tools.pdf_tool.ui.main_ui import PDFToolUI


def add_page_numbers(ui: PDFToolUI) -> None:
    """Add page numbers to PDF."""
    if not ui.files:
        ui.status_label.configure(text="Seleccione un PDF primero", text_color=COLORS.get("warning", "orange"))
        return
    num_position = getattr(ui, "num_position", None)
    position = num_position.get() if num_position else "footer"
    num_start = getattr(ui, "num_start", None)
    start = int(num_start.get() or 1) if num_start else 1
    num_format = getattr(ui, "num_format", None)
    fmt = num_format.get() if num_format else "Pagina {n} de {total}"
    ui.status_label.configure(text="Procesando...", text_color="blue")
    ui.process_async("page_numbers", ui.files, {
        "position": position,
        "start": start,
        "format": fmt,
    })
