"""
Utilidades comunes del proyecto.
Funciones helper que pueden ser usadas por múltiples módulos.
"""
import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def get_ffmpeg_path() -> str:
    """
    Obtiene el path de ffmpeg (local o del sistema).
    
    Returns:
        str: Ruta al ejecutable de ffmpeg
    """
    # Primero verificar en tools/ffmpeg/
    local_ffmpeg = Path(__file__).parent.parent / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
    if local_ffmpeg.exists():
        return str(local_ffmpeg)
    return "ffmpeg"  # Usar del PATH


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


def get_output_path(input_path: str, suffix: str) -> str:
    """
    Genera ruta de salida con sufijo manteniendo la extensión original.
    
    Args:
        input_path: Ruta del archivo de entrada
        suffix: Sufijo a agregar (ej: '_output')
        
    Returns:
        str: Ruta con el sufijo agregado
    """
    p = Path(input_path)
    parent = p.parent
    stem = p.stem
    ext = p.suffix
    return str(parent / f"{stem}{suffix}{ext}")


def get_output_path_format(input_path: str, suffix: str, new_ext: str) -> str:
    """
    Genera ruta de salida con nuevo formato/extensión.
    
    Args:
        input_path: Ruta del archivo de entrada
        suffix: Sufijo a agregar
        new_ext: Nueva extensión (incluir el punto: '.mp3')
        
    Returns:
        str: Ruta con el nuevo formato
    """
    p = Path(input_path)
    parent = p.parent
    stem = p.stem
    return str(parent / f"{stem}{suffix}{new_ext}")


def ensure_directory(path: str) -> Path:
    """
    Asegura que un directorio exista, créalo si no existe.
    
    Args:
        path: Ruta al directorio
        
    Returns:
        Path: Objeto Path del directorio
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path