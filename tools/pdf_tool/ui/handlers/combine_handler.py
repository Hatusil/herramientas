"""Combine handler. R0: <80 lines."""
from __future__ import annotations
from typing import TYPE_CHECKING

from core.constants import COLORS

if TYPE_CHECKING:
    from tools.pdf_tool.ui.main_ui import PDFToolUI


def merge_pdfs(ui: PDFToolUI) -> None:
    """Merge multiple PDFs into one."""
    if not ui.files or len(ui.files) < 2:
        ui.status_label.configure(
            text="Seleccione al menos 2 PDFs", text_color=COLORS.get("warning", "orange")
        )
        return
    ui.process_async("merge", ui.files, {})


def extract_pages(ui: PDFToolUI) -> None:
    """Extract specific pages from PDF."""
    if not ui.files:
        ui.status_label.configure(text="Seleccione un PDF primero", text_color=COLORS.get("warning", "orange"))
        return
    extract_entry = getattr(ui, "extract_pages", None)
    pages_str = extract_entry.get().strip() if extract_entry else ""
    if not pages_str:
        ui.status_label.configure(
            text="Ingrese las paginas a extraer", text_color=COLORS.get("warning", "orange")
        )
        return
    try:
        if "-" in pages_str:
            parts = pages_str.split("-")
            pages = list(range(int(parts[0]), int(parts[1]) + 1))
        else:
            pages = [int(p.strip()) for p in pages_str.split(",")]
    except ValueError:
        ui.status_label.configure(text="Formato de paginas invalido", text_color="red")
        return
    ui.process_async("extract", ui.files, {"pages": pages})


def extract_range(ui: PDFToolUI) -> None:
    """Extract a range of pages from PDF."""
    if not ui.files:
        ui.status_label.configure(text="Seleccione un PDF primero", text_color=COLORS.get("warning", "orange"))
        return
    extract_start = getattr(ui, "extract_start", None)
    extract_end = getattr(ui, "extract_end", None)
    try:
        start = int(extract_start.get()) if extract_start else 1
        end = int(extract_end.get()) if extract_end else 1
    except ValueError:
        ui.status_label.configure(text="Numeros de pagina invalidos", text_color="red")
        return
    if start < 1 or end < 1:
        ui.status_label.configure(text="Los numeros deben ser >= 1", text_color="red")
        return
    if start > end:
        ui.status_label.configure(text="Inicio debe ser menor que fin", text_color="red")
        return
    ui.status_label.configure(text="Procesando...", text_color="blue")
    ui.process_async("extract_range", ui.files, {"start": start, "end": end})
