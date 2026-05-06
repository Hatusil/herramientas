"""
Utilidades comunes del proyecto - Módulo de compatibilidad.
Este módulo re-exporta funciones de los módulos especializados.
Cumple con máxima A1 (una sola responsabilidad por módulo).

Módulos especializados:
- core/file_utils.py: Validación de archivos y paths
- core/text_utils.py: Procesamiento de texto
- core/ffmpeg_utils.py: Utilidades FFmpeg
- core/pdf_utils.py: Utilidades PDF
"""
# Re-exportar todo para compatibilidad
from core.file_utils import (
    get_output_path,
    get_output_path_format,
    ensure_directory,
    validate_input_file,
    validate_file_extension,
    validate_file_size,
    format_error_message,
)

from core.text_utils import (
    STOP_WORDS,
    clean_text,
)

from core.ffmpeg_utils import (
    get_ffmpeg_path,
    get_ffprobe_path,
    check_ffmpeg,
    clear_ffmpeg_cache,
)

from core.pdf_utils import (
    check_pypdf,
    clean_metadata,
)

__all__ = [
    # file_utils
    'get_output_path',
    'get_output_path_format',
    'ensure_directory',
    'validate_input_file',
    'validate_file_extension',
    'validate_file_size',
    'format_error_message',
    # text_utils
    'STOP_WORDS',
    'clean_text',
    # ffmpeg_utils
    'get_ffmpeg_path',
    'get_ffprobe_path',
    'check_ffmpeg',
    'clear_ffmpeg_cache',
    # pdf_utils
    'check_pypdf',
    'clean_metadata',
]