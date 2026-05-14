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
    
    def _on_process(self, action: str, files: list, options: dict) -> dict:
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
            
            elif action == 'edit_metadata':
                return processor.edit_audio_metadata(
                    files,
                    title=options.get('title'),
                    artist=options.get('artist'),
                    album=options.get('album'),
                    genre=options.get('genre'),
                    year=options.get('year'),
                    track=options.get('track'),
                    comment=options.get('comment'),
                    composer=options.get('composer')
                )
            
            elif action == 'transcribe':
                return processor.transcribe_audio(
                    files[0] if files else "",
                    model_size=options.get('model', 'base'),
                    output_format=options.get('format', 'txt')
                )
            
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
    
    def process(self, files: list, options: dict) -> dict:
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

    # =============================================================================
    # ASYNC PROCESSING - No bloquea UI
    # =============================================================================
    def process_async(self, files: list, options: dict, callback) -> None:
        """
        Procesa archivos en background con callback.
        
        Args:
            files: Lista de rutas de archivos
            options: Opciones de procesamiento
            callback: Función(result) a llamar al terminar
        """
        action = options.get('action', 'normalize')
        print(f"DEBUG process_async: action={action}, files={files}")

        # Usar función async del processor si existe
        try:
            print(f"DEBUG: callback={callback}, action={action}")
            if action == 'normalize':
                from tools.audio_tool.processor import normalize_audio_async
                print("DEBUG: importing normalize_audio_async OK")
                normalize_audio_async(files, callback=callback, **options)
                print("DEBUG: normalize_audio_async called")
            elif action == 'clean':
                from tools.audio_tool.processor import clean_audio_metadata_async
                clean_audio_metadata_async(files, callback=callback)
            elif action == 'convert':
                from tools.audio_tool.processor import convert_audio_async
                print("DEBUG: importing convert_audio_async OK")
                convert_audio_async(
                    files,
                    output_format=options.get('format', 'mp3'),
                    callback=callback,
                    quality=options.get('quality', 192)
                )
                print("DEBUG: convert_audio_async called")
            elif action == 'repair':
                from tools.audio_tool.processor import repair_audio_async
                print("DEBUG: importing repair_audio_async OK")
                repair_audio_async(files, callback=callback)
                print("DEBUG: repair_audio_async called")
            elif action == 'edit_metadata':
                from tools.audio_tool.processor import edit_audio_metadata_async
                edit_audio_metadata_async(files, callback=callback, **options)
            elif action == 'transcribe':
                from tools.audio_tool.processors.transcribe import transcribe_audio_async
                transcribe_audio_async(
                    files,
                    callback=callback,
                    model=options.get('model', 'base'),
                    format=options.get('format', 'txt')
                )
            else:
                # Fallback a sync
                result = self._on_process(action, files, options)
                callback(result)
        except Exception as e:
            logger.error(f"Error en process_async: {e}")
            callback({'success': False, 'error': str(e)})