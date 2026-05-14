"""
Normalización de audio: loudness normalization usando EBU R128.
"""
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any

from core import constants
from core.utils import get_ffmpeg_path, check_ffmpeg, get_output_path
from core.metrics import Timer, increment

logger = logging.getLogger(__name__)


def normalize_audio(files: List[str], **options) -> Dict[str, Any]:
    """
    Normaliza el volumen de archivos de audio.

    Args:
        files: Lista de rutas de archivos
        target_lufs: Target LUFS (default: -16)
        limit_clipping: Si agregar limitador para evitar clipping
        sample_rate: Frecuencia de muestreo (None = mantener)
        quality: Calidad MP3 en kbps (128/192/256/320)

    Returns:
        dict: Resultado con success, message, output_files, error
    """
    with Timer('audio_tool.normalize_audio'):
        if not check_ffmpeg():
            increment('audio_errors')
            return {'success': False, 'error': 'FFmpeg no instalado', 'output_files': []}

        target_lufs = options.get('target_lufs', -16)
        limit_clipping = options.get('limit_clipping', True)
        sample_rate = options.get('sample_rate')
        quality = options.get('quality', 192)

        output_files = []
        errors = []
        skipped = []

        for file_path in files:
            input_file = Path(file_path)

            if not input_file.exists():
                errors.append(f"No encontrado: {input_file.name}")
                continue

                if input_file.suffix.lower() not in ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac']:
                    errors.append(f"Formato no soportado: {input_file.suffix}")
                    continue

            # Skip already normalized files
            if input_file.stem.endswith('_normalized'):
                skipped.append(input_file.name)
                continue

            output_file = get_output_path(file_path, '_normalized')

            # Construir filtro de audio
            af_filters = [f'loudnorm=I={target_lufs}:LRA={constants.LRA}:TP={constants.TP}']

            if sample_rate:
                af_filters.append(f'aresample=async={sample_rate}')

            af_string = ','.join(af_filters)

            # Determinar codec y calidad según formato
            if input_file.suffix.lower() == '.mp3':
                codec = 'libmp3lame'
                bitrate = f'{quality}k'
            elif input_file.suffix.lower() == '.wav':
                codec = 'pcm_s16le'
                bitrate = None
            elif input_file.suffix.lower() == '.flac':
                codec = 'flac'
                bitrate = None
            else:
                codec = 'libmp3lame'
                bitrate = f'{quality}k'

            cmd = [get_ffmpeg_path(), '-y', '-nostdin', '-i', str(input_file), '-af', af_string]

            if bitrate:
                cmd.extend(['-b:a', bitrate])
            if sample_rate:
                cmd.extend(['-ar', str(sample_rate)])

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
                    logger.info(f"Normalizado: {input_file.name}")
                else:
                    err = result.stderr[-300:] if result.stderr else 'Unknown'
                    errors.append(f"{input_file.name}: {err[:100]}")

            except subprocess.TimeoutExpired:
                errors.append(f"Timeout: {input_file.name}")
                increment('audio_errors')
            except Exception as e:
                errors.append(f"Excepción: {str(e)}")
                increment('audio_errors')

        if len(output_files) > 0:
            increment('audio_operations_total')

        success = len(output_files) > 0

        skipped_msg = f", omitidos {len(skipped)}" if skipped else ""
        return {
            'success': success,
            'message': f"Normalizados {len(output_files)}/{len(files)} archivos{skipped_msg}",
            'output_files': output_files,
            'skipped_files': skipped,
            'error': '; '.join(errors) if errors else None
        }


# =============================================================================
# ASYNC
# =============================================================================
from core.async_utils import run_in_background


def normalize_audio_async(files: List[str], callback, **options):
    """
    Versión async de normalize_audio().

    Args:
        files: Lista de rutas de archivos
        callback: Función(result) a llamar al terminar
        **options: Opciones (target_lufs, limit_clipping, sample_rate, quality)

    Returns:
        Future
    """
    return run_in_background(normalize_audio, files, callback=callback, **options)