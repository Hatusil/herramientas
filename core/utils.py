"""
Utilidades comunes del proyecto.
Funciones helper que pueden ser usadas por múltiples módulos.
"""
import functools
import logging
import os
import platform
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


# ============================================================================
# STOP WORDS - Palabras comunes a filtrar en procesamiento de texto
# ============================================================================
STOP_WORDS = {
    'es': {'el', 'la', 'los', 'las', 'un', 'una', 'unas', 'unos', 'de', 'del', 'al', 'a', 
           'en', 'con', 'por', 'para', 'sin', 'sobre', 'entre', 'y', 'e', 'o', 'u', 'que',
           'como', 'más', 'pero', 'ni', 'si', 'no', 'sí', 'él', 'ella', 'ellos', 'ellas',
           'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos', 'esas', 'esto',
           'mi', 'tu', 'su', 'mis', 'tus', 'sus', 'nuestro', 'nuestra', 'nosotros',
           'ser', 'estar', 'hay', 'fue', 'era', 'son', 'es', 'está', 'han', 'había',
           'lo', 'al', 'todo', 'toda', 'todos', 'todas', 'poco', 'poca', 'pocos', 'pocas',
           'mucho', 'mucha', 'muchos', 'muchas', 'otro', 'otra', 'otros', 'otras', 'mismo', 'misma'},
    'en': {'the', 'a', 'an', 'and', 'or', 'but', 'if', 'in', 'to', 'of', 'for', 'on', 
           'with', 'at', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been',
           'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
           'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used',
           'it', 'he', 'she', 'they', 'we', 'you', 'i', 'me', 'him', 'her', 'us', 'them',
           'this', 'that', 'these', 'those', 'what', 'which', 'who', 'whom', 'whose',
           'my', 'your', 'his', 'its', 'our', 'their',
           'not', 'no', 'yes', 'all', 'any', 'some', 'such', 'nor', 'only',
           'very', 'just', 'also', 'now', 'then', 'there', 'here', 'when', 'where',
           'each', 'every', 'both', 'few', 'more', 'most', 'other',
           'so', 'than', 'too', 'even', 'still', 'already', 'yet'}
}


def clean_text(text: str, remove_stopwords: bool = True, languages: List[str] = ['es', 'en'], exclude_words: Optional[List[str]] = None) -> str:
    """
    Limpia el texto: minúsculas, remove signos, stopwords.
    
    Args:
        text: Texto a limpiar
        remove_stopwords: Si True,移除 stopwords según idiomas
        languages: Lista de idiomas para stopwords (es, en)
        exclude_words: Lista de palabras adicionales a excluir
        
    Returns:
        str: Texto limpio
    """
    # Minúsculas
    text = text.lower()
    
    # Remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    
    # Normalizar espacios
    text = re.sub(r'\s+', ' ', text).strip()
    
    if remove_stopwords:
        stop = set()
        for lang in languages:
            stop.update(STOP_WORDS.get(lang, set()))
        words = text.split()
        text = ' '.join(w for w in words if w not in stop and len(w) > 2)
    
    # Excluir palabras custom
    if exclude_words:
        exclude_set = set(w.lower() for w in exclude_words)
        words = text.split()
        text = ' '.join(w for w in words if w not in exclude_set)
    
    return text


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


# =============================================================================
# VALIDACIÓN DE ARCHIVOS
# =============================================================================

def validate_input_file(path: str) -> dict:
    """
    Valida que un archivo de entrada exista y sea legible.
    
    Args:
        path: Ruta al archivo
        
    Returns:
        dict: {'valid': bool, 'error': str or None}
    """
    if not path:
        return {'valid': False, 'error': 'No path provided'}
    if not os.path.exists(path):
        return {'valid': False, 'error': 'File does not exist'}
    if not os.path.isfile(path):
        return {'valid': False, 'error': 'Not a file'}
    if not os.access(path, os.R_OK):
        return {'valid': False, 'error': 'File not readable'}
    return {'valid': True}


def validate_file_extension(path: str, allowed_extensions: list) -> dict:
    """
    Valida que el archivo tenga una extensión permitida.
    
    Args:
        path: Ruta al archivo
        allowed_extensions: Lista de extensiones permitidas (ej: ['.pdf', '.txt'])
        
    Returns:
        dict: {'valid': bool, 'error': str or None}
    """
    if not path:
        return {'valid': False, 'error': 'No path provided'}
    
    ext = os.path.splitext(path)[1].lower()
    allowed = [e.lower() for e in allowed_extensions]
    
    if ext not in allowed:
        return {'valid': False, 'error': f'Extensión {ext} no permitida. Permitidas: {", ".join(allowed)}'}
    
    return {'valid': True}


def validate_file_size(path: str, max_size_mb: float = 100) -> dict:
    """
    Valida que el archivo no exceda un tamaño máximo.
    
    Args:
        path: Ruta al archivo
        max_size_mb: Tamaño máximo en MB (default: 100)
        
    Returns:
        dict: {'valid': bool, 'error': str or None, 'size_mb': float}
    """
    if not path or not os.path.exists(path):
        return {'valid': True}  # Handled by validate_input_file
    
    size_bytes = os.path.getsize(path)
    size_mb = size_bytes / (1024 * 1024)
    
    if size_mb > max_size_mb:
        return {'valid': False, 'error': f'Archivo demasiado grande ({size_mb:.1f}MB). Máximo: {max_size_mb}MB', 'size_mb': round(size_mb, 2)}
    
    return {'valid': True, 'size_mb': round(size_mb, 2)}


def format_error_message(error: Exception, context: str = "") -> str:
    """
    Formatea un error con contexto opcional.
    
    Args:
        error: Excepción occurring
        context: Contexto adicional (ej: nombre de función, operación)
        
    Returns:
        str: Mensaje de error formateado
    """
    error_type = type(error).__name__
    error_msg = str(error)
    if context:
        return f"{context}: {error_type} - {error_msg}"
    return f"{error_type}: {error_msg}"


# =============================================================================
# PDF UTILITIES - pypdf helpers
# =============================================================================

# pypdf - Lazy import para evitar error si no está instalado
try:
    from pypdf import PdfReader, PdfWriter
    _pypdf_available = True
except ImportError:
    _pypdf_available = False
    PdfReader = None
    PdfWriter = None


def check_pypdf() -> bool:
    """Verifica si pypdf está instalado."""
    return _pypdf_available


def clean_metadata(files: List[str]) -> Dict[str, Any]:
    """
    Limpia metadatos de un PDF.
    
    Args:
        files: Lista de rutas de PDFs
        
    Returns:
        dict: Resultado de la operación
    """
    if not check_pypdf():
        return {'success': False, 'error': 'pypdf no está instalado', 'output_files': []}
    
    output_files = []
    errors = []
    
    for file_path in files:
        if not os.path.exists(file_path):
            errors.append(f"Archivo no encontrado: {file_path}")
            continue
        
        try:
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            # Copiar páginas sin metadatos
            for page in reader.pages:
                writer.add_page(page)
            
            # Eliminar metadatos completamente
            writer.metadata = None
            
            output_path = get_output_path(file_path, '_cleaned')
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"Metadatos limpiados: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Metadatos limpiados en {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }