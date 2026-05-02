"""
Processor: Funciones para procesamiento básico de video.
"""
import logging
import subprocess
import os
from pathlib import Path
from typing import Any, Dict, List

from core.utils import get_ffmpeg_path, check_ffmpeg

logger = logging.getLogger(__name__)

# Funciones importadas desde core.utils para evitar duplicación:
# - get_ffmpeg_path()
# - check_ffmpeg()


def extract_audio(video_path: str, output_format: str = 'mp3') -> Dict[str, Any]:
    """Extrae audio de un video."""
    if not check_ffmpeg():
        return {'success': False, 'error': 'FFmpeg no instalado', 'output_files': []}
    
    if not os.path.exists(video_path):
        return {'success': False, 'error': 'Archivo no encontrado', 'output_files': []}
    
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
            return {
                'success': True,
                'message': f'Audio extraido: {output_path.name}',
                'output_files': [str(output_path)],
                'error': None
            }
        else:
            # Get error message
            err = result.stderr[:200] if result.stderr else 'Unknown'
            return {
                'success': False,
                'error': f'Error al extraer: {err[:100]}',
                'output_files': []
            }
            
    except Exception as e:
        return {'success': False, 'error': str(e), 'output_files': []}


def convert_video(files: List[str], output_format: str, **options) -> Dict[str, Any]:
    """Convierte video a otro formato."""
    if not check_ffmpeg():
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
                logger.info(f"Convertido: {p.name} -> {output_path.name}")
            else:
                err = result.stderr[:300] if result.stderr else 'Unknown error'
                errors.append(f"{p.name}: {err[:100]}")
                
        except Exception as e:
            errors.append(f"Excepción: {str(e)}")
    
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


def get_video_info(video_path: str) -> Dict[str, Any]:
    """Obtiene información del video."""
    if not check_ffmpeg():
        return {'success': False, 'error': 'FFmpeg no instalado'}
    
    if not os.path.exists(video_path):
        return {'success': False, 'error': 'Archivo no encontrado'}
    
    try:
        # Get ffprobe from same directory as ffmpeg
        ffmpeg_bin = Path(get_ffmpeg_path()).parent
        ffprobe_bin = ffmpeg_bin / 'ffprobe.exe'
        cmd = [str(ffprobe_bin), '-v', 'quiet', '-print_format', 'json', 
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