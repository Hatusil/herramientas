"""
Processor: Funciones de procesamiento de audio usando FFmpeg.
"""
import subprocess
import logging
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from core import constants
from core.utils import get_ffmpeg_path, get_ffprobe_path, check_ffmpeg, get_output_path, get_output_path_format, validate_input_file, validate_file_extension, validate_file_size

# Métricas
from core.metrics import Counter, Timer, increment

logger = logging.getLogger(__name__)

# Contadores de operaciones
audio_operations_total = Counter('audio_operations_total')
audio_errors = Counter('audio_errors')


# =============================================================================
# UTILIDADES
# =============================================================================
# Funciones importadas desde core.utils para evitar duplicación:
# - get_ffmpeg_path(), check_ffmpeg(), get_output_path(), get_output_path_format()
# - validate_input_file(), validate_file_extension(), validate_file_size()

AUDIO_EXTENSIONS = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.aiff']
MAX_AUDIO_SIZE_MB = 500  # 500MB max for audio files


def _validate_audio_input(file_path: str) -> Dict[str, Any]:
    """
    Valida archivo de entrada para operaciones de audio.
    
    Returns:
        {'valid': bool, 'error': str or None}
    """
    # Check existence
    check = validate_input_file(file_path)
    if not check['valid']:
        return check
    
    # Check extension
    check = validate_file_extension(file_path, AUDIO_EXTENSIONS)
    if not check['valid']:
        return check
    
    # Check size
    check = validate_file_size(file_path, MAX_AUDIO_SIZE_MB)
    if not check['valid']:
        return check
    
    return {'valid': True}


# =============================================================================
# INFO - METADATOS
# =============================================================================

# A1: Funciones helper para SRP - get_audio_info refactorizada

def _run_ffprobe(file_path: str) -> Dict[str, Any]:
    """1. Ejecutar ffprobe y retornar JSON."""
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
    """2. Extraer stream de audio del JSON."""
    for s in streams:
        if s.get('codec_type') == 'audio':
            return s
    return None


def _format_audio_info(file_path: str, format_info: Dict, audio_stream: Optional[Dict]) -> Dict[str, Any]:
    """3. Formatear información para respuesta."""
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
        # A1: Usar funciones helper separadas (SRP)
        data = _run_ffprobe(file_path)
        
        format_info = data.get('format', {})
        streams = data.get('streams', [])
        
        audio_stream = _extract_audio_stream(streams)
        
        return _format_audio_info(file_path, format_info, audio_stream)
        
    except Exception as e:
        logger.error(f"Error obteniendo info: {e}")
        return {'success': False, 'error': str(e)}


# =============================================================================
# NORMALIZAR
# =============================================================================

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
        sample_rate = options.get('sample_rate')  # None = mantener
        quality = options.get('quality', 192)  # kbps
        
        output_files = []
        errors = []
        
        for file_path in files:
            input_file = Path(file_path)
            
            if not input_file.exists():
                errors.append(f"No encontrado: {input_file.name}")
                continue
            
            if input_file.suffix.lower() not in ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac']:
                errors.append(f"Formato no soportado: {input_file.suffix}")
                continue
            
            output_file = get_output_path(file_path, '_normalized')
            
            # Construir filtro de audio
            af_filters = [f'loudnorm=I={target_lufs}:LRA={constants.LRA}:TP={constants.TP}']
            
            # Nota: alimiter puede causar problemas en algunos sistemas
            # Por ahora lo comentamos hasta verificar compatibilidad
            # if limit_clipping:
            #     af_filters.append('alimiter=limit=0.95')
            
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
                    # Show error from FFmpeg
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
        
        return {
            'success': success,
            'message': f"Normalizados {len(output_files)}/{len(files)} archivos",
            'output_files': output_files,
            'error': '; '.join(errors) if errors else None
        }


# =============================================================================
# LIMPIAR METADATOS
# =============================================================================

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


# =============================================================================
# EDITAR METADATOS
# =============================================================================

def validate_metadata_value(value: str, max_length: int = 100) -> tuple[bool, str]:
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
# CONVERTIR
# =============================================================================

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
        
        # Validate output format
        valid_formats = ['mp3', 'wav', 'flac', 'ogg', 'aac', 'm4a']
        if output_format.lower() not in valid_formats:
            increment('audio_errors')
            return {'success': False, 'error': f'Formato no válido: {output_format}. Usar: {", ".join(valid_formats)}', 'output_files': []}
        
        quality = options.get('quality', 192)
        requested_bitrate = quality * 1000  # Convert to bps
        
        output_files = []
        errors = []
        skipped = []
        
        for file_path in files:
            input_file = Path(file_path)
            
            # Validate with helper
            validation = _validate_audio_input(file_path)
            if not validation['valid']:
                errors.append(f"{input_file.name}: {validation['error']}")
                continue
            
            # Determinar formato de entrada por extensión
            input_format = input_file.suffix.lstrip('.').lower()
            output_format_lower = output_format.lower()
            
            # Obtener calidad elegida
            requested_quality = options.get('quality', 192)
            
            # Skip solo si mismo formato Y misma calidad por defecto
            if input_format == output_format_lower and requested_quality == 192:
                skipped.append(f"{input_file.name} - Ya está en {input_format.upper()}")
                logger.info(f"Omite (mismo formato): {input_file.name}")
                continue
            
            # Skip si mismo formato pero diferente calidad
            if input_format == output_format_lower:
                logger.info(f"Convirtiendo {input_file.name} con calidad {requested_quality}k...")
            
            # Nuevo formato
            ext = f'.{output_format}'
            output_file = get_output_path_format(file_path, '_converted', ext)
            
            # Codec según formato
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
        
        # Verificar si todos fueron omitidos
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
# REPARAR
# =============================================================================

def verify_audio_integrity(file_path: str) -> Dict[str, Any]:
    """
    Verifica si un archivo de audio está corrupto o no.
    Returns: {'corrupt': bool, 'message': str, 'details': dict}
    """
    if not check_ffmpeg():
        return {'corrupt': False, 'message': 'FFmpeg no instalado', 'details': {}}
    
    if not os.path.exists(file_path):
        return {'corrupt': False, 'message': 'Archivo no encontrado', 'details': {}}
    
    try:
        # Usar función cross-platform get_ffprobe_path()
        cmd = [
            get_ffprobe_path(),
            '-v', 'error',
            '-show_format',
            '-show_streams',
            file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            # Hay error - archivo potencialmente corrupto
            return {
                'corrupt': True,
                'message': 'Archivo corrupto o no válido',
                'details': {'error': result.stderr[:200]}
            }
        
        # Verificar si tiene stream de audio
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
            '-b:a', '320k',  # Alta calidad
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
# INFO (Aliases para compatibilidad)
# =============================================================================

def get_metadata(file_path: str) -> Dict[str, Any]:
    """Alias para get_audio_info."""
    return get_audio_info(file_path)


# =============================================================================
# ASYNC VERSIONS - No bloquean UI
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