"""Optimize handler. R0: <80 lines."""
from __future__ import annotations
from typing import TYPE_CHECKING

from core.constants import COLORS

if TYPE_CHECKING:
    from tools.pdf_tool.ui.state import PDFState, PDFContext


def compress_pdf(state: "PDFState") -> None:
    """Compress PDF."""
    if not state.ctx.files:
        if state.ctx.status_label is not None:
            state.ctx.status_label.configure(
                text="Seleccione un PDF primero",
                text_color=COLORS.get("warning", "orange"),
            )
        return
    compress_level = state.compress_level
    level = compress_level.get() if compress_level is not None else "medium"
    if state.ctx.status_label is not None:
        state.ctx.status_label.configure(text="Procesando...", text_color="blue")
    if state.ctx.process_async is not None:
        state.ctx.process_async("compress", state.ctx.files, {"level": level})


def clean_metadata(state: "PDFState", ctx: "PDFContext") -> None:
    """Clean PDF metadata (widget-less)."""
    if not ctx.files:
        if ctx.status_label is not None:
            ctx.status_label.configure(
                text="Seleccione un PDF primero",
                text_color=COLORS.get("warning", "orange"),
            )
        return
    if ctx.status_label is not None:
        ctx.status_label.configure(text="Procesando...", text_color="blue")
    if ctx.process_async is not None:
        ctx.process_async("clean_metadata", ctx.files, {})
