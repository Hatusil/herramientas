"""
Processor: Funciones de procesamiento de PDFs usando pypdf, Pillow y reportlab.

Este módulo DELega a los módulos especializados en tools/pdf_tool/modules/
siguiendo la máxima C2: NO duplicar código, usar módulos existentes.

API expuesta para compatibilidad hacia atrás - las funciones llaman a los módulos.
"""
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Importar funciones compartidas de core (máxima C2: Consistency)
from core.utils import get_output_path, validate_input_file, validate_file_extension, validate_file_size
from core.metrics import Timer, Counter, increment  # Máxima A12: Observabilidad

# Importar módulos especializados (delegación - máxima C2: no duplicar)
from tools.pdf_tool.modules import (
    # Info
    get_pdf_info as _get_pdf_info_module,
    check_pdf_encrypted as _check_pdf_encrypted_module,
    # Annotations
    add_text_annotation as _add_text_annotation_module,
    # Page Numbers
    add_page_numbers as _add_page_numbers_module,
    # Watermarks
    add_text_watermark as _add_text_watermark_module,
    add_image_watermark as _add_image_watermark_module,
    remove_watermarks as _remove_watermarks_module,
    remove_annotations as _remove_annotations_module,
    # Transform
    rotate_pages as _rotate_pages_module,
    reorder_pages as _reorder_pages_module,
    merge_pdfs as _merge_pdfs_module,
    extract_pages as _extract_pages_module,
    extract_page as _extract_page_module,
    extract_range as _extract_range_module,
    reorder_pages_advanced as _reorder_pages_advanced_module,
    validate_page_number as _validate_page_number_module,
    validate_page_range as _validate_page_range_module,
    validate_new_order as _validate_new_order_module,
    # Security
    encrypt_pdf as _encrypt_pdf_module,
    decrypt_pdf as _decrypt_pdf_module,
    # Conversion
    images_to_pdf as _images_to_pdf_module,
    pdf_to_images as _pdf_to_images_module,
    redact_area as _redact_area_module,
    # Compression
    compress_pdf as _compress_pdf_module,
    # Watermark removal (Fitz)
    remove_watermark as _remove_watermark_fitz_module,
    check_fitz as _check_fitz_module,
    # Pipeline
    execute_pipeline_operations as _execute_pipeline_operations_module,
)

# Constantes y utilitarias delegadas a utils.py
from tools.pdf_tool.utils import (
    _validate_pdf_input, _validate_encryption_password, check_pypdf,
    PDF_EXTENSIONS, MAX_PDF_SIZE_MB
)

logger = logging.getLogger(__name__)

# get_output_path() importado desde core.utils (máxima #3: Consistency)


# =============================================================================
# INFO - Delegado a modules/info.py (máxima C2: no duplicar código)
# =============================================================================

def get_pdf_info(file_path: str) -> Dict[str, Any]:
    """Obtiene información y metadatos de un PDF."""
    with Timer('pdf_tool.get_pdf_info'):
        increment('pdf_tool.get_pdf_info_calls')
        return _get_pdf_info_module(file_path)


def check_pdf_encrypted(file_path: str) -> bool:
    """Verifica si un PDF está encriptado."""
    return _check_pdf_encrypted_module(file_path)


# =============================================================================
# WATERMARKS - Delegado a modules/watermarks.py (máxima C2: no duplicar código)
# =============================================================================

def add_text_watermark(files: List[str], text: str, **options) -> Dict[str, Any]:
    """Agrega marca de agua de texto a PDFs."""
    return _add_text_watermark_module(files, text, **options)


def add_image_watermark(files: List[str], image_path: str, **options) -> Dict[str, Any]:
    """Agrega marca de agua de imagen a PDFs."""
    return _add_image_watermark_module(files, image_path, **options)


def remove_watermarks(files: List[str], **options) -> Dict[str, Any]:
    """Elimina marcas de agua de PDFs (visual/annotations/auto)."""
    return _remove_watermarks_module(files, **options)


# =============================================================================
# EDICIÓN - ANOTACIONES - Delegado a modules/annotations.py
# =============================================================================

def add_text_annotation(files: List[str], text: str, page: int = 0,
                        x: float = 100, y: float = 100, **options) -> Dict[str, Any]:
    """Agrega una anotación de texto a una página del PDF."""
    return _add_text_annotation_module(files, text, page, x, y, **options)


# =============================================================================
# TRANSFORMACIONES - Delegado a modules/transform.py (máxima C2: no duplicar código)
# =============================================================================

def rotate_pages(files: List[str], degrees: int = 90, pages: List[int] = None) -> Dict[str, Any]:
    """Rota páginas del PDF."""
    with Timer('pdf_tool.rotate_pages'):
        increment('pdf_tool.rotate_pages_calls')
        return _rotate_pages_module(files, degrees=degrees, pages=pages)


