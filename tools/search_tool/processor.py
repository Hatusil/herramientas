"""
Processor: Funciones de búsqueda avanzada de archivos.

Arquitectura (SRP - máxima R0: clases <300 líneas):
- filters.py: Filtros de búsqueda (nombre, fecha, tamaño, extensión)
- content_extractors.py: Extracción de contenido (DOCX, PDF, XLSX, PPTX)
- exports.py: Exportación a CSV/TXT
- search_all.py: Búsqueda completa (funciones helper)
"""
# Re-export para compatibilidad hacia atrás
from tools.search_tool.filters import (
    search_by_name, search_by_date, filter_by_size, filter_by_extension
)
from tools.search_tool.content_extractors import (
    get_file_content, search_content,
    extract_docx_content, extract_pdf_content, 
    extract_xlsx_content, extract_pptx_content
)
from tools.search_tool.exports import export_to_csv, export_to_txt

# Importar search_all (mantiene las funciones helper internamente)
from tools.search_tool.search_all import search_all

__all__ = [
    'search_by_name', 'search_by_date', 'filter_by_size', 'filter_by_extension',
    'get_file_content', 'search_content',
    'export_to_csv', 'export_to_txt',
    'search_all',
]