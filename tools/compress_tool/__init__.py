"""
CompressTool: Plugin para comprimir y descomprimir archivos.
"""
from core.base_tool import BaseTool


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
        from tools.compress_tool.ui import CompressToolUI
        self.ui = CompressToolUI(parent_frame, self._on_process)
        self.ui.pack(fill="both", expand=True)
    
    def _on_process(self, action: str, files: list, options: dict) -> dict:
        return self.process(files, {**options, 'action': action})
    
    def process(self, files: list, options: dict) -> dict:
        from tools.compress_tool import processor
        action = options.get('action', 'zip')
        
        if action == 'zip':
            return processor.compress_to_zip(
                files, options.get('output'), options.get('level', 6))
        elif action == 'tar':
            return processor.compress_to_tar(
                files, options.get('output'), options.get('compression', 'gz'))
        elif action == 'unzip':
            if not files:
                return {'success': False, 'error': 'No hay archivo ZIP'}
            return processor.decompress_zip(files[0], options.get('output_dir'))
        elif action == 'untar':
            if not files:
                return {'success': False, 'error': 'No hay archivo TAR'}
            return processor.decompress_tar(files[0], options.get('output_dir'))
        elif action == 'list':
            if not files:
                return {'success': False, 'error': 'No hay archivo ZIP'}
            return processor.list_zip_contents(files[0])
        else:
            return {'success': False, 'error': f'Unknown action: {action}'}