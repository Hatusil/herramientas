"""
DuplicateTool: Plugin para encontrar archivos duplicados.
"""
from core.base_tool import BaseTool
from tools.duplicate_tool.ui import DuplicateToolUI


class DuplicateTool(BaseTool):
    """Herramienta para encontrar duplicados."""
    
    def __init__(self):
        self.ui = None
    
    def get_name(self) -> str:
        return "Duplicados"
    
    def get_icon(self) -> str:
        return "📋"
    
    def get_description(self) -> str:
        return "Encontrar archivos duplicados por contenido"
    
    def build_ui(self, parent_frame) -> None:
        self.ui = DuplicateToolUI(parent_frame, self._on_process)
        self.ui.pack(fill="both", expand=True)
        # Asegurar altura mínima
        self.ui.configure(height=600)
    
    def _on_process(self, action: str, files: list, options: dict) -> dict:
        return {'success': True, 'message': 'UI handles directly'}
    
    def process(self, files: list, options: dict) -> dict:
        return {'success': True, 'message': 'UI handles directly'}