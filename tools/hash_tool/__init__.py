"""
HashTool: Plugin para calcular y verificar checksums.
"""
import logging
from typing import List, Dict, Any

from core.base_tool import BaseTool
from core.exceptions import (
    FileNotFoundError,
    UnsupportedFormatError,
    ProcessingError,
    TimeoutError,
    ValidationError,
)
from tools.hash_tool import processor


logger = logging.getLogger(__name__)


class HashTool(BaseTool):
    """Herramienta para calcular y verificar hashes."""
    
    def __init__(self):
        self.ui = None
    
    def get_name(self) -> str:
        return "Hash"
    
    def get_icon(self) -> str:
        return "#️⃣"
    
    def get_description(self) -> str:
        return "Calcular y verificar MD5, SHA1, SHA256"
    
    def build_ui(self, parent_frame) -> None:
        from tools.hash_tool.ui import HashToolUI
        self.ui = HashToolUI(parent_frame, self._on_process)
        self.ui.pack(fill="both", expand=True)
    
    def _on_process(self, action: str, files: list, options: dict) -> dict:
        return self.process(files, options)

    def process(self, files: list, options: dict) -> dict:
        action = options.get('action', 'calculate')
        
        try:
            if action == 'calculate':
                if not files:
                    return {'success': False, 'error': 'No hay archivo'}
                return processor.calculate_hash(
                    files[0], options.get('algorithm', 'sha256'), options.get('timeout', 30))
            elif action == 'all':
                if not files:
                    return {'success': False, 'error': 'No hay archivo'}
                return processor.calculate_all_hashes(files[0])
            elif action == 'verify':
                if not files:
                    return {'success': False, 'error': 'No hay archivo'}
                return processor.verify_hash(
                    files[0], options.get('expected_hash', ''), options.get('algorithm', 'sha256'))
            elif action == 'list':
                return processor.calculate_file_hash_list(files, options.get('algorithm', 'sha256'))
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}
        except FileNotFoundError as e:
            logger.error(f"Archivo no encontrado: {e}")
            return {'success': False, 'error': str(e)}
        except (UnsupportedFormatError, ValidationError) as e:
            logger.error(f"Error de validación: {e}")
            return {'success': False, 'error': str(e)}
        except TimeoutError as e:
            logger.error(f"Timeout: {e}")
            return {'success': False, 'error': str(e)}
        except ProcessingError as e:
            logger.error(f"Error de procesamiento: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return {'success': False, 'error': f'Error inesperado: {e}'}