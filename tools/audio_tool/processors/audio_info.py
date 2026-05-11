"""
Audio info: Obtiene información de archivos de audio vía ffprobe.
"""
import subprocess
import logging
import os
from typing import Dict, Any, List, Optional

from core.utils import get_ffprobe_path, check_ffmpeg

logger = logging.getLogger(__name__)


def _run_ffprobe(file_path: str) -> Dict[str, Any]:
    """Ejecutar ffprobe y retornar JSON."""
    import json
    cmd = [
        get_ffprobe_path(),
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        file_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if result.returncode != 0:
        raise Exception('Error leyendo archivo')

    return json.loads(result.stdout)


def _extract_audio_stream(streams: List[Dict]) -> Optional[Dict]:
    """Extraer stream de audio del JSON."""
    for s in streams:
        if s.get('codec_type') == 'audio':
            return s
    return None


def _format_audio_info(
    file_path: str,
    format_info: Dict,
    audio_stream: Optional[Dict]
) -> Dict[str, Any]:
    """Formatear información para respuesta."""
    return {
        'success': True,
        'file_name': os.path.basename(file_path),
        'file_size': int(format_info.get('size', 0)),
        'duration': float(format_info.get('duration', 0)),
        'format': format_info.get('format_name', 'desconocido'),

        # Audio
        'codec': audio_stream.get('codec_name', 'desconocido') if audio_stream else 'N/A',
        'sample_rate': int(audio_stream.get('sample_rate', 0)) if audio_stream else 0,
        'channels': audio_stream.get('channels', 0) if audio_stream else 0,
        'bit_rate': int(format_info.get('bit_rate', 0)),

        # Tags
        'title': format_info.get('tags', {}).get('title', ''),
        'artist': format_info.get('tags', {}).get('artist', ''),
        'album': format_info.get('tags', {}).get('album', ''),
        'track': format_info.get('tags', {}).get('track', ''),
        'year': format_info.get('tags', {}).get('date', ''),
        'genre': format_info.get('tags', {}).get('genre', ''),
    }


def get_audio_info(file_path: str) -> Dict[str, Any]:
    """
    Obtiene información y metadatos de un archivo de audio.

    Args:
        file_path: Ruta al archivo de audio

    Returns:
        dict: Información del archivo
    """
    if not os.path.exists(file_path):
        return {'success': False, 'error': 'Archivo no encontrado'}

    if not check_ffmpeg():
        return {'success': False, 'error': 'FFmpeg no instalado'}

    try:
        data = _run_ffprobe(file_path)

        format_info = data.get('format', {})
        streams = data.get('streams', [])

        audio_stream = _extract_audio_stream(streams)

        return _format_audio_info(file_path, format_info, audio_stream)

    except Exception as e:
        logger.error(f"Error obteniendo info: {e}")
        return {'success': False, 'error': str(e)}


def get_metadata(file_path: str) -> Dict[str, Any]:
    """Alias para get_audio_info."""
    return get_audio_info(file_path)
