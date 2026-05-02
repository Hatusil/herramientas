"""
Processor: Funciones de procesamiento de audio usando FFmpeg.
"""
import subprocess
import logging
import os
import json
from pathlib import Path
from typing import List, Dict, Any

from core import constants
from core.utils import get_ffmpeg_path, check_ffmpeg, get_output_path, get_output_path_format


logger = logging.getLogger(__name__)


# =============================================================================
# UTILIDADES
# =============================================================================
# Funciones importadas desde core.utils para evitar duplicación:
# - get_ffmpeg_path()
# - check_ffmpeg()
# - get_output_path()
# - get_output_path_format()


# =============================================================================
# INFO - METADATOS
# =============================================================================

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
        # Usar ffprobe desde la misma ubicación que ffmpeg
        ffmpeg_bin = Path(get_ffmpeg_path()).parent
        ffprobe_bin = ffmpeg_bin / 'ffprobe.exe'
        
        # Usar ffprobe para obtener info
        cmd = [
            str(ffprobe_bin) if ffprobe_bin.exists() else 'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return {'success': False, 'error': 'Error leyendo archivo'}
        
        data = json.loads(result.stdout)
        
        # Extraer info relevante
        format_info = data.get('format', {})
        streams = data.get('streams', [])
        
        # Buscar stream de audio
        audio_stream = None
        for s in streams:
            if s.get('codec_type') == 'audio':
                audio_stream = s
                break
        
        info = {
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
        
        return info
        
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
    if not check_ffmpeg():
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
        except Exception as e:
            errors.append(f"Excepción: {str(e)}")
    
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
    if not check_ffmpeg():
        return {'success': False, 'error': 'FFmpeg no instalado', 'output_files': []}
    
    quality = options.get('quality', 192)
    requested_bitrate = quality * 1000  # Convert to bps
    
    output_files = []
    errors = []
    skipped = []
    
    for file_path in files:
        input_file = Path(file_path)
        
        if not input_file.exists():
            errors.append(f"No encontrado: {input_file.name}")
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
        # Usar ffprobe para verificar
        ffmpeg_bin = Path(get_ffmpeg_path()).parent
        ffprobe_bin = ffmpeg_bin / 'ffprobe.exe'
        
        cmd = [
            str(ffprobe_bin) if ffprobe_bin.exists() else 'ffprobe',
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