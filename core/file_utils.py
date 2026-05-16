"""
Utilidades de archivos: validación y paths.
Cumple con máxima A1 (una sola responsabilidad).
"""
import os
from pathlib import Path
from typing import Optional


def get_output_path(input_path: str, suffix: str, _exists_ok: bool = True) -> str:
    """
    Genera ruta de salida con sufijo manteniendo la extensión original.
    Cumple con máxima A8 (idempotencia): evita sobrescribir archivos existentes.
    
    Args:
        input_path: Ruta del archivo de entrada
        suffix: Sufijo a agregar (ej: '_output')
        _exists_ok: Si True (default), permite sobrescribir. Si False, evita colisión.
        
    Returns:
        str: Ruta con el sufijo agregado
    """
    p = Path(input_path)
    parent = p.parent
    stem = p.stem
    ext = p.suffix
    output = parent / f"{stem}{suffix}{ext}"
    
    if not _exists_ok and output.exists():
        counter = 1
        while output.exists():
            output = parent / f"{stem}{suffix}_{counter}{ext}"
            counter += 1
    
    return str(output)


def get_output_path_format(input_path: str, suffix: str, new_ext: str, _exists_ok: bool = True) -> str:
    """
    Genera ruta de salida con nuevo formato/extensión.
    Cumple con máxima A8 (idempotencia): evita sobrescribir archivos existentes.
    
    Args:
        input_path: Ruta del archivo de entrada
        suffix: Sufijo a agregar
        new_ext: Nueva extensión (incluir el punto: '.mp3')
        _exists_ok: Si True (default), permite sobrescribir. Si False, evita colisión.
        
    Returns:
        str: Ruta con el nuevo formato
    """
    p = Path(input_path)
    parent = p.parent
    stem = p.stem
    output = parent / f"{stem}{suffix}{new_ext}"
    
    if not _exists_ok and output.exists():
        counter = 1
        while output.exists():
            output = parent / f"{stem}{suffix}_{counter}{new_ext}"
            counter += 1
    
    return str(output)


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


def validate_input_file(path) -> dict:
    """
    Valida que un archivo de entrada exista y sea legible.
    
    Args:
        path: Ruta al archivo (str o list)
        
    Returns:
        dict: {'valid': bool, 'error': str or None}
    """
    # Manejar lista
    if isinstance(path, (list, tuple)):
        path = path[0] if path else ""
    
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