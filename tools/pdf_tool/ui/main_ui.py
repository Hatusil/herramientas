"""
PDFToolUI Main - Esqueleto principal de la UI de PDF.

La clase PDFToolUI orchestrates los tabs especializados.
Los métodos _setup_*_tab() están en módulos separados para SRP.
"""

import os
import logging
from typing import List, Callable, Dict, Any, Optional

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from PIL import Image

# Import BaseToolUI from core
from core.base_tool_ui import BaseToolUI
from core.help_panel import add_help

logger = logging.getLogger(__name__)


def get_pdf_thumbnail(file_path: str, size: tuple = (200, 250)) -> Optional[Image.Image]:
    """Genera un thumbnail de la primera página de un PDF usando Fitz."""
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
        logger.warning(f"Error generando thumbnail: {e}")
        return None


class PDFToolUI(BaseToolUI):
    """UI para procesamiento de archivos PDF."""

    def __init__(self, master, on_process: Callable, **kwargs):
        super().__init__(master, on_process, **kwargs)

        # Estado: evitar doble click
        self.is_processing = False

        # Setup progress bar
        self._setup_progress_bar()

        # Build tool-specific tabs after base selector
        self._build_tabs()

    def _build_tabs(self) -> None:
        """Build tool-specific tabs."""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Agregar tabs
        self.tab_info = self.tabview.add("Info")
        self.tab_edit = self.tabview.add("Editar")
        self.tab_transform = self.tabview.add("Transformar")
        self.tab_watermark = self.tabview.add("Watermark")
        self.tab_security = self.tabview.add("Seguridad")
        self.tab_combine = self.tabview.add("Combinar")
        self.tab_numbers = self.tabview.add("Números")
        self.tab_optimize = self.tabview.add("Optimizar")
        self.tab_pipeline = self.tabview.add("Pipeline")

        # Importar y ejecutar setup de cada tab
        from tools.pdf_tool.ui import watermark_tab, edit_tab, transform_tab
        from tools.pdf_tool.ui import combine_tab, numbers_tab, security_tab
        from tools.pdf_tool.ui import optimize_tab, pipeline_tab, info_tab

        self._setup_info_tab = info_tab.setup_info_tab
        self._setup_edit_tab = edit_tab.setup_edit_tab
        self._setup_transform_tab = transform_tab.setup_transform_tab
        self._setup_watermark_tab = watermark_tab.setup_watermark_tab
        self._setup_security_tab = security_tab.setup_security_tab
        self._setup_combine_tab = combine_tab.setup_combine_tab
        self._setup_numbers_tab = numbers_tab.setup_numbers_tab
        self._setup_optimize_tab = optimize_tab.setup_optimize_tab
        self._setup_pipeline_tab = pipeline_tab.setup_pipeline_tab

        # Configurar cada tab
        self._setup_info_tab(self)
        self._setup_edit_tab(self)
        self._setup_transform_tab(self)
        self._setup_watermark_tab(self)
        self._setup_security_tab(self)
        self._setup_combine_tab(self)
        self._setup_numbers_tab(self)
        self._setup_optimize_tab(self)
        self._setup_pipeline_tab(self)

    def _get_file_label(self) -> str:
        return "Archivos PDF:"

    def _get_file_dialog_filters(self) -> List[tuple]:
        return [
            ("PDF files", "*.pdf"),
            ("All files", "*.*")
        ]

    def _setup_ui(self) -> None:
        """Configura los widgets de la UI."""
        # Título
        title = ctk.CTkLabel(
            self,
            text="Procesamiento de PDF",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(0, 10))

        # Panel de ayuda
        help_panel = add_help(
            self,
            title="Ayuda - Procesamiento de PDF",
            description="📄 Procesa PDFs: watermark, anotar, rotar, combinar, extraer páginas, números, encriptar, comprimir",
            usage=[
                "1. 📥 Agregar PDFs con 'Agregar PDFs...'",
                "2. 📑 Elegir operación (Watermark/Editar/Transformar/etc)",
                "3. ⚙️ Configurar opciones",
                "4. ▶️ Click en ejecutar",
            ],
            tips=[
                "💡 Pipeline permite encadenar operaciones múltiples",
                "💡 Usá 'Info' para ver propiedades antes de modificar",
                "💡 Combinar crea un nuevo PDF, no modifica los originales",
            ],
            warnings=[
                "⚠️ PDFs encriptados requieren contraseña primero",
                "⚠️ Combinar/extraer son destructivos - crea nuevo archivo",
                "⚠️ Watermark modifica el original",
            ],
        )
        help_panel.pack(fill="x", padx=10, pady=5)

        # File selector (from BaseToolUI)
        self._setup_file_selector()

    def _show_result(self, result: Dict[str, Any]) -> None:
        """Muestra el resultado del procesamiento."""
        if result.get('success'):
            self.status_label.configure(
                text=result.get('message', 'Completado'),
                text_color="green"
            )
        else:
            self.status_label.configure(
                text=result.get('message', 'Error'),
                text_color="red"
            )


# Importar handlers de cada tab para mantener backwards compatibility
# Los métodos _apply_text_watermark, _remove_watermark, etc. están en los módulos de tabs
from tools.pdf_tool.ui import watermark_tab, edit_tab, transform_tab
from tools.pdf_tool.ui import combine_tab, numbers_tab, security_tab
from tools.pdf_tool.ui import optimize_tab, pipeline_tab, info_tab

# Asignar métodos al 클래се
PDFToolUI._apply_text_watermark = watermark_tab.apply_text_watermark
PDFToolUI._remove_watermark = watermark_tab.remove_watermark
PDFToolUI._on_opacity_slider_change = watermark_tab.on_opacity_slider_change
PDFToolUI._on_rotation_slider_change = watermark_tab.on_rotation_slider_change
PDFToolUI._update_watermark_inputs = watermark_tab.update_watermark_inputs
PDFToolUI._select_watermark_image = watermark_tab.select_watermark_image

PDFToolUI._add_annotation = edit_tab.add_annotation
PDFToolUI._redact_area = edit_tab.redact_area
PDFToolUI._extract_range = edit_tab.extract_range

PDFToolUI._rotate_pages = transform_tab.rotate_pages
PDFToolUI._reorder_pages = transform_tab.reorder_pages

PDFToolUI._merge_pdfs = combine_tab.merge_pdfs
PDFToolUI._extract_pages = combine_tab.extract_pages

PDFToolUI._add_page_numbers = numbers_tab.add_page_numbers

PDFToolUI._encrypt_pdf = security_tab.encrypt_pdf
PDFToolUI._decrypt_pdf = security_tab.decrypt_pdf

PDFToolUI._compress_pdf = optimize_tab.compress_pdf
PDFToolUI._clean_metadata = optimize_tab.clean_metadata

PDFToolUI._update_pipeline_inputs = pipeline_tab.update_pipeline_inputs
PDFToolUI._add_to_pipeline = pipeline_tab.add_to_pipeline
PDFToolUI._refresh_pipeline_list = pipeline_tab.refresh_pipeline_list
PDFToolUI._clear_pipeline = pipeline_tab.clear_pipeline
PDFToolUI._execute_pipeline = pipeline_tab.execute_pipeline

PDFToolUI._show_pdf_info = info_tab.show_pdf_info