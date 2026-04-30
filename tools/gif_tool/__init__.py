"""
GifTool: Plugin para crear GIFs animados.
"""
from core.base_tool import BaseTool
from tools.gif_tool.ui import GifToolUI


class GifTool(BaseTool):
    """Herramienta para crear GIFs animados."""
    
    def __init__(self):
        self.ui = None
    
    def get_name(self) -> str:
        return "GIF"
    
    def get_icon(self) -> str:
        return "🎞️"
    
    def get_description(self) -> str:
        return "Crear GIFs animados desde imágenes"
    
    def build_ui(self, parent_frame) -> None:
        self.ui = GifToolUI(parent_frame, self._on_process)
        self.ui.pack(fill="both", expand=True)
    
    def _on_process(self, action: str, files: list, options: dict) -> dict:
        return {'success': True, 'message': 'UI handles directly'}
    
    def process(self, files: list, options: dict) -> dict:
        return {'success': True, 'message': 'UI handles directly'}