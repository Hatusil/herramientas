"""
DuplicateTool: Plugin para encontrar archivos duplicados.
"""
from core.base_tool import BaseTool


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
        from tools.duplicate_tool.ui import DuplicateToolUI
        self.ui = DuplicateToolUI(parent_frame, self._on_process)
        self.ui.pack(fill="both", expand=True)
        self.ui.configure(height=600)
    
    def _on_process(self, action: str, files: list, options: dict) -> dict:
        return self.process(files, options)
    
    def process(self, files: list, options: dict) -> dict:
        import os
        from tools.duplicate_tool import processor
        action = options.get('action', 'hash')
        
        # Use folder_path from options, fallback to files[0] if it's a valid directory
        folder_path = options.get('folder_path')
        if not folder_path and files:
            folder_path = files[0] if os.path.isdir(files[0]) else None
        
        if not folder_path:
            return {'success': False, 'error': 'No folder path provided'}
        
        if action in ('hash', 'async'):
            return processor.find_duplicates_async(folder_path, options.get('extensions'))
        elif action == 'size':
            return processor.find_duplicates_by_size(folder_path)
        else:
            return {'success': False, 'error': f'Unknown action: {action}'}