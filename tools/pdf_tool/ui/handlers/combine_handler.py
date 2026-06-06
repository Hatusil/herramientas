"""Combine handler. R0: <80 lines."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.pdf_tool.ui.state import PDFState, PDFContext


def merge_pdfs(state: PDFState, ctx: PDFContext) -> None:
    """Merge multiple PDFs into one (widget-less)."""
    files = ctx.files
    if not files or len(files) < 2:
        ctx.status_label and ctx.status_label.configure(
            text="Seleccione al menos 2 PDFs", text_color="orange",
        )
        return
    if ctx.process_async is not None:
        ctx.process_async("merge", files, {})


def extract_pages(state: PDFState) -> None:
    """Extract specific pages from PDF."""
    files = state.ctx.files
    if not files:
        state.ctx.status_label and state.ctx.status_label.configure(
            text="Seleccione un PDF primero", text_color="orange",
        )
        return
    entry = state.extract_pages
    pages_str = entry.get().strip() if entry is not None else ""
    if not pages_str:
        state.ctx.status_label and state.ctx.status_label.configure(
            text="Ingrese las paginas a extraer", text_color="orange",
        )
        return
    try:
        if "-" in pages_str:
            parts = pages_str.split("-")
            pages = list(range(int(parts[0]), int(parts[1]) + 1))
        else:
            pages = [int(p.strip()) for p in pages_str.split(",")]
    except ValueError:
        state.ctx.status_label and state.ctx.status_label.configure(
            text="Formato de paginas invalido", text_color="red",
        )
        return
    state.ctx.status_label and state.ctx.status_label.configure(
        text="Procesando...", text_color="blue",
    )
    if state.ctx.process_async is not None:
        state.ctx.process_async("extract", files, {"pages": pages})


def extract_range(state: PDFState) -> None:
    """Extract a range of pages from PDF."""
    files = state.ctx.files
    if not files:
        state.ctx.status_label and state.ctx.status_label.configure(
            text="Seleccione un PDF primero", text_color="orange",
        )
        return
    start_entry = state.extract_start
    end_entry = state.extract_end
    try:
        start = int(start_entry.get()) if start_entry is not None else 1
        end = int(end_entry.get()) if end_entry is not None else 1
    except ValueError:
        state.ctx.status_label and state.ctx.status_label.configure(
            text="Numeros de pagina invalidos", text_color="red",
        )
        return
    if start < 1 or end < 1:
        state.ctx.status_label and state.ctx.status_label.configure(
            text="Los numeros deben ser >= 1", text_color="red",
        )
        return
    if start > end:
        state.ctx.status_label and state.ctx.status_label.configure(
            text="Inicio debe ser menor que fin", text_color="red",
        )
        return
    state.ctx.status_label and state.ctx.status_label.configure(
        text="Procesando...", text_color="blue",
    )
    if state.ctx.process_async is not None:
        state.ctx.process_async("extract_range", files, {"start": start, "end": end})
