"""
RenameTool: Plugin para renombrar archivos en masa.
"""
from core.base_tool import BaseTool
from tools.rename_tool.ui import RenameToolUI


class RenameTool(BaseTool):
    """Herramienta para renombrar archivos."""
    
    def __init__(self):
        self.ui = None
    
    def get_name(self) -> str:
        return "Renombrar"
    
    def get_icon(self) -> str:
        return "✏️"
    
    def get_description(self) -> str:
        return "Renombrar archivos en masa"
    
    def build_ui(self, parent_frame) -> None:
        self.ui = RenameToolUI(parent_frame, self._on_process)
        self.ui.pack(fill="both", expand=True)
    
    def _on_process(self, action: str, files: list, options: dict) -> dict:
        return {'success': True, 'message': 'UI handles directly'}
    
    def process(self, files: list, options: dict) -> dict:
        return {'success': True, 'message': 'UI handles directly'}