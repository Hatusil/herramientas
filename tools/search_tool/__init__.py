"""
SearchTool: Plugin para búsqueda avanzada de archivos.
"""
from core.base_tool import BaseTool
from tools.search_tool.ui import SearchToolUI


class SearchTool(BaseTool):
    """Herramienta de búsqueda avanzada."""
    
    def __init__(self):
        self.ui = None
    
    def get_name(self) -> str:
        return "Search"
    
    def get_icon(self) -> str:
        return "🔍"
    
    def get_description(self) -> str:
        return "Búsqueda avanzada por nombre, fecha y contenido"
    
    def build_ui(self, parent_frame) -> None:
        self.ui = SearchToolUI(parent_frame, self._on_process)
        self.ui.pack(fill="both", expand=True)
    
    def _on_process(self, action: str, files: list, options: dict) -> dict:
        return self.process(files, options)
    
    def process(self, files: list, options: dict) -> dict:
        """Ejecuta la búsqueda."""
        if not files and 'folder' in options:
            from tools.search_tool.processor import search_all
            return search_all(options['folder'], options)
        return {'success': False, 'error': 'No hay carpeta seleccionada'}