"""Optimize handler. R0: <80 lines."""
from __future__ import annotations
from typing import TYPE_CHECKING

from core.constants import COLORS

if TYPE_CHECKING:
    from tools.pdf_tool.ui.main_ui import PDFToolUI


def compress_pdf(ui: PDFToolUI) -> None:
    """Compress PDF."""
    if not ui.files:
        ui.status_label.configure(text="Seleccione un PDF primero", text_color=COLORS.get("warning", "orange"))
        return
    compress_level = getattr(ui, "compress_level", None)
    level = compress_level.get() if compress_level else "medium"
    ui.status_label.configure(text="Procesando...", text_color="blue")
    ui.process_async("compress", ui.files, {"level": level})


def clean_metadata(ui: PDFToolUI) -> None:
    """Clean PDF metadata."""
    if not ui.files:
        ui.status_label.configure(text="Seleccione un PDF primero", text_color=COLORS.get("warning", "orange"))
        return
    ui.status_label.configure(text="Procesando...", text_color="blue")
    ui.process_async("clean_metadata", ui.files, {})
