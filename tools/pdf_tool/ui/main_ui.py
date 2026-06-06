"""
PDFToolUI Main - Orchestrator for PDF Tool UI.

Creates state, callbacks, and tab instances. NO handler logic, NO monkey-patch.
"""
from __future__ import annotations

import logging
from typing import Callable, Dict, Any, Optional, List

import customtkinter as ctk
from PIL import Image

from core.base_tool_ui import BaseToolUI
from core.help_panel import add_help
from core.constants import COLORS

from tools.pdf_tool.ui.callbacks import PDFCallbacks
from tools.pdf_tool.ui.tabs.info_tab import InfoTab
from tools.pdf_tool.ui.tabs.edit_tab import EditTab
from tools.pdf_tool.ui.tabs.transform_tab import TransformTab
from tools.pdf_tool.ui.tabs.watermark_tab import WatermarkTab
from tools.pdf_tool.ui.tabs.security_tab import SecurityTab
from tools.pdf_tool.ui.tabs.combine_tab import CombineTab
from tools.pdf_tool.ui.tabs.numbers_tab import NumbersTab
from tools.pdf_tool.ui.tabs.optimize_tab import OptimizeTab
from tools.pdf_tool.ui.tabs.pipeline_tab import PipelineTab

logger = logging.getLogger(__name__)


def get_pdf_thumbnail(file_path: str, size: tuple = (200, 250)) -> Optional[Image.Image]:
    """Generate a thumbnail from the first page of a PDF using Fitz."""
    try:
        import fitz
        doc = fitz.open(file_path)
        if doc.page_count < 1:
            doc.close()
            return None
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
        img = pix.pil_image()
        doc.close()
        img.thumbnail(size, Image.Resampling.LANCZOS)
        return img
    except Exception as e:
        logger.warning(f"Error generating thumbnail: {e}")
        return None


class PDFToolUI(BaseToolUI):
    """Main UI orchestrator for PDF Tool."""

    def __init__(self, master, on_process: Callable, **kwargs):
        self._processing = False
        self.is_processing = False
        super().__init__(master, on_process, **kwargs)

    def _setup_ui(self) -> None:
        """Build the complete UI layout."""
        title = ctk.CTkLabel(
            self,
            text="Procesamiento de PDF",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title.pack(pady=(0, 10))

        add_help(
            self,
            title="Ayuda - Procesamiento de PDF",
            description="Procesa PDFs: watermark, anotar, rotar, combinar, extraer paginas, numeros, encriptar, comprimir",
            usage=[
                "1. Agregar PDFs con 'Agregar PDFs...'",
                "2. Elegir operacion (Watermark/Editar/Transformar/etc)",
                "3. Configurar opciones",
                "4. Click en ejecutar",
            ],
            tips=[
                "Pipeline permite encadenar operaciones multiples",
                "Usa 'Info' para ver propiedades antes de modificar",
                "Combinar crea un nuevo PDF, no modifica los originales",
            ],
            warnings=[
                "PDFs encriptados requieren contrasena primero",
                "Combinar/extraer son destructivos - crea nuevo archivo",
                "Watermark modifica el original",
            ],
        ).pack(fill="x", padx=10, pady=5)

        self._setup_file_selector()

        self.status_label = ctk.CTkLabel(self, text="", text_color="gray")
        self.status_label.pack(pady=5)

        self._setup_progress_bar()

        self.callbacks = PDFCallbacks(
            on_status=self._set_status,
        )

        self._build_tabs()

    def _get_file_label(self) -> str:
        return "Archivos PDF:"

    def _get_file_dialog_filters(self) -> List[tuple]:
        return [
            ("PDF files", "*.pdf"),
            ("All files", "*.*"),
        ]

    def _build_tabs(self) -> None:
        """Create tab view and all tab instances."""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        tab_configs = [
            ("Info", InfoTab),
            ("Editar", EditTab),
            ("Transformar", TransformTab),
            ("Watermark", WatermarkTab),
            ("Seguridad", SecurityTab),
            ("Combinar", CombineTab),
            ("Numeros", NumbersTab),
            ("Optimizar", OptimizeTab),
            ("Pipeline", PipelineTab),
        ]

        self.tabs = {}
        for name, cls in tab_configs:
            frame = self.tabview.add(name)
            tab = cls(frame, self.callbacks, main_ui=self)
            self.tabs[name] = tab

    def _check_files(self) -> bool:
        """Check if files are selected. Returns True if files exist."""
        if not self.files:
            self.status_label.configure(
                text="Seleccione un PDF", text_color=COLORS.get("warning", "orange")
            )
            return False
        return True

    def _set_status(self, message: str, color: str = "blue") -> None:
        """Update status label."""
        resolved = COLORS.get(color, color) if not color.startswith("#") else color
        self.status_label.configure(text=message, text_color=resolved)

    def _show_result(self, result: Dict[str, Any]) -> None:
        """Show processing result."""
        if result.get("success"):
            self.status_label.configure(
                text=result.get("message", "Completado"),
                text_color="green",
            )
        else:
            self.status_label.configure(
                text=result.get("message", "Error"),
                text_color="red",
            )
