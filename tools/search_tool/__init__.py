"""
SearchTool: Plugin para búsqueda avanzada de archivos.
"""
from core.base_tool import BaseTool


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
        from tools.search_tool.ui.main_ui import SearchToolUI
        self.ui = SearchToolUI(parent_frame, self._on_process)
        self.ui.pack(fill="both", expand=True)
    
    def _on_process(self, action: str, files: list, options: dict) -> dict:
        return self.process(files, options)
    
    def process(self, files: list, options: dict) -> dict:
        """Ejecuta la búsqueda."""
        from tools.search_tool import processor
        action = options.get('action', 'search')

        if action == 'search':
            folder = options.get('folder', files[0] if files else None)
            if not folder:
                return {'success': False, 'error': 'No hay carpeta seleccionada'}
            return processor.search_all(folder, options)
        elif action == 'find_duplicates':
            folder = options.get('folder', files[0] if files else None)
            if not folder:
                return {'success': False, 'error': 'No hay carpeta seleccionada'}
            return processor.find_duplicates_by_name(folder, options.get('min_size', 0))
        elif action == 'list':
            folder = options.get('folder', files[0] if files else None)
            if not folder:
                return {'success': False, 'error': 'No hay carpeta seleccionada'}
            return processor.list_files(folder, options.get('pattern', '*'))
        else:
            return {'success': False, 'error': f'Unknown action: {action}'}