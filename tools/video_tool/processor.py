"""
Processor: Funciones para procesamiento básico de video.
"""
import logging
import subprocess
import os
from pathlib import Path
from typing import Dict, Any

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
        
        codec = 'libmp3lame' if output_format == 'mp3' else 'copy'
        bitrate = '192k' if output_format == 'mp3' else None
        
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


def convert_video(video_path: str, output_format: str, **options) -> Dict[str, Any]:
    """Convierte video a otro formato."""
    if not check_ffmpeg():
        return {'success': False, 'error': 'FFmpeg no instalado', 'output_files': []}
    
    if not os.path.exists(video_path):
        return {'success': False, 'error': 'Archivo no encontrado', 'output_files': []}
    
    try:
        p = Path(video_path)
        output_path = p.parent / f"{p.stem}_converted.{output_format}"
        
        # Codec según formato
        codecs = {
            'mp4': 'libx264',
            'avi': 'mpeg4',
            'mkv': 'libx264',
            'webm': 'libvpx-vp9',
            'mov': 'mpeg4'
        }
        
        codec = codecs.get(output_format, 'libx264')
        
        cmd = [get_ffmpeg_path(), '-y', '-i', video_path, '-codec:v', codec]
        
        # Calidad
        crf = options.get('crf', 23)
        if output_format in ['mp4', 'mkv', 'webm']:
            cmd.extend(['-crf', str(crf)])
        
        # Audio
        cmd.extend(['-codec:a', 'aac', '-b:a', '128k'])
        
        cmd.append(str(output_path))
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0 and output_path.exists():
            return {
                'success': True,
                'message': f'Convertido: {output_path.name}',
                'output_files': [str(output_path)],
                'error': None
            }
        else:
            # Filter out ffmpeg version info from error
            err = result.stderr
            if err and 'ffmpeg version' in err:
                lines = err.split('\n')
                err = '\n'.join([l for l in lines if 'ffmpeg' not in l.lower() and l.strip()])
            return {
                'success': False,
                'error': 'Error al convertir video',
                'output_files': []
            }
            
    except Exception as e:
        return {'success': False, 'error': str(e), 'output_files': []}


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
            
            'audio_codec': audio_stream.get('codec_name', 'N/A') if audio_stream else 'N/A',
            'audio_bitrate': audio_stream.get('bit_rate', 'N/A') if audio_stream else 'N/A',
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}