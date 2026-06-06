"""Edit handler. R0: <80 lines."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.pdf_tool.ui.state import PDFState


def add_annotation(state: "PDFState") -> None:
    """Add text annotation to PDF."""
    if not state.ctx.files:
        if state.ctx.status_label is not None:
            state.ctx.status_label.configure(
                text="Seleccione un PDF primero", text_color="orange",
            )
        return
    annot_text = state.annot_text
    text = annot_text.get() if annot_text is not None else ""
    annot_page = state.annot_page
    page = int(annot_page.get() or 0) if annot_page is not None else 0
    annot_x = state.annot_x
    x = float(annot_x.get() or 100) if annot_x is not None else 100
    annot_y = state.annot_y
    y = float(annot_y.get() or 100) if annot_y is not None else 100
    if state.ctx.status_label is not None:
        state.ctx.status_label.configure(text="Procesando...", text_color="blue")
    if state.ctx.process_async is not None:
        state.ctx.process_async("add_annotation", state.ctx.files, {
            "text": text,
            "page": page,
            "x": x,
            "y": y,
        })


def redact_area(state: "PDFState") -> None:
    """Redact area in PDF."""
    if not state.ctx.files:
        if state.ctx.status_label is not None:
            state.ctx.status_label.configure(
                text="Seleccione un PDF primero", text_color="orange",
            )
        return
    redact_page = state.redact_page
    page = int(redact_page.get() or 0) if redact_page is not None else 0
    redact_x = state.redact_x
    x = float(redact_x.get() or 100) if redact_x is not None else 100
    redact_y = state.redact_y
    y = float(redact_y.get() or 100) if redact_y is not None else 100
    redact_w = state.redact_w
    w = float(redact_w.get() or 100) if redact_w is not None else 100
    redact_h = state.redact_h
    h = float(redact_h.get() or 30) if redact_h is not None else 30
    if state.ctx.status_label is not None:
        state.ctx.status_label.configure(text="Procesando...", text_color="blue")
    if state.ctx.process_async is not None:
        state.ctx.process_async("redact", state.ctx.files, {
            "page": page,
            "x": x,
            "y": y,
            "width": w,
            "height": h,
        })