def reorder_pages(files: List[str], new_order: List[int]) -> Dict[str, Any]:
    """Reordena las páginas de un PDF."""
    return _reorder_pages_module(files, new_order)


def merge_pdfs(files: List[str], output_path: str = None) -> Dict[str, Any]:
    """Combina múltiples PDFs en uno."""
    with Timer('pdf_tool.merge_pdfs'):
        increment('pdf_tool.merge_pdfs_calls')
        return _merge_pdfs_module(files, output_path=output_path)


def extract_pages(files: List[str], pages: List[int]) -> Dict[str, Any]:
    """Extrae páginas específicas de un PDF."""
    return _extract_pages_module(files, pages)


def extract_range(files: List[str], start: int, end: int) -> Dict[str, Any]:
    """Extrae un rango de páginas de un PDF."""
    return _extract_range_module(files, start, end)


def extract_page(files: List[str], page_number: int) -> Dict[str, Any]:
    """Extrae una página específica de un PDF."""
    return _extract_page_module(files, page_number)


def reorder_pages_advanced(files: List[str], new_order: List[int]) -> Dict[str, Any]:
    """Reordena las páginas de un PDF con validación mejorada."""
    return _reorder_pages_advanced_module(files, new_order)


# =============================================================================
# NÚMEROS DE PÁGINA
# =============================================================================

def add_page_numbers(files: List[str], **options) -> Dict[str, Any]:
    """Agrega números de página al PDF."""
    return _add_page_numbers_module(files, **options)


# =============================================================================
# CONVERSIÓN - Delegado a modules/conversion.py (máxima C2: no duplicar código)
# =============================================================================

def images_to_pdf(image_paths: List[str], output_path: str = None) -> Dict[str, Any]:
    """
    Convierte imágenes a PDF.
    
    Args:
        image_paths: Lista de rutas de imágenes
        output_path: Ruta de salida
        
    Returns:
        dict: Resultado de la operación
    """
    return _images_to_pdf_module(image_paths, output_path=output_path)


def pdf_to_images(files: List[str], output_dir: str = None) -> Dict[str, Any]:
    """
    Exporta páginas de PDF como imágenes.
    
    Args:
        files: Lista de rutas de PDFs
        output_dir: Directorio de salida
        
    Returns:
        dict: Resultado de la operación
    """
    return _pdf_to_images_module(files, output_dir=output_dir)


def redact_area(files: List[str], page: int = 0, x: float = 100, y: float = 100,
                width: float = 100, height: float = 50) -> Dict[str, Any]:
    """
    Censa un área del PDF.
    
    Args:
        files: Lista de rutas de PDFs
        page: Número de página (0-indexed)
        x, y: Posición
        width, height: Dimensiones
        
    Returns:
        dict: Resultado de la operación
    """
    with Timer('pdf_tool.redact_area'):
        increment('pdf_tool.redact_area_calls')
        return _redact_area_module(files, page=page, x=x, y=y, width=width, height=height)


# =============================================================================
# SEGURIDAD - Delegado a modules/security.py (máxima C2: no duplicar código)
# =============================================================================

def encrypt_pdf(files: List[str], password: str) -> Dict[str, Any]:
    """Bloquea un PDF con contraseña."""
    return _encrypt_pdf_module(files, password)


def decrypt_pdf(files: List[str], password: str) -> Dict[str, Any]:
    """Desbloquea un PDF con contraseña."""
    return _decrypt_pdf_module(files, password)


# =============================================================================
# OPTIMIZACIÓN - Delegado a modules/compression.py
# =============================================================================

def compress_pdf(files: List[str], level: str = 'medium') -> Dict[str, Any]:
    """Comprime un PDF para reducir su tamaño."""
    return _compress_pdf_module(files, level)


def clean_metadata(files: List[str]) -> Dict[str, Any]:
    """Limpia metadatos de un PDF (delegado a core.utils)."""
    from core.utils import clean_metadata as _clean_metadata
    return _clean_metadata(files)


# =============================================================================
# PIPELINE INTEGRATION - Delegado a modules/pipeline.py (máxima C2: no duplicar código)
# =============================================================================

def execute_pipeline(files: List[str], operations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Ejecuta múltiples operaciones en pipeline."""
    if not files:
        return {'success': False, 'error': 'No se proporcionó archivo de entrada'}
    if not operations:
        return {'success': False, 'error': 'No hay operaciones para ejecutar'}
    return _execute_pipeline_operations_module(files[0], operations)


# =============================================================================
# ASYNC VERSIONS - Movido a async_processors.py (máxima R0: <300 líneas)
# =============================================================================