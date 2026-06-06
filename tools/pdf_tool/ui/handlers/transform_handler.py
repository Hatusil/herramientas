"""Transform handler. R0: <80 lines."""
from __future__ import annotations
from typing import TYPE_CHECKING

from core.constants import COLORS

if TYPE_CHECKING:
    from tools.pdf_tool.ui.state import PDFState


def rotate_pages(state: "PDFState") -> None:
    """Rotate PDF pages."""
    if not state.ctx.files:
        if state.ctx.status_label is not None:
            state.ctx.status_label.configure(
                text="Seleccione un PDF primero",
                text_color=COLORS.get("warning", "orange"),
            )
        return
    rotate_var = state.rotate_var
    degrees = int(rotate_var.get()) if rotate_var is not None else 90
    rotate_entry = state.rotate_pages
    pages = None
    if rotate_entry is not None and rotate_entry.get().strip():
        pages = [int(p) for p in rotate_entry.get().split(",")]
    if state.ctx.status_label is not None:
        state.ctx.status_label.configure(text="Procesando...", text_color="blue")
    if state.ctx.process_async is not None:
        state.ctx.process_async("rotate", state.ctx.files, {"degrees": degrees, "pages": pages})


def reorder_pages(state: "PDFState") -> None:
    """Reorder PDF pages."""
    if not state.ctx.files:
        if state.ctx.status_label is not None:
            state.ctx.status_label.configure(
                text="Seleccione un PDF primero",
                text_color=COLORS.get("warning", "orange"),
            )
        return
    reorder_input = state.reorder_input
    order_str = reorder_input.get().strip() if reorder_input is not None else ""
    if not order_str:
        if state.ctx.status_label is not None:
            state.ctx.status_label.configure(
                text="Ingrese el orden de paginas",
                text_color=COLORS.get("warning", "orange"),
            )
        return
    try:
        new_order = [int(p) for p in order_str.split(",")]
    except ValueError:
        if state.ctx.status_label is not None:
            state.ctx.status_label.configure(
                text="Orden invalido", text_color="red",
            )
        return
    if state.ctx.status_label is not None:
        state.ctx.status_label.configure(text="Procesando...", text_color="blue")
    if state.ctx.process_async is not None:
        state.ctx.process_async("reorder", state.ctx.files, {"new_order": new_order})
