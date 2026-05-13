"""
Utilidades para FFmpeg.
Cumple con máxima A1 (una sola responsabilidad).
"""
import functools
import logging
import platform
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1)
def get_ffmpeg_path() -> str:
    """
    Obtiene el path de ffmpeg (local, bundle PyInstaller, o PATH).
    Cross-platform: Windows (.exe) vs Linux (no extension).

    Returns:
        str: Ruta al ejecutable de ffmpeg
    """
    ext = ".exe" if platform.system() == "Windows" else ""

    # 1. Buscar en bundle PyInstaller (_MEIPASS)
    if hasattr(sys, '_MEIPASS'):
        bundled = Path(sys._MEIPASS) / "ffmpeg" / f"ffmpeg{ext}"
        if bundled.exists():
            return str(bundled)

    # 2. Buscar en tools/ffmpeg/bin (desarrollo)
    local_ffmpeg = Path(__file__).parent.parent / "tools" / "ffmpeg" / "bin" / f"ffmpeg{ext}"
    if local_ffmpeg.exists():
        return str(local_ffmpeg)

    # 3. Usar del PATH
    return "ffmpeg"


@functools.lru_cache(maxsize=1)
def get_ffprobe_path() -> str:
    """
    Obtiene el path de ffprobe (local, bundle PyInstaller, o PATH).
    Cross-platform: Windows (.exe) vs Linux (no extension).

    Returns:
        str: Ruta al ejecutable de ffprobe
    """
    ext = ".exe" if platform.system() == "Windows" else ""

    # 1. Buscar en bundle PyInstaller (_MEIPASS)
    if hasattr(sys, '_MEIPASS'):
        bundled = Path(sys._MEIPASS) / "ffmpeg" / f"ffprobe{ext}"
        if bundled.exists():
            return str(bundled)

    # 2. Buscar en tools/ffmpeg/bin (desarrollo)
    local_ffprobe = Path(__file__).parent.parent / "tools" / "ffmpeg" / "bin" / f"ffprobe{ext}"
    if local_ffprobe.exists():
        return str(local_ffprobe)

    # 3. Usar del PATH
    return "ffprobe"


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