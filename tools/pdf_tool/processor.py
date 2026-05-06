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

# Importar funciones compartidas de core (máxima #3: Consistency)
from core.utils import get_output_path, validate_input_file, validate_file_extension, validate_file_size

# Importar módulos especializados (delegación - máxima C2: no duplicar)
from tools.pdf_tool.modules import (
    # Info
    get_pdf_info as _get_pdf_info_module,
    check_pdf_encrypted as _check_pdf_encrypted_module,
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
    # Watermark removal (Fitz)
    remove_watermark as _remove_watermark_fitz_module,
    check_fitz as _check_fitz_module,
    # Pipeline
    execute_pipeline_operations as _execute_pipeline_operations_module,
)

# Constantes de validación
PDF_EXTENSIONS = ['.pdf']
MAX_PDF_SIZE_MB = 100  # 100MB max for PDF files


def _validate_pdf_input(file_path: str) -> Dict[str, Any]:
    """Valida archivo de entrada para operaciones PDF."""
    check = validate_input_file(file_path)
    if not check['valid']:
        return check
    check = validate_file_extension(file_path, PDF_EXTENSIONS)
    if not check['valid']:
        return check
    check = validate_file_size(file_path, MAX_PDF_SIZE_MB)
    if not check['valid']:
        return check
    return {'valid': True}

try:
    from pypdf import PdfReader, PdfWriter, PageObject
    from pypdf.generic import RectangleObject
    from pypdf.annotations import FreeText, Highlight
except ImportError:
    PdfReader = None
    PdfWriter = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from io import BytesIO
except ImportError:
    canvas = None

logger = logging.getLogger(__name__)


# =============================================================================
# VALIDACIÓN
# =============================================================================

def _validate_encryption_password(password: str) -> bool:
    """
    Valida la contraseña para encriptación de PDF.
    
    Args:
        password: Contraseña a validar
        
    Returns:
        bool: True si la contraseña es válida
    """
    if not password or len(password) < 4 or len(password) > 64:
        return False
    return True


# =============================================================================
# UTILIDADES
# =============================================================================

def check_pypdf() -> bool:
    """Verifica si pypdf está instalado."""
    return PdfReader is not None


# get_output_path() importado desde core.utils (máxima #3: Consistency)


# =============================================================================
# INFO - Delegado a modules/info.py (máxima C2: no duplicar código)
# =============================================================================

def get_pdf_info(file_path: str) -> Dict[str, Any]:
    """
    Obtiene información y metadatos de un PDF.
    
    Args:
        file_path: Ruta al archivo PDF
        
    Returns:
        dict: Información del PDF
    """
    return _get_pdf_info_module(file_path)


def check_pdf_encrypted(file_path: str) -> bool:
    """Verifica si un PDF está encriptado."""
    return _check_pdf_encrypted_module(file_path)


# =============================================================================
# WATERMARKS - Delegado a modules/watermarks.py (máxima C2: no duplicar código)
# =============================================================================

def add_text_watermark(files: List[str], text: str, **options) -> Dict[str, Any]:
    """
    Agrega marca de agua de texto a PDFs.
    
    Args:
        files: Lista de rutas de PDFs
        text: Texto del watermark
        **options: font_size, color, opacity, rotation, position
        
    Returns:
        dict: Resultado de la operación
    """
    return _add_text_watermark_module(files, text, **options)


def add_image_watermark(files: List[str], image_path: str, **options) -> Dict[str, Any]:
    """
    Agrega marca de agua de imagen a PDFs.
    
    Args:
        files: Lista de rutas de PDFs
        image_path: Ruta a la imagen
        **options: scale, opacity, position
        
    Returns:
        dict: Resultado de la operación
    """
    return _add_image_watermark_module(files, image_path, **options)


