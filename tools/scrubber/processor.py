"""
Processor: Funciones para limpiar metadatos de archivos.

Arquitectura (SRP - máxima R0: clases <300 líneas):
- image_processor.py: Imágenes (EXIF)
- docx_processor.py: Documentos DOCX
- xlsx_processor.py: Hojas de cálculo XLSX
"""
# Re-export para compatibilidad hacia atrás
from tools.scrubber.image_processor import get_image_metadata, clean_image_metadata
from tools.scrubber.docx_processor import get_docx_metadata, clean_docx
from tools.scrubber.xlsx_processor import get_xlsx_metadata, clean_xlsx

__all__ = [
    'get_image_metadata', 'clean_image_metadata',
    'get_docx_metadata', 'clean_docx',
    'get_xlsx_metadata', 'clean_xlsx',
]

# Alias para backward compatibility
MAX_SCRUB_SIZE_MB = 2000