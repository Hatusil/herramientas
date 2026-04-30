"""
CompressTool: Plugin para comprimir y descomprimir archivos.
"""
from core.base_tool import BaseTool
from tools.compress_tool.ui import CompressToolUI


class CompressTool(BaseTool):
    """Herramienta para comprimir archivos."""
    
    def __init__(self):
        self.ui = None
    
    def get_name(self) -> str:
        return "Comprimir"
    
    def get_icon(self) -> str:
        return "📦"
    
    def get_description(self) -> str:
        return "Comprimir y extraer archivos ZIP, TAR"
    
    def build_ui(self, parent_frame) -> None:
        self.ui = CompressToolUI(parent_frame, self._on_process)
        self.ui.pack(fill="both", expand=True)
    
    def _on_process(self, action: str, files: list, options: dict) -> dict:
        return {'success': True, 'message': 'UI handles directly'}
    
    def process(self, files: list, options: dict) -> dict:
        return {'success': True, 'message': 'UI handles directly'}