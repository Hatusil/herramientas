"""Pipeline handler. R0: <80 lines."""
from __future__ import annotations
import os
from typing import TYPE_CHECKING, Any, Dict

from core.constants import COLORS

if TYPE_CHECKING:
    from tools.pdf_tool.ui.state import PDFState


def execute_pipeline(state: "PDFState") -> Dict[str, Any]:
    """Execute all pipeline operations. Returns result dict so the tab can refresh UI."""
    if not state.ctx.files:
        if state.ctx.status_label is not None:
            state.ctx.status_label.configure(
                text="Seleccione un PDF primero",
                text_color=COLORS.get("warning", "orange"),
            )
        return {"success": False, "error": "No hay archivos"}
    pipeline_ops = state.pipeline_operations
    if not pipeline_ops:
        if state.ctx.status_label is not None:
            state.ctx.status_label.configure(
                text="No hay operaciones en el pipeline",
                text_color=COLORS.get("warning", "orange"),
            )
        return {"success": False, "error": "No hay operaciones"}
    if state.ctx.status_label is not None:
        state.ctx.status_label.configure(text="Ejecutando pipeline...", text_color="blue")
    from tools.pdf_tool.modules.pipeline import execute_pipeline_operations

    result = execute_pipeline_operations(state.ctx.files[0], pipeline_ops)
    if result.get("success"):
        output_file = result.get("output_file")
        if state.ctx.status_label is not None:
            state.ctx.status_label.configure(
                text=f"Pipeline completado: {result.get('message', '')}",
                text_color="green",
            )
        pipeline_ops.clear()
        if output_file and os.path.exists(output_file):
            state.ctx.files = [output_file]
    else:
        if state.ctx.status_label is not None:
            state.ctx.status_label.configure(
                text=f"Error: {result.get('error', 'Error desconocido')}",
                text_color="red",
            )
    return result
