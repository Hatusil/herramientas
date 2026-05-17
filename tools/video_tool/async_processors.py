"""
Funciones async para video_tool - no bloquean la UI.
Separado de processor.py por SRP (máxima R0: clases <300 líneas).
"""
from core.async_utils import run_in_background
from tools.video_tool.processor import extract_audio, convert_video


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


def convert_video_async(files: list, output_format: str, callback, **options):
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