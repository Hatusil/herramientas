"""
Processor para DOCX - limpieza de metadatos.
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


def get_docx_metadata(file_path: str) -> Dict[str, Any]:
    """Obtiene metadatos de un archivo DOCX."""
    if not os.path.exists(file_path):
        return {'success': False, 'error': 'Archivo no encontrado'}
    
    if not file_path.lower().endswith('.docx'):
        return {'success': False, 'error': 'No es un archivo DOCX'}
    
    try:
        from docx import Document
        
        doc = Document(file_path)
        core_props = doc.core_properties
        
        info = {
            'title': core_props.title or '',
            'author': core_props.author or '',
            'subject': core_props.subject or '',
            'keywords': core_props.keywords or '',
            'created': str(core_props.created) if core_props.created else '',
            'modified': str(core_props.modified) if core_props.modified else '',
            'last_modified_by': core_props.last_modified_by or '',
            'revision': core_props.revision or 0,
        }
        
        has_metadata = any(v for k, v in info.items() if k != 'revision')
        
        return {
            'success': True,
            'file_name': os.path.basename(file_path),
            'has_metadata': has_metadata,
            'metadata': info
        }
        
    except Exception as e:
        logger.error(f"Error leyendo metadatos DOCX: {e}")
        return {'success': False, 'error': str(e)}


def clean_docx(file_path: str) -> Dict[str, Any]:
    """Limpia metadatos de un archivo DOCX."""
    with Timer('scrubber.clean_docx'):
        if not os.path.exists(file_path):
            increment('scrubber_errors')
            return {'success': False, 'error': 'Archivo no encontrado', 'output_files': []}
        
        if not file_path.lower().endswith('.docx'):
            increment('scrubber_errors')
            return {'success': False, 'error': 'No es un archivo DOCX', 'output_files': []}
        
        try:
            from docx import Document
            
            doc = Document(file_path)
            
            core_props = doc.core_properties
            core_props.title = ''
            core_props.author = ''
            core_props.subject = ''
            core_props.keywords = ''
            core_props.last_modified_by = ''
            core_props.comments = ''
            
            output_path = get_output_path(file_path, '_clean', _exists_ok=False)
            doc.save(output_path)
            
            increment('scrubber_operations_total')
            
            return {
                'success': True,
                'message': 'Metadatos DOCX eliminados',
                'output_files': [output_path],
                'error': None
            }
            
        except Exception as e:
            increment('scrubber_errors')
            logger.error(f"Error limpiando DOCX: {e}")
            return {'success': False, 'error': str(e), 'output_files': []}