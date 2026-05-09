"""
ImageTool: Plugin para procesamiento digital de imágenes (PDI).
"""
import logging

from core.base_tool import BaseTool

logger = logging.getLogger(__name__)


class ImageTool(BaseTool):
    """Herramienta de procesamiento digital de imágenes."""

    def __init__(self):
        self.ui = None

    def get_name(self) -> str:
        return "Imagen"

    def get_icon(self) -> str:
        return "🖼️"

    def get_description(self) -> str:
        return "Procesamiento Digital de Imágenes — 7 fases"

    def build_ui(self, parent_frame):
        # UI se implementa en PR #2
        pass

    def process(self, files: list, options: dict) -> dict:
        """Procesa imágenes según la operación seleccionada."""
        return {
            'success': True,
            'output_files': [],
            'message': 'ImageTool foundation ready',
            'error': None
        }