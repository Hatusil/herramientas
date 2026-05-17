"""
Compression module - PDF compression utilities.
"""
import logging
import os
from typing import List, Dict, Any

from pypdf import PdfReader, PdfWriter

from core.utils import get_output_path
from tools.pdf_tool.utils import check_pypdf

logger = logging.getLogger(__name__)


def compress_pdf(files: List[str], level: str = 'medium') -> Dict[str, Any]:
    """
    Comprime un PDF para reducir su tamaño.
    
    Args:
        files: Lista de rutas de PDFs
        level: Nivel de compresión (low, medium, high)
        
    Returns:
        dict: Resultado de la operación
    """
    if not check_pypdf():
        return {'success': False, 'error': 'pypdf no está instalado', 'output_files': []}
    
    # pypdf tiene opciones básicas de compresión
    # La compresión real requiere técnicas adicionales
    
    output_files = []
    errors = []
    
    for file_path in files:
        if not os.path.exists(file_path):
            errors.append(f"Archivo no encontrado: {file_path}")
            continue
        
        try:
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            # Copiar todas las páginas al writer
            # pypdf aplica compresión básica al escribir
            for page in reader.pages:
                writer.add_page(page)
            
            output_path = get_output_path(file_path, '_compressed', _exists_ok=False)
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"PDF comprimido: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Comprimidos {len(output_files)}/{len(files)} PDFs",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }