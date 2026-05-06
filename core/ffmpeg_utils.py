"""
Utilidades para FFmpeg.
Cumple con máxima A1 (una sola responsabilidad).
"""
import functools
import logging
import platform
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1)
def get_ffmpeg_path() -> str:
    """
    Obtiene el path de ffmpeg (local o del sistema).
    Cross-platform: Windows (.exe) vs Linux (no extension).
    
    Returns:
        str: Ruta al ejecutable de ffmpeg
    """
    ext = ".exe" if platform.system() == "Windows" else ""
    local_ffmpeg = Path(__file__).parent.parent / "tools" / "ffmpeg" / "bin" / f"ffmpeg{ext}"
    if local_ffmpeg.exists():
        return str(local_ffmpeg)
    return "ffmpeg"  # Usar del PATH


@functools.lru_cache(maxsize=1)
def get_ffprobe_path() -> str:
    """
    Obtiene el path de ffprobe (local o del sistema).
    Cross-platform: Windows (.exe) vs Linux (no extension).
    
    Returns:
        str: Ruta al ejecutable de ffprobe
    """
    ext = ".exe" if platform.system() == "Windows" else ""
    local_ffprobe = Path(__file__).parent.parent / "tools" / "ffmpeg" / "bin" / f"ffprobe{ext}"
    if local_ffprobe.exists():
        return str(local_ffprobe)
    return "ffprobe"  # Usar del PATH


@functools.lru_cache(maxsize=1)
def check_ffmpeg() -> bool:
    """
    Verifica si FFmpeg está instalado y disponible.
    
    Returns:
        bool: True si ffmpeg está disponible
    """
    try:
        ffmpeg = get_ffmpeg_path()
        result = subprocess.run(
            [ffmpeg, '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    except Exception as e:
        logger.warning(f"FFmpeg check failed: {e}")
        return False


def clear_ffmpeg_cache() -> None:
    """
    Limpia la caché de las funciones FFmpeg.
    Útil para testing o cuando se reinstala FFmpeg.
    """
    get_ffmpeg_path.cache_clear()
    get_ffprobe_path.cache_clear()
    check_ffmpeg.cache_clear()