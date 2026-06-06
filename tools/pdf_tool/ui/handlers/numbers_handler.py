"""Page numbers handler. R0: <80 lines."""
from __future__ import annotations
from typing import TYPE_CHECKING

from core.constants import COLORS

if TYPE_CHECKING:
    from tools.pdf_tool.ui.state import PDFState


def add_page_numbers(state: "PDFState") -> None:
    """Add page numbers to PDF."""
    if not state.ctx.files:
        if state.ctx.status_label is not None:
            state.ctx.status_label.configure(
                text="Seleccione un PDF primero",
                text_color=COLORS.get("warning", "orange"),
            )
        return
    num_position = state.num_position
    position = num_position.get() if num_position is not None else "footer"
    num_start = state.num_start
    start = int(num_start.get() or 1) if num_start is not None else 1
    num_format = state.num_format
    fmt = num_format.get() if num_format is not None else "Pagina {n} de {total}"
    if state.ctx.status_label is not None:
        state.ctx.status_label.configure(text="Procesando...", text_color="blue")
    if state.ctx.process_async is not None:
        state.ctx.process_async("page_numbers", state.ctx.files, {
            "position": position,
            "start": start,
            "format": fmt,
        })
