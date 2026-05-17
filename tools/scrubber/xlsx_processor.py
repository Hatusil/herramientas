"""
Processor para XLSX - limpieza de metadatos.
Separado de processor.py por SRP (máxima R0: clases <300 líneas).
"""
import os
import logging
from typing import Dict, Any

from core.utils import get_output_path
from core.metrics import Counter, Timer, increment

logger = logging.getLogger(__name__)

scrubber_operations_total = Counter('scrubber_operations_total')
scrubber_errors = Counter('scrubber_errors')


def get_xlsx_metadata(file_path: str) -> Dict[str, Any]:
    """Obtiene metadatos de un archivo XLSX."""
    if not os.path.exists(file_path):
        return {'success': False, 'error': 'Archivo no encontrado'}
    
    if not file_path.lower().endswith('.xlsx'):
        return {'success': False, 'error': 'No es un archivo XLSX'}
    
    try:
        import openpyxl
        
        wb = openpyxl.load_workbook(file_path)
        
        props = wb.properties
        
        info = {
            'title': props.title or '',
            'author': props.creator or '',
            'subject': props.subject or '',
            'keywords': props.keywords or '',
            'created': str(props.created) if props.created else '',
            'modified': str(props.modified) if props.modified else '',
            'lastModifiedBy': props.lastModifiedBy or '',
        }
        
        has_metadata = any(v for v in info.values())
        
        return {
            'success': True,
            'file_name': os.path.basename(file_path),
            'has_metadata': has_metadata,
            'metadata': info
        }
        
    except Exception as e:
        logger.error(f"Error leyendo metadatos XLSX: {e}")
        return {'success': False, 'error': str(e)}


def clean_xlsx(file_path: str) -> Dict[str, Any]:
    """Limpia metadatos de un archivo XLSX."""
    with Timer('scrubber.clean_xlsx'):
        if not os.path.exists(file_path):
            increment('scrubber_errors')
            return {'success': False, 'error': 'Archivo no encontrado', 'output_files': []}
        
        if not file_path.lower().endswith('.xlsx'):
            increment('scrubber_errors')
            return {'success': False, 'error': 'No es un archivo XLSX', 'output_files': []}
        
        try:
            import openpyxl
            
            wb = openpyxl.load_workbook(file_path)
            
            props = wb.properties
            props.title = ''
            props.creator = ''
            props.subject = ''
            props.keywords = ''
            props.lastModifiedBy = ''
            
            output_path = get_output_path(file_path, '_clean', _exists_ok=False)
            wb.save(output_path)
            
            increment('scrubber_operations_total')
            
            return {
                'success': True,
                'message': 'Metadatos XLSX eliminados',
                'output_files': [output_path],
                'error': None
            }
            
        except Exception as e:
            increment('scrubber_errors')
            logger.error(f"Error limpiando XLSX: {e}")
            return {'success': False, 'error': str(e), 'output_files': []}