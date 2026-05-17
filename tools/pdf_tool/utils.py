"""
Utilidades para pdf_tool: validación, helpers.
Separado de processor.py por SRP (máxima R0: clases <300 líneas).
"""
from typing import Any, Dict

from core.utils import validate_input_file, validate_file_extension, validate_file_size

PDF_EXTENSIONS = ('.pdf',)
MAX_PDF_SIZE_MB = 100


def _validate_pdf_input(file_path: str) -> Dict[str, Any]:
    """Valida archivo de entrada para operaciones PDF."""
    check = validate_input_file(file_path)
    if not check['valid']:
        return check
    check = validate_file_extension(file_path, PDF_EXTENSIONS)
    if not check['valid']:
        return check
    check = validate_file_size(file_path, MAX_PDF_SIZE_MB)
    if not check['valid']:
        return check
    return {'valid': True}


def _validate_encryption_password(password: str) -> bool:
    """Valida la contraseña para encriptación de PDF."""
    if not password or len(password) < 4 or len(password) > 64:
        return False
    return True


def check_pypdf() -> bool:
    """Verifica si pypdf está instalado."""
    try:
        from pypdf import PdfReader
        return PdfReader is not None
    except ImportError:
        return False