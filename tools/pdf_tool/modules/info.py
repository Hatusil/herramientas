"""
Módulo de información de PDFs.
Proporciona funciones para obtener metadatos y información de archivos PDF.
"""
import logging
from typing import Dict, Any

from core.pdf_utils import get_pdf_info as _get_pdf_info_core

logger = logging.getLogger(__name__)


def get_pdf_info(file_path: str) -> Dict[str, Any]:
    """Re-export from core (máxima C2: Consistency)."""
    return _get_pdf_info_core(file_path)


def check_pdf_encrypted(file_path: str) -> bool:
    """Verifica si un PDF está encriptado."""
    result = get_pdf_info(file_path)
    return result.get('is_encrypted', False)