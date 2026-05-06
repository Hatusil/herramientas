"""
Módulo de información de PDFs.
Proporciona funciones para obtener metadatos y información de archivos PDF.
"""
import logging
import os
from typing import Dict, Any

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

# Importar función compartida de core (máxima C2: Consistency)
from core.utils import check_pypdf

logger = logging.getLogger(__name__)


def get_pdf_info(file_path: str) -> Dict[str, Any]:
    """
    Obtiene información y metadatos de un PDF.
    
    Args:
        file_path: Ruta al archivo PDF
        
    Returns:
        dict: Información del PDF
    """
    if not check_pypdf():
        return {'success': False, 'error': 'pypdf no está instalado'}
    
    if not os.path.exists(file_path):
        return {'success': False, 'error': 'Archivo no encontrado'}
    
    try:
        reader = PdfReader(file_path)
        
        # Verificar si está encriptado
        is_encrypted = reader.is_encrypted
        
        # Metadatos
        metadata = reader.metadata or {}
        info = {
            'success': True,
            'file_name': os.path.basename(file_path),
            'file_size': os.path.getsize(file_path),
            'num_pages': len(reader.pages),
            'is_encrypted': is_encrypted,
            'title': metadata.get('/Title', ''),
            'author': metadata.get('/Author', ''),
            'subject': metadata.get('/Subject', ''),
            'creator': metadata.get('/Creator', ''),
            'producer': metadata.get('/Producer', ''),
            'creation_date': metadata.get('/CreationDate', ''),
            'modification_date': metadata.get('/ModDate', ''),
        }
        
        # Info de cada página
        pages_info = []
        for i, page in enumerate(reader.pages):
            pages_info.append({
                'page_num': i + 1,
                'rotation': page.get('/Rotate', 0),
                'mediabox': str(page.mediabox) if page.mediabox else None,
            })
        
        info['pages'] = pages_info
        
        return info
        
    except Exception as e:
        logger.error(f"Error obteniendo info de PDF: {e}")
        return {'success': False, 'error': str(e)}


def check_pdf_encrypted(file_path: str) -> bool:
    """
    Verifica si un PDF está encriptado.
    
    Args:
        file_path: Ruta al archivo PDF
        
    Returns:
        bool: True si está encriptado
    """
    try:
        reader = PdfReader(file_path)
        return reader.is_encrypted
    except Exception:
        return False