def remove_watermarks(files: List[str], **options) -> Dict[str, Any]:
    """
    Elimina marcas de agua de PDFs.
    
    Usa el módulo watermark_removal.py con Fitz para eliminación visual
    (watermarks mergeados en el contenido). Si Fitz no está disponible,
    usa pypdf para eliminar solo anotaciones.
    
    Args:
        files: Lista de rutas de PDFs
        **options:
            - mode: 'visual' | 'annotations' | 'auto' (default: 'auto')
            - detection_mode: 'auto' | 'manual' (para modo visual)
            - manual_region: dict con x, y, width, height (para modo manual)
            
    Returns:
        dict: Resultado de la operación
    """
    mode = options.get('mode', 'auto')
    
    # Mode 'auto': intentar visual primero, luego fallback a annotations
    # Mode 'visual': solo eliminación visual con Fitz
    # Mode 'annotations': solo eliminación de anotaciones con pypdf
    
    if mode == 'auto' or mode == 'visual':
        # Intentar eliminación visual con Fitz
        if _check_fitz_module():
            detection_mode = options.get('detection_mode', 'auto')
            manual_region = options.get('manual_region', None)
            
            result = _remove_watermark_fitz_module(
                files,
                detection_mode=detection_mode,
                preserve_layout=True,
                manual_region=manual_region
            )
            
            if result.get('success'):
                logger.info("Eliminación visual de watermark completada")
                return result
            
            # Si falló pero es modo 'auto', continuar al fallback
            if mode == 'visual':
                return result
    
    # Fallback a eliminación de anotaciones con pypdf
    return _remove_annotations_module(files)


# =============================================================================
# EDICIÓN - ANOTACIONES
# =============================================================================

def add_text_annotation(files: List[str], text: str, page: int = 0, 
                        x: float = 100, y: float = 100, **options) -> Dict[str, Any]:
    """
    Agrega una anotación de texto a una página del PDF.
    
    Args:
        files: Lista de rutas de PDFs
        text: Texto de la anotación
        page: Número de página (0-indexed)
        x, y: Posición
        **options: font, font_size, color, background_color
        
    Returns:
        dict: Resultado de la operación
    """
    if not check_pypdf():
        return {'success': False, 'error': 'pypdf no está instalado', 'output_files': []}
    
    output_files = []
    errors = []
    
    font = options.get('font', 'Helvetica')
    font_size = options.get('font_size', '12pt')
    font_color = options.get('font_color', '000000')
    bg_color = options.get('background_color', 'FFFF00')
    
    for file_path in files:
        if not os.path.exists(file_path):
            errors.append(f"Archivo no encontrado: {file_path}")
            continue
        
        try:
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            for i, page_obj in enumerate(reader.pages):
                if i == page:
                    # Crear anotación de texto libre
                    annotation = FreeText(
                        text=text,
                        rect=(x, y, x + 200, y + 50),
                        font=font,
                        font_size=font_size,
                        font_color=font_color,
                        background_color=bg_color,
                    )
                    annotation.flags = 4  # Printable
                    writer.add_annotation(page_number=i, annotation=annotation)
                
                writer.add_page(page_obj)
            
            output_path = get_output_path(file_path, '_annotated')
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"Anotación agregada: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Anotación agregada a {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


def redact_area(files: List[str], page: int = 0, x: float = 100, y: float = 100,
                width: float = 100, height: float = 50) -> Dict[str, Any]:
    """
    Censa un área del PDF (la pinta de negro/blanco).
    
    Args:
        files: Lista de rutas de PDFs
        page: Número de página (0-indexed)
        x, y: Posición superior izquierda
        width, height: Dimensiones del área
        
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
            
            for i, page_obj in enumerate(reader.pages):
                if i == page:
                    # Crear rectángulo de censurado
                    # Usamos una anotación de cuadrado como overlay
                    from pypdf.annotations import Square
                    annotation = Square(
                        rect=(x, y, x + width, y + height),
                        # No hay color de fondo directo, usamos Border
                    )
                    # Simplemente dibujar un rectángulo negro
                    # En pypdf esto es limitado, usamosapproach alternativo
                    
                writer.add_page(page_obj)
            
            output_path = get_output_path(file_path, '_redacted')
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"Área censurada: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    # Función no implementada - requiere biblioteca de renderizado
    # Volver a esto después
    return {
        'success': False,
        'message': 'Funcionalidad no implementada',
        'output_files': [],
        'error': 'PDF a imágenes requiere implementación adicional (renderizado con pdf2image o similar)'
    }


# =============================================================================
# TRANSFORMACIONES - Delegado a modules/transform.py (máxima C2: no duplicar código)
# =============================================================================

def rotate_pages(files: List[str], degrees: int = 90, pages: List[int] = None) -> Dict[str, Any]:
    """
    Rota páginas del PDF.
    
    Args:
        files: Lista de rutas de PDFs
        degrees: Grados de rotación (90, 180, 270)
        pages: Lista de números de página a rotar (None = todas)
        
    Returns:
        dict: Resultado de la operación
    """
    return _rotate_pages_module(files, degrees=degrees, pages=pages)


def reorder_pages(files: List[str], new_order: List[int]) -> Dict[str, Any]:
    """
    Reordena las páginas de un PDF.
    
    Args:
        files: Lista de rutas de PDFs
        new_order: Lista con el nuevo orden de páginas (1-indexed)
        
    Returns:
        dict: Resultado de la operación
    """
    return _reorder_pages_module(files, new_order)


def merge_pdfs(files: List[str], output_path: str = None) -> Dict[str, Any]:
    """
    Combina múltiples PDFs en uno.
    
    Args:
        files: Lista de rutas de PDFs a combinar
        output_path: Ruta de salida (opcional)
        
    Returns:
        dict: Resultado de la operación
    """
    return _merge_pdfs_module(files, output_path=output_path)


def extract_pages(files: List[str], pages: List[int]) -> Dict[str, Any]:
    """
    Extrae páginas específicas de un PDF.
    
    Args:
        files: Lista de rutas de PDFs
        pages: Lista de números de página a extraer (1-indexed)
        
    Returns:
        dict: Resultado de la operación
    """
    return _extract_pages_module(files, pages)


def extract_range(files: List[str], start: int, end: int) -> Dict[str, Any]:
    """
    Extrae un rango de páginas de un PDF.
    
    Args:
        files: Lista de rutas de PDFs
        start: Página inicial (1-indexed)
        end: Página final (1-indexed)
        
    Returns:
        dict: Resultado de la operación
    """
    return _extract_range_module(files, start, end)


def extract_page(files: List[str], page_number: int) -> Dict[str, Any]:
    """
    Extrae una página específica de un PDF.
    
    Args:
        files: Lista de rutas de PDFs
        page_number: Número de página a extraer (1-indexed)
        
    Returns:
        dict: Resultado de la operación
    """
    return _extract_page_module(files, page_number)


def reorder_pages_advanced(files: List[str], new_order: List[int]) -> Dict[str, Any]:
    """
    Reordena las páginas de un PDF con validación mejorada.
    
    Args:
        files: Lista de rutas de PDFs
        new_order: Lista con el nuevo orden de páginas (1-indexed)
        
    Returns:
        dict: Resultado de la operación
    """
    return _reorder_pages_advanced_module(files, new_order)


# =============================================================================
# NÚMEROS DE PÁGINA
# =============================================================================

def add_page_numbers(files: List[str], **options) -> Dict[str, Any]:
    """
    Agrega números de página al PDF.
    
    Args:
        files: Lista de rutas de PDFs
        **options: position (header/footer), format, start, font_size, color
        
    Returns:
        dict: Resultado de la operación
    """
    if not check_pypdf() or canvas is None:
        return {'success': False, 'error': 'pypdf o reportlab no instalado', 'output_files': []}
    
    output_files = []
    errors = []
    
    position = options.get('position', 'footer')  # header o footer
    format_str = options.get('format', 'Página {n} de {total}')  # formato con {n} y {total}
    start = options.get('start', 1)  # número inicial
    font_size = options.get('font_size', 12)
    color = options.get('color', '#000000')
    
    # Convertir color
    r = int(color[1:3], 16) / 255
    g = int(color[3:5], 16) / 255
    b = int(color[5:7], 16) / 255
    
    for file_path in files:
        if not os.path.exists(file_path):
            errors.append(f"Archivo no encontrado: {file_path}")
            continue
        
        try:
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            total_pages = len(reader.pages)
            
            for i, page in enumerate(reader.pages):
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)
                
                # Crear número de página
                page_num = start + i
                text = format_str.replace('{n}', str(page_num)).replace('{total}', str(total_pages))
                
                # Crear overlay
                packet = BytesIO()
                c = canvas.Canvas(packet, pagesize=(page_width, page_height))
                c.setFont("Helvetica", font_size)
                c.setFillColorRGB(r, g, b)
                
                # Posición
                text_width = c.stringWidth(text, "Helvetica", font_size)
                x = (page_width - text_width) / 2
                y = 20 if position == 'footer' else page_height - 30
                
                c.drawString(x, y, text)
                c.save()
                packet.seek(0)
                
                # Merge con página
                overlay_reader = PdfReader(packet)
                overlay_page = overlay_reader.pages[0]
                page.merge_page(overlay_page)
                
                writer.add_page(page)
            
            output_path = get_output_path(file_path, '_numbered')
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"Números de página agregados: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Números de página agregados a {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


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
    return _redact_area_module(files, page=page, x=x, y=y, width=width, height=height)


# =============================================================================
# SEGURIDAD - Delegado a modules/security.py (máxima C2: no duplicar código)
# =============================================================================

def encrypt_pdf(files: List[str], password: str) -> Dict[str, Any]:
    """
    Bloquea un PDF con contraseña.
    
    Args:
        files: Lista de rutas de PDFs
        password: Contraseña para bloquear
        
    Returns:
        dict: Resultado de la operación
    """
    return _encrypt_pdf_module(files, password)


def decrypt_pdf(files: List[str], password: str) -> Dict[str, Any]:
    """
    Desbloquea un PDF con contraseña.
    
    Args:
        files: Lista de rutas de PDFs
        password: Contraseña para desbloquear
        
    Returns:
        dict: Resultado de la operación
    """
    return _decrypt_pdf_module(files, password)


# =============================================================================
# OPTIMIZACIÓN
# =============================================================================

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
            
            output_path = get_output_path(file_path, '_compressed')
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


def clean_metadata(files: List[str]) -> Dict[str, Any]:
    """
    Limpia metadatos de un PDF.
    
    Args:
        files: Lista de rutas de PDFs
        
    Returns:
        dict: Resultado de la operación
        
    .. deprecated::
        Usar directamente `core.utils.clean_metadata` en su lugar.
    """
    # Alias para backward compatibility - délega a core.utils
    from core.utils import clean_metadata as _clean_metadata
    return _clean_metadata(files)


# =============================================================================
# PIPELINE INTEGRATION - Delegado a modules/pipeline.py (máxima C2: no duplicar código)
# =============================================================================

def execute_pipeline(files: List[str], operations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Ejecuta múltiples operaciones en pipeline.
    
    Args:
        files: Lista de archivos PDF (solo se usa el primero)
        operations: Lista de operaciones con 'type' y 'params'
        
    Returns:
        dict: Resultado de la ejecución
    """
    if not files:
        return {'success': False, 'error': 'No se proporcionó archivo de entrada'}
    
    if not operations:
        return {'success': False, 'error': 'No hay operaciones para ejecutar'}
    
    input_file = files[0]
    
    return _execute_pipeline_operations_module(input_file, operations)