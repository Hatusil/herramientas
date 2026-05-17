"""
Módulo de transformación de PDFs.

Arquitectura (SRP - máxima R0: clases <300 líneas):
- validation.py: Validaciones de páginas
- transform_operations.py: Operaciones (rotate, reorder, merge, extract)
"""
# Re-export para compatibilidad hacia atrás
from tools.pdf_tool.modules.validation import (
    validate_page_number, validate_page_range, validate_new_order
)
from tools.pdf_tool.modules.transform_operations import (
    rotate_pages, reorder_pages, merge_pdfs, extract_pages,
    extract_page, extract_range, reorder_pages_advanced
)

__all__ = [
    'validate_page_number', 'validate_page_range', 'validate_new_order',
    'rotate_pages', 'reorder_pages', 'merge_pdfs', 'extract_pages',
    'extract_page', 'extract_range', 'reorder_pages_advanced',
]