"""
Reparación de audio: detecta y repara archivos corruptos.
"""
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any

from core.utils import get_ffmpeg_path, check_ffmpeg, get_output_path

logger = logging.getLogger(__name__)


def verify_audio_integrity(file_path: str) -> Dict[str, Any]:
    """
    Verifica si un archivo de audio está corrupto.

    Returns:
        {'corrupt': bool, 'message': str, 'details': dict}
    """
    from core.utils import get_ffprobe_path

    if not check_ffmpeg():
        return {'corrupt': False, 'message': 'FFmpeg no instalado', 'details': {}}

    if not Path(file_path).exists():
        return {'corrupt': False, 'message': 'Archivo no encontrado', 'details': {}}

    try:
        cmd = [
            get_ffprobe_path(),
            '-v', 'error',
            '-show_format',
            '-show_streams',
            file_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            return {
                'corrupt': True,
                'message': 'Archivo corrupto o no válido',
                'details': {'error': result.stderr[:200]}
            }

        if 'audio' not in result.stdout.lower():
            return {
                'corrupt': True,
                'message': 'No contiene stream de audio',
                'details': {}
            }

        return {'corrupt': False, 'message': 'Archivo OK', 'details': {}}

    except subprocess.TimeoutExpired:
        return {'corrupt': True, 'message': 'Timeout al verificar', 'details': {}}
    except Exception as e:
        return {'corrupt': True, 'message': f'Error: {str(e)}', 'details': {}}


def verify_multiple_audio(files: List[str]) -> Dict[str, Any]:
    """Verifica múltiples archivos y retorna el estado de cada uno."""
    results = []
    corrupt_count = 0
    ok_count = 0

    for file_path in files:
        result = verify_audio_integrity(file_path)
        results.append({
            'file': file_path,
            'name': Path(file_path).name,
            'corrupt': result['corrupt'],
            'message': result['message']
        })
        if result['corrupt']:
            corrupt_count += 1
        else:
            ok_count += 1

    return {
        'success': True,
        'total': len(files),
        'ok': ok_count,
        'corrupt': corrupt_count,
        'results': results
    }


def repair_audio(files: List[str]) -> Dict[str, Any]:
    """
    Repara archivos de audio corruptos.
    Solo usa opciones seguras que no rompan archivos buenos.
    """
    if not check_ffmpeg():
        return {'success': False, 'error': 'FFmpeg no instalado', 'output_files': []}

    output_files = []
    errors = []

    for file_path in files:
        input_file = Path(file_path)

        if not input_file.exists():
            errors.append(f"No encontrado: {input_file.name}")
            continue

        output_file = get_output_path(file_path, '_repaired')

        # Opciones conservative - solo re-encodear sin perder calidad
        cmd = [
            get_ffmpeg_path(), '-y', '-nostdin',
            '-i', str(input_file),
            '-codec:a', 'libmp3lame',
            '-b:a', '320k',
            str(output_file)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0 and Path(output_file).exists():
                output_files.append(str(output_file))
                logger.info(f"Reparado: {input_file.name}")
            else:
                errors.append(f"No se pudo reparar: {input_file.name}")

        except Exception as e:
            errors.append(f"Excepción: {str(e)}")

    success = len(output_files) > 0

    return {
        'success': success,
        'message': f"Reparados {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


# =============================================================================
# ASYNC
# =============================================================================
from core.async_utils import run_in_background


def repair_audio_async(files: List[str], callback):
    """
    Versión async de repair_audio().

    Args:
        files: Lista de rutas de archivos
        callback: Función(result) a llamar al terminar

    Returns:
        Future
    """
    return run_in_background(repair_audio, files, callback=callback)
