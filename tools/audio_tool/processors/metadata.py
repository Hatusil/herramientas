"""
Metadatos de audio: limpieza y edición de tags.
"""
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any

from core.utils import get_ffmpeg_path, check_ffmpeg, get_output_path
from tools.audio_tool.processors.audio_info import get_audio_info

logger = logging.getLogger(__name__)


def validate_metadata_value(value: str, max_length: int = 100) -> tuple:
    """
    Valida un valor de metadato.

    Args:
        value: Valor a validar
        max_length: Longitud máxima permitida

    Returns:
        (is_valid, sanitized_value)
    """
    if not value:
        return (False, "")

    value = ' '.join(value.split())

    if not value.strip():
        return (False, "")

    if len(value) > max_length:
        value = value[:max_length]

    allowed_pattern = "ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÜÑabcdefghijklmnopqrstuvwxyz0123456789 ()-_.!,?'&"

    sanitized = ""
    for char in value:
        if char.upper() in allowed_pattern.upper():
            sanitized += char

    if not sanitized.strip():
        return (False, "")

    return (True, sanitized)


def clean_audio_metadata(files: List[str]) -> Dict[str, Any]:
    """
    Limpia metadatos de archivos de audio.

    Args:
        files: Lista de rutas de archivos

    Returns:
        dict: Resultado
    """
    if not check_ffmpeg():
        return {'success': False, 'error': 'FFmpeg no instalado', 'output_files': []}

    output_files = []
    errors = []
    skipped = []

    for file_path in files:
        input_file = Path(file_path)

        if not input_file.exists():
            errors.append(f"No encontrado: {input_file.name}")
            continue

        audio_info = get_audio_info(str(input_file))

        if not audio_info.get('success'):
            errors.append(f"Error leyendo: {input_file.name}")
            continue

        metadata_fields = ['title', 'artist', 'album', 'track', 'year', 'genre']
        has_metadata = any(audio_info.get(field) for field in metadata_fields)

        if not has_metadata:
            skipped.append(input_file.name)
            logger.info(f"Sin metadatos: {input_file.name} - omitido")
            continue

        output_file = get_output_path(file_path, '_clean')

        cmd = [
            get_ffmpeg_path(), '-y', '-nostdin',
            '-i', str(input_file),
            '-codec:a', 'libmp3lame',
            '-b:a', '320k',
            '-map_metadata', '0',
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
                logger.info(f"Limpiado: {input_file.name}")
            else:
                err = result.stderr[-200:] if result.stderr else 'Unknown error'
                errors.append(f"{input_file.name}: {err[:80]}")

        except Exception as e:
            errors.append(f"Excepción: {str(e)}")

    if skipped and not output_files:
        return {
            'success': False,
            'message': f"No hay metadatos para limpiar en {len(skipped)} archivo(s)",
            'output_files': [],
            'error': None
        }

    success = len(output_files) > 0
    msg = f"Limpiados {len(output_files)}/{len(files)} archivos"
    if skipped:
        msg += f" ({len(skipped)} sin metadatos)"

    return {
        'success': success,
        'message': msg,
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


def edit_audio_metadata(
    files: List[str],
    title: str = None,
    artist: str = None,
    album: str = None,
    genre: str = None,
    year: str = None,
    track: str = None,
    comment: str = None,
    composer: str = None
) -> Dict[str, Any]:
    """
    Edita metadatos de archivos de audio.
    """
    if not check_ffmpeg():
        return {'success': False, 'error': 'FFmpeg no instalado', 'output_files': []}

    metadata_fields = {}
    field_map = {
        'title': title,
        'artist': artist,
        'album': album,
        'genre': genre,
        'date': year,
        'track': track,
        'comment': comment,
        'composer': composer
    }

    for field, value in field_map.items():
        if value:
            is_valid, sanitized = validate_metadata_value(value)
            if is_valid:
                metadata_fields[field] = sanitized

    if not metadata_fields:
        return {'success': False, 'error': 'No hay metadatos válidos para agregar'}

    output_files = []
    errors = []

    for file_path in files:
        input_file = Path(file_path)

        if not input_file.exists():
            errors.append(f"No encontrado: {input_file.name}")
            continue

        output_file = get_output_path(file_path, '_edited')

        cmd = [
            get_ffmpeg_path(), '-y', '-nostdin',
            '-i', str(input_file),
            '-codec:a', 'libmp3lame',
            '-b:a', '320k'
        ]

        for field, value in metadata_fields.items():
            cmd.extend(['-metadata', f'{field}={value}'])

        cmd.append(str(output_file))

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0 and Path(output_file).exists():
                output_files.append(str(output_file))
                logger.info(f"Editado: {input_file.name}")
            else:
                err = result.stderr[-200:] if result.stderr else 'Unknown error'
                errors.append(f"{input_file.name}: {err[:80]}")

        except Exception as e:
            errors.append(f"Excepción: {str(e)}")

    success = len(output_files) > 0
    fields_edited = ', '.join(metadata_fields.keys())

    return {
        'success': success,
        'message': f"Editados {len(output_files)}/{len(files)} archivos ({fields_edited})",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


# =============================================================================
# ASYNC
# =============================================================================
from core.async_utils import run_in_background


def clean_audio_metadata_async(files: List[str], callback):
    """
    Versión async de clean_audio_metadata().

    Args:
        files: Lista de rutas de archivos
        callback: Función(result) a llamar al terminar

    Returns:
        Future
    """
    return run_in_background(clean_audio_metadata, files, callback=callback)


def edit_audio_metadata_async(files: List[str], callback, **metadata):
    """
    Versión async de edit_audio_metadata().

    Args:
        files: Lista de rutas de archivos
        callback: Función(result) a llamar al terminar
        **metadata: title, artist, album, genre, year, track, comment, composer

    Returns:
        Future
    """
    return run_in_background(
        edit_audio_metadata, files,
        title=metadata.get('title'),
        artist=metadata.get('artist'),
        album=metadata.get('album'),
        genre=metadata.get('genre'),
        year=metadata.get('year'),
        track=metadata.get('track'),
        comment=metadata.get('comment'),
        composer=metadata.get('composer'),
        callback=callback
    )