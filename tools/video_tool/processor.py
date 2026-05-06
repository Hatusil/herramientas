"""
Processor: Funciones para procesamiento básico de video.
"""
import logging
import subprocess
import os
from pathlib import Path
from typing import Any, Dict, List

from core.utils import get_ffmpeg_path, get_ffprobe_path, check_ffmpeg, get_output_path, validate_input_file, validate_file_extension, validate_file_size

# Métricas
from core.metrics import Counter, Timer, increment

logger = logging.getLogger(__name__)

# Funciones importadas desde core.utils para evitar duplicación:
# - get_ffmpeg_path(), check_ffmpeg()
# - validate_input_file(), validate_file_extension(), validate_file_size()

VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v']
MAX_VIDEO_SIZE_MB = 2000  # 2GB max for video files


def _validate_video_input(file_path: str) -> Dict[str, Any]:
    """Valida archivo de entrada para operaciones de video."""
    check = validate_input_file(file_path)
    if not check['valid']:
        return check
    check = validate_file_extension(file_path, VIDEO_EXTENSIONS)
    if not check['valid']:
        return check
    check = validate_file_size(file_path, MAX_VIDEO_SIZE_MB)
    if not check['valid']:
        return check
    return {'valid': True}


def extract_audio(video_path: str, output_format: str = 'mp3') -> Dict[str, Any]:
    """Extrae audio de un video."""
    with Timer('video_tool.extract_audio'):
        if not check_ffmpeg():
            increment('video_tool.errors')
            return {'success': False, 'error': 'FFmpeg no instalado', 'output_files': []}
        
        # Validate input
        validation = _validate_video_input(video_path)
        if not validation['valid']:
            increment('video_tool.errors')
            return {'success': False, 'error': validation['error'], 'output_files': []}
        
        try:
            p = Path(video_path)
            output_path = p.parent / f"{p.stem}_audio.{output_format}"
            
            # Configurar codec según formato de salida
            if output_format == 'mp3':
                codec = 'libmp3lame'
                bitrate = '192k'
            elif output_format == 'ogg':
                codec = 'libvorbis'
                bitrate = '192k'
            elif output_format == 'wav':
                codec = 'pcm_s16le'
                bitrate = None
            else:
                codec = 'copy'
                bitrate = None
            
            cmd = [get_ffmpeg_path(), '-y', '-i', video_path, '-vn']
            
            if bitrate:
                cmd.extend(['-b:a', bitrate])
            
            cmd.extend(['-codec:a', codec, str(output_path)])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and output_path.exists():
                increment('video_tool.audio_extracted')
                return {
                    'success': True,
                    'message': f'Audio extraido: {output_path.name}',
                    'output_files': [str(output_path)],
                    'error': None
                }
            else:
                # Get error message
                err = result.stderr[:200] if result.stderr else 'Unknown'
                increment('video_tool.errors')
                return {
                    'success': False,
                    'error': f'Error al extraer: {err[:100]}',
                    'output_files': []
                }
                
        except Exception as e:
            increment('video_tool.errors')
            return {'success': False, 'error': str(e), 'output_files': []}


def convert_video(files: List[str], output_format: str, **options) -> Dict[str, Any]:
    """Convierte video a otro formato."""
    with Timer('video_tool.convert_video'):
        if not check_ffmpeg():
            increment('video_tool.errors')
            return {'success': False, 'error': 'FFmpeg no instalado', 'output_files': []}
        
        output_files = []
        errors = []
        skipped = []
        
        video_codecs = {
            'mp4': 'libx264',
            'avi': 'mpeg4',
            'mkv': 'libx264',
            'mov': 'mpeg4'
        }
        
        audio_codecs = {
            'mp4': 'aac',
            'avi': 'mp3',
            'mkv': 'aac',
            'mov': 'aac'
        }
        
        for video_path in files:
            if not os.path.exists(video_path):
                errors.append(f"No encontrado: {Path(video_path).name}")
                continue
            
            # Determinar formato de entrada
            input_format = Path(video_path).suffix.lstrip('.').lower()
            output_format_lower = output_format.lower()
            
            # Obtener CRF elegido por usuario
            user_crf = options.get('crf', 23)
            default_crf = 23
            
            # Skip solo si mismo formato Y mismo CRF (calidad por defecto)
            if input_format == output_format_lower and user_crf == default_crf:
                skipped.append(f"{Path(video_path).name} - Ya está en {input_format.upper()}")
                logger.info(f"Omite (mismo formato): {Path(video_path).name}")
                continue
            
            # Skip con formatos iguales pero diferente CRF
            if input_format == output_format_lower:
                logger.info(f"Convirtiendo {Path(video_path).name} con CRF {user_crf}...")
            
            # Obtener info solo si necesita conversión
            video_info = get_video_info(video_path)
            
            p = Path(video_path)
            output_path = p.parent / f"{p.stem}_converted.{output_format}"
            
            logger.info(f"Convirtiendo {p.name} a {output_format}...")
            
            video_codec = video_codecs.get(output_format, 'libx264')
            audio_codec = audio_codecs.get(output_format, 'aac')
            
            cmd = [get_ffmpeg_path(), '-y', '-i', video_path, '-codec:v', video_codec]
            
            if output_format in ['mp4', 'mkv']:
                cmd.extend(['-preset', 'medium'])
            
            crf = options.get('crf', 23)
            if output_format in ['mp4', 'mkv']:
                cmd.extend(['-crf', str(crf)])
            
            if audio_codec in ['libopus', 'libvorbis']:
                cmd.extend(['-codec:a', audio_codec])
            else:
                cmd.extend(['-codec:a', audio_codec, '-b:a', '128k'])
            
            cmd.append(str(output_path))
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                
                if result.returncode == 0 and output_path.exists():
                    output_files.append(str(output_path))
                    increment('video_tool.video_converted')
                    logger.info(f"Convertido: {p.name} -> {output_path.name}")
                else:
                    err = result.stderr[:300] if result.stderr else 'Unknown error'
                    errors.append(f"{p.name}: {err[:100]}")
                    increment('video_tool.errors')
                    
            except Exception as e:
                errors.append(f"Excepción: {str(e)}")
                increment('video_tool.errors')
        
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
        
        if not success and errors:
            increment('video_tool.errors')
        
        return {
            'success': success,
            'message': msg,
            'output_files': output_files,
            'skipped': skipped,
            'error': '; '.join(errors) if errors else None
        }


def get_video_info(video_path: str) -> Dict[str, Any]:
    """Obtiene información del video."""
    if not check_ffmpeg():
        return {'success': False, 'error': 'FFmpeg no instalado'}
    
    if not os.path.exists(video_path):
        return {'success': False, 'error': 'Archivo no encontrado'}
    
    try:
        # Use cross-platform get_ffprobe_path()
        cmd = [get_ffprobe_path(), '-v', 'quiet', '-print_format', 'json', 
               '-show_format', '-show_streams', video_path]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return {'success': False, 'error': 'Error leyendo video'}
        
        import json
        data = json.loads(result.stdout)
        
        # Buscar streams
        video_stream = None
        audio_stream = None
        
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
            elif stream.get('codec_type') == 'audio':
                audio_stream = stream
        
        fmt = data.get('format', {})
        
        return {
            'success': True,
            'file_name': os.path.basename(video_path),
            'file_size': int(fmt.get('size', 0)),
            'duration': float(fmt.get('duration', 0)),
            'format': fmt.get('format_name', ''),
            
            'video_codec': video_stream.get('codec_name', 'N/A') if video_stream else 'N/A',
            'video_resolution': f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}" if video_stream else 'N/A',
            'video_fps': video_stream.get('r_frame_rate', 'N/A') if video_stream else 'N/A',
            'video_bitrate': fmt.get('bit_rate', 'N/A') if fmt else 'N/A',
            
            'audio_codec': audio_stream.get('codec_name', 'N/A') if audio_stream else 'N/A',
            'audio_bitrate': audio_stream.get('bit_rate', 'N/A') if audio_stream else 'N/A',
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


# =============================================================================
# ASYNC VERSIONS - No bloquean UI
# =============================================================================
from core.async_utils import run_in_background

def extract_audio_async(video_path: str, output_format: str, callback):
    """
    Versión async de extract_audio().
    
    Args:
        video_path: Ruta al video
        output_format: Formato de salida (mp3/ogg/wav)
        callback: Función(result) a llamar al terminar
    
    Returns:
        Future
    """
    return run_in_background(extract_audio, video_path, output_format, callback=callback)


def convert_video_async(files: List[str], output_format: str, callback, **options):
    """
    Versión async de convert_video().
    
    Args:
        files: Lista de rutas de videos
        output_format: Formato de salida (mp4/avi/mkv)
        callback: Función(result) a llamar al terminar
        **options: crf, etc.
    
    Returns:
        Future
    """
    return run_in_background(convert_video, files, output_format, callback=callback, **options)