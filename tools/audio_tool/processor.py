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
    
    for file_path in files:
        input_file = Path(file_path)
        
        if not input_file.exists():
            errors.append(f"No encontrado: {input_file.name}")
            continue
        
        output_file = get_output_path(file_path, '_clean')
        
        # Copiar sin metadatos - opciones seguras
        cmd = [
            get_ffmpeg_path(), '-y', '-nostdin',
            '-i', str(input_file),
            '-codec:a', 'libmp3lame',
            '-b:a', '320k',  # Alta calidad
            '-map_metadata', '0',  # Remove all metadata
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
    
    success = len(output_files) > 0
    
    return {
        'success': success,
        'message': f"Limpiados {len(output_files)}/{len(files)} archivos",
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
    
    output_files = []
    errors = []
    
    for file_path in files:
        input_file = Path(file_path)
        
        if not input_file.exists():
            errors.append(f"No encontrado: {input_file.name}")
            continue
        
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
    
    success = len(output_files) > 0
    
    return {
        'success': success,
        'message': f"Convertidos {len(output_files)}/{len(files)} archivos a {output_format.upper()}",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


# =============================================================================
# REPARAR
# =============================================================================

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