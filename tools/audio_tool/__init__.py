"""
AudioTool: Plugin para procesamiento de archivos de audio.
"""
import logging
from typing import List, Dict, Any

from core.base_tool import BaseTool
from core import constants
from tools.audio_tool import processor
from tools.audio_tool.ui import AudioToolUI


logger = logging.getLogger(__name__)


class AudioTool(BaseTool):
    """Herramienta para procesar archivos de audio."""
    
    def __init__(self):
        self.ui = None
    
    def get_name(self) -> str:
        return "Audio"
    
    def get_icon(self) -> str:
        return "🎵"
    
    def get_description(self) -> str:
        return "Normalizar, convertir, limpiar y reparar audio"
    
    def build_ui(self, parent_frame) -> None:
        """Construye la UI de la herramienta."""
        self.ui = AudioToolUI(parent_frame, self._on_process)
        self.ui.pack(fill="both", expand=True)
    
    def _on_process(self, action: str, files: List[str], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maneja el procesamiento de archivos.
        
        Args:
            action: Acción a realizar
            files: Lista de archivos a procesar
            options: Opciones adicionales
            
        Returns:
            dict: Resultado del procesamiento
        """
        logger.debug(f"_on_process: action={action}, files={len(files)}")
        
        try:
            if action == 'normalize':
                logger.debug(f"Calling normalize_audio with {len(files)} files")
                result = processor.normalize_audio(
                    files,
                    target_lufs=options.get('target_lufs', constants.DEFAULT_LUFS),
                    limit_clipping=options.get('limit_clipping', True),
                    sample_rate=options.get('sample_rate'),
                    quality=options.get('quality', 192)
                )
                logger.debug(f"normalize result: success={result.get('success', False)}")
                return result
            
            elif action == 'clean':
                return processor.clean_audio_metadata(files)
            
            elif action == 'convert':
                return processor.convert_audio(
                    files,
                    output_format=options.get('format', 'mp3'),
                    quality=options.get('quality', 192)
                )
            
            elif action == 'repair':
                logger.debug(f"Calling repair_audio with {len(files)} files")
                result = processor.repair_audio(files)
                logger.debug(f"repair result: success={result.get('success', False)}")
                return result
            
            else:
                return {
                    'success': False,
                    'message': f'Acción desconocida: {action}',
                    'output_files': [],
                    'error': 'Unknown action'
                }
        
        except Exception as e:
            logger.error(f"Error procesando audio: {e}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'output_files': [],
                'error': str(e)
            }
    
    def process(self, files: List[str], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa los archivos.
        
        Args:
            files: Lista de rutas de archivos
            options: Opciones de procesamiento
            
        Returns:
            dict: Resultado con success, message, output_files, error
        """
        action = options.get('action', 'normalize')
        return self._on_process(action, files, options)