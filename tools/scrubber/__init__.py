"""
ScrubberTool: Plugin para limpiar metadatos de archivos.
"""
import logging
from typing import List, Dict, Any

from core.base_tool import BaseTool
from tools.scrubber import processor
from tools.scrubber.ui import ScrubberToolUI


logger = logging.getLogger(__name__)


class ScrubberTool(BaseTool):
    """Herramienta para limpiar metadatos de archivos."""
    
    def __init__(self):
        self.ui = None
    
    def get_name(self) -> str:
        return "Scrubber"
    
    def get_icon(self) -> str:
        return "🧹"
    
    def get_description(self) -> str:
        return "Limpiar metadatos de imágenes y documentos"
    
    def build_ui(self, parent_frame) -> None:
        """Construye la UI de la herramienta."""
        self.ui = ScrubberToolUI(parent_frame, self._on_process)
        self.ui.pack(fill="both", expand=True)
    
    def _on_process(self, action: str, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maneja el procesamiento de archivos.
        """
        try:
            if action == 'clean_image':
                return processor.clean_image_metadata(file_path, options)
            
            elif action == 'clean_docx':
                return processor.clean_docx(file_path)
            
            elif action == 'clean_xlsx':
                return processor.clean_xlsx(file_path)
            
            elif action == 'clean_pdf':
                # Usar el processor de PDF tool
                from tools.pdf_tool.processor import clean_metadata
                return clean_metadata([file_path])
            
            else:
                return {
                    'success': False,
                    'message': f'Acción desconocida: {action}',
                    'output_files': [],
                    'error': 'Unknown action'
                }
        
        except Exception as e:
            logger.error(f"Error en scrubber: {e}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'output_files': [],
                'error': str(e)
            }
    
    def process(self, files: List[str], options: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa archivos."""
        action = options.get('action', 'clean_image')
        return self._on_process(action, files[0] if files else '', options)