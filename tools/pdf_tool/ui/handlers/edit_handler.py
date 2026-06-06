"""Edit handler. R0: <80 lines."""
from __future__ import annotations
from typing import TYPE_CHECKING

from core.constants import COLORS

if TYPE_CHECKING:
    from tools.pdf_tool.ui.main_ui import PDFToolUI


def add_annotation(ui: PDFToolUI) -> None:
    """Add text annotation to PDF."""
    if not ui._check_files():
        return
    annot_text = getattr(ui, "annot_text", None)
    text = annot_text.get() if annot_text and hasattr(annot_text, "get") else ""
    annot_page = getattr(ui, "annot_page", None)
    page = int(annot_page.get() or 0) if annot_page else 0
    annot_x = getattr(ui, "annot_x", None)
    x = float(annot_x.get() or 100) if annot_x else 100
    annot_y = getattr(ui, "annot_y", None)
    y = float(annot_y.get() or 100) if annot_y else 100
    ui.status_label.configure(text="Procesando...", text_color="blue")
    ui.process_async("add_annotation", ui.files, {
        "text": text,
        "page": page,
        "x": x,
        "y": y,
    })


def redact_area(ui: PDFToolUI) -> None:
    """Redact area in PDF."""
    if not ui._check_files():
        return
    redact_page = getattr(ui, "redact_page", None)
    page = int(redact_page.get() or 0) if redact_page else 0
    redact_x = getattr(ui, "redact_x", None)
    x = float(redact_x.get() or 100) if redact_x else 100
    redact_y = getattr(ui, "redact_y", None)
    y = float(redact_y.get() or 100) if redact_y else 100
    redact_w = getattr(ui, "redact_w", None)
    w = float(redact_w.get() or 100) if redact_w else 100
    redact_h = getattr(ui, "redact_h", None)
    h = float(redact_h.get() or 30) if redact_h else 30
    ui.status_label.configure(text="Procesando...", text_color="blue")
    ui.process_async("redact", ui.files, {
        "page": page,
        "x": x,
        "y": y,
        "width": w,
        "height": h,
    })
