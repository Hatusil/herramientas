"""
Conversión de audio: conversión entre formatos (mp3, wav, flac, ogg, etc).
"""
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any

from core.utils import get_ffmpeg_path, check_ffmpeg, get_output_path_format
from core.metrics import Timer, increment

logger = logging.getLogger(__name__)

AUDIO_EXTENSIONS = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.aiff']
MAX_AUDIO_SIZE_MB = 500


def _validate_audio_input(file_path: str) -> Dict[str, Any]:
    """Valida archivo de entrada para operaciones de audio."""
    from core.utils import validate_input_file, validate_file_extension, validate_file_size

    check = validate_input_file(file_path)
    if not check['valid']:
        return check

    check = validate_file_extension(file_path, AUDIO_EXTENSIONS)
    if not check['valid']:
        return check

    check = validate_file_size(file_path, MAX_AUDIO_SIZE_MB)
    if not check['valid']:
        return check

    return {'valid': True}


def convert_audio(files: List[str], output_format: str, **options) -> Dict[str, Any]:
    """
    Convierte archivos de audio a otro formato.

    Args:
        files: Lista de rutas de archivos
        output_format: Formato de salida (mp3/wav/flac/ogg)
        quality: Calidad en kbps (para mp3/ogg)

    Returns:
        dict: Resultado
    """
    with Timer('audio_tool.convert_audio'):
        if not check_ffmpeg():
            increment('audio_errors')
            return {'success': False, 'error': 'FFmpeg no instalado', 'output_files': []}

        valid_formats = ['mp3', 'wav', 'flac', 'ogg', 'aac', 'm4a']
        if output_format.lower() not in valid_formats:
            increment('audio_errors')
            return {'success': False, 'error': f'Formato no válido: {output_format}. Usar: {", ".join(valid_formats)}', 'output_files': []}

        quality = options.get('quality', 192)

        output_files = []
        errors = []
        skipped = []

        for file_path in files:
            input_file = Path(file_path)

            validation = _validate_audio_input(file_path)
            if not validation['valid']:
                errors.append(f"{input_file.name}: {validation['error']}")
                continue

            input_format = input_file.suffix.lstrip('.').lower()
            output_format_lower = output_format.lower()

            requested_quality = options.get('quality', 192)

            if input_format == output_format_lower and requested_quality == 192:
                skipped.append(f"{input_file.name} - Ya está en {input_format.upper()}")
                logger.info(f"Omite (mismo formato): {input_file.name}")
                continue

            if input_format == output_format_lower:
                logger.info(f"Convirtiendo {input_file.name} con calidad {requested_quality}k...")

            ext = f'.{output_format}'
            output_file = get_output_path_format(file_path, '_converted', ext)

            if output_format == 'mp3':
                codec = 'libmp3lame'
                bitrate = f'{quality}k'
            elif output_format == 'wav':
                codec = 'pcm_s16le'
                bitrate = None
            elif output_format == 'flac':
                codec = 'flac'
                bitrate = None
            elif output_format == 'ogg':
                codec = 'libvorbis'
                bitrate = f'{quality}k'
            else:
                codec = 'libmp3lame'
                bitrate = f'{quality}k'

            cmd = [get_ffmpeg_path(), '-y', '-nostdin', '-i', str(input_file)]

            if bitrate:
                cmd.extend(['-b:a', bitrate])

            cmd.extend(['-codec:a', codec, str(output_file)])

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0 and Path(output_file).exists():
                    output_files.append(str(output_file))
                    logger.info(f"Convertido: {input_file.name} -> {output_file.name}")
                else:
                    errors.append(f"Error: {input_file.name}")

            except Exception as e:
                errors.append(f"Excepción: {str(e)}")
                increment('audio_errors')

        if len(output_files) > 0:
            increment('audio_operations_total')

        if not output_files and skipped:
            return {
                'success': True,
                'message': f"Todos los archivos ya están en formato {output_format.upper()} ({len(skipped)} omitidos)",
                'output_files': [],
                'skipped': skipped,
                'error': None
            }

        success = len(output_files) > 0
        msg = f"Convertidos {len(output_files)}/{len(files)} archivos a {output_format.upper()}"
        if skipped:
            msg += f" ({len(skipped)} omitidos)"

        return {
            'success': success,
            'message': msg,
            'output_files': output_files,
            'skipped': skipped,
            'error': '; '.join(errors) if errors else None
        }


# =============================================================================
# ASYNC
# =============================================================================
from core.async_utils import run_in_background


def convert_audio_async(files: List[str], output_format: str, callback, **options):
    """
    Versión async de convert_audio().

    Args:
        files: Lista de rutas de archivos
        output_format: Formato de salida (mp3/wav/flac/ogg)
        callback: Función(result) a llamar al terminar
        **options: Opciones (quality)

    Returns:
        Future
    """
    return run_in_background(convert_audio, files, output_format, callback=callback, **options)