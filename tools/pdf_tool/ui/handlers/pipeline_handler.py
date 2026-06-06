"""Pipeline handler. R0: <80 lines."""
from __future__ import annotations
import os
from typing import TYPE_CHECKING, Any, Dict

from core.constants import COLORS

if TYPE_CHECKING:
    from tools.pdf_tool.ui.main_ui import PDFToolUI


def execute_pipeline(ui: PDFToolUI) -> Dict[str, Any]:
    """Execute all pipeline operations. Returns result dict so the tab can refresh UI."""
    if not ui.files:
        ui.status_label.configure(text="Seleccione un PDF primero", text_color=COLORS.get("warning", "orange"))
        return {"success": False, "error": "No hay archivos"}
    pipeline_ops = getattr(ui, "pipeline_operations", [])
    if not pipeline_ops:
        ui.status_label.configure(
            text="No hay operaciones en el pipeline", text_color=COLORS.get("warning", "orange")
        )
        return {"success": False, "error": "No hay operaciones"}
    ui.status_label.configure(text="Ejecutando pipeline...", text_color="blue")
    from tools.pdf_tool.modules.pipeline import execute_pipeline_operations

    result = execute_pipeline_operations(ui.files[0], pipeline_ops)
    if result.get("success"):
        output_file = result.get("output_file")
        ui.status_label.configure(
            text=f"Pipeline completado: {result.get('message', '')}",
            text_color="green",
        )
        pipeline_ops.clear()
        if output_file and os.path.exists(output_file):
            ui.files = [output_file]
            ui._update_file_list()
    else:
        ui.status_label.configure(
            text=f"Error: {result.get('error', 'Error desconocido')}",
            text_color="red",
        )
    return result
