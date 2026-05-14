"""
GifTool: Plugin para crear GIFs animados.
"""
from core.base_tool import BaseTool


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
        from tools.gif_tool.ui import GifToolUI
        self.ui = GifToolUI(parent_frame, self._on_process)
        self.ui.pack(fill="both", expand=True)
    
    def _on_process(self, action: str, files: list, options: dict) -> dict:
        return self.process(files, options)
    
    def process(self, files: list, options: dict) -> dict:
        from tools.gif_tool import processor
        action = options.get('action', 'create')
        
        if action == 'create':
            return processor.create_gif(
                files, options.get('output'), options.get('duration', 500), options.get('loop', 0))
        elif action == 'extract':
            if not files:
                return {'success': False, 'error': 'No hay archivo GIF'}
            return processor.extract_frames(files[0], options.get('output_dir'))
        elif action == 'info':
            if not files:
                return {'success': False, 'error': 'No hay archivo GIF'}
            return processor.get_gif_info(files[0])
        else:
            return {'success': False, 'error': f'Unknown action: {action}'}