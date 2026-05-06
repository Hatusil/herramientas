"""
Utilidades para PDF usando pypdf.
Cumple con máxima A1 (una sola responsabilidad).
"""
import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# pypdf - Lazy import para evitar error si no está instalado
try:
    from pypdf import PdfReader, PdfWriter
    _pypdf_available = True
except ImportError:
    _pypdf_available = False
    PdfReader = None
    PdfWriter = None


# Import from file_utils para mantener compatibilidad
from core.file_utils import get_output_path


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