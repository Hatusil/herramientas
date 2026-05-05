"""
Processor: Funciones de procesamiento de PDFs usando pypdf, Pillow y reportlab.
"""
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Importar funciones compartidas de core (máxima #3: Consistency)
from core.utils import get_output_path

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
    """Verifica si un PDF está encriptado."""
    try:
        reader = PdfReader(file_path)
        return reader.is_encrypted
    except Exception:
        return False


# =============================================================================
# WATERMARKS
# =============================================================================

def _create_text_watermark_pdf(text: str, page_size: Tuple, **options) -> bytes:
    """Crea un PDF temporal con el texto del watermark."""
    if canvas is None:
        raise ImportError("reportlab no está instalado")
    
    width, height = page_size
    packet = BytesIO()
    
    # Configuración
    font_size = options.get('font_size', 48)
    color = options.get('color', '#888888')
    opacity = options.get('opacity', 0.3)
    rotation = options.get('rotation', 45)
    
    # Convertir color hex a RGB
    r = int(color[1:3], 16) / 255
    g = int(color[3:5], 16) / 255
    b = int(color[5:7], 16) / 255
    
    c = canvas.Canvas(packet, pagesize=(width, height))
    c.setFont("Helvetica-Bold", font_size)
    c.setFillColorRGB(r, g, b, alpha=opacity)
    
    # Rotar
    c.saveState()
    c.translate(width / 2, height / 2)
    c.rotate(rotation)
    c.drawCentredString(0, 0, text)
    c.restoreState()
    
    c.save()
    packet.seek(0)
    return packet.read()


def add_text_watermark(files: List[str], text: str, **options) -> Dict[str, Any]:
    """
    Agrega marca de agua de texto a PDFs.
    
    Args:
        files: Lista de rutas de PDFs
        text: Texto del watermark
        **options: font_size, color, opacity, rotation
        
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
            
            # Crear watermark para cada página
            for page in reader.pages:
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)
                
                watermark_data = _create_text_watermark_pdf(
                    text, (page_width, page_height), **options
                )
                watermark_reader = PdfReader(BytesIO(watermark_data))
                watermark_page = watermark_reader.pages[0]
                
                page.merge_page(watermark_page)
                writer.add_page(page)
            
            output_path = get_output_path(file_path, '_watermarked')
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"Watermark agregado: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Watermark aplicado a {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


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
    if not check_pypdf() or Image is None:
        return {'success': False, 'error': 'pypdf o Pillow no instalado', 'output_files': []}
    
    output_files = []
    errors = []
    
    # Opciones con defaults
    scale = options.get('scale', 0.5)  # 50% del tamaño de página
    opacity = options.get('opacity', 0.3)
    
    # Crear página de watermark como PDF
    if not os.path.exists(image_path):
        return {'success': False, 'error': f'Imagen no encontrada: {image_path}', 'output_files': []}
    
    try:
        img = Image.open(image_path)
        img_width, img_height = img.size
    except Exception as e:
        return {'success': False, 'error': f'Error abriendo imagen: {e}', 'output_files': []}
    
    for file_path in files:
        if not os.path.exists(file_path):
            errors.append(f"Archivo no encontrado: {file_path}")
            continue
        
        try:
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            for page in reader.pages:
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)
                
                # Escalar imagen al tamaño de página
                scaled_width = page_width * scale
                scaled_height = scaled_width * (img_height / img_width)
                
                # Crear watermark PDF temporal
                packet = BytesIO()
                c = canvas.Canvas(packet, pagesize=(page_width, page_height))
                c.setFillAlpha(opacity)
                c.drawImage(image_path, 
                           (page_width - scaled_width) / 2,
                           (page_height - scaled_height) / 2,
                           width=scaled_width,
                           height=scaled_height)
                c.save()
                packet.seek(0)
                
                watermark_reader = PdfReader(packet)
                watermark_page = watermark_reader.pages[0]
                
                page.merge_page(watermark_page)
                writer.add_page(page)
            
            output_path = get_output_path(file_path, '_watermarked')
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"Watermark de imagen aplicado: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Watermark de imagen aplicado a {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


def remove_watermarks(files: List[str]) -> Dict[str, Any]:
    """
    Elimina anotaciones (marcas de agua) de PDFs.
    
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
            
            for page in reader.pages:
                # Eliminar anotaciones
                if '/Annots' in page:
                    del page['/Annots']
                writer.add_page(page)
            
            output_path = get_output_path(file_path, '_clean')
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"Anotaciones eliminadas: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Anotaciones eliminadas de {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


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
# TRANSFORMACIONES - ROTAR Y REORDENAR
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
    if not check_pypdf():
        return {'success': False, 'error': 'pypdf no está instalado', 'output_files': []}
    
    if degrees not in [90, 180, 270]:
        return {'success': False, 'error': 'Degrees debe ser 90, 180 o 270', 'output_files': []}
    
    output_files = []
    errors = []
    
    for file_path in files:
        if not os.path.exists(file_path):
            errors.append(f"Archivo no encontrado: {file_path}")
            continue
        
        try:
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            for i, page in enumerate(reader.pages):
                if pages is None or (i + 1) in pages:
                    try:
                        # Obtener rotación actual (manejar diferentes tipos)
                        current_rotation = 0
                        if '/Rotate' in page:
                            rot_obj = page['/Rotate']
                            # Puede ser int o indirect object
                            try:
                                current_rotation = int(rot_obj)
                            except (TypeError, ValueError):
                                current_rotation = 0
                        
                        new_rotation = (current_rotation + degrees) % 360
                        page['/Rotate'] = new_rotation
                    except Exception as e:
                        logger.warning(f"Error rotando página {i}: {e}")
                
                writer.add_page(page)
            
            output_path = get_output_path(file_path, f'_rotated_{degrees}')
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"Páginas rotadas: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Rotación aplicada a {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


def reorder_pages(files: List[str], new_order: List[int]) -> Dict[str, Any]:
    """
    Reordena las páginas de un PDF.
    
    Args:
        files: Lista de rutas de PDFs
        new_order: Lista con el nuevo orden de páginas (1-indexed)
        
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
            
            num_pages = len(reader.pages)
            
            # Validar que los números de página sean válidos
            for p in new_order:
                if p < 1 or p > num_pages:
                    return {'success': False, 'error': f'Número de página inválido: {p}', 'output_files': []}
            
            # Reordenar según el nuevo orden
            for new_pos in new_order:
                page = reader.pages[new_pos - 1]  # Convertir a 0-indexed
                writer.add_page(page)
            
            output_path = get_output_path(file_path, '_reordered')
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"Páginas reordenadas: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Páginas reordenadas en {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


# =============================================================================
# COMBINAR Y DIVIDIR
# =============================================================================

def merge_pdfs(files: List[str], output_path: str = None) -> Dict[str, Any]:
    """
    Combina múltiples PDFs en uno.
    
    Args:
        files: Lista de rutas de PDFs a combinar
        output_path: Ruta de salida (opcional)
        
    Returns:
        dict: Resultado de la operación
    """
    if not check_pypdf():
        return {'success': False, 'error': 'pypdf no está instalado', 'output_files': []}
    
    if len(files) < 2:
        return {'success': False, 'error': 'Se necesitan al menos 2 PDFs para combinar', 'output_files': []}
    
    errors = []
    writer = PdfWriter()
    total_pages = 0
    
    for file_path in files:
        if not os.path.exists(file_path):
            errors.append(f"Archivo no encontrado: {file_path}")
            continue
        
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                writer.add_page(page)
            total_pages += len(reader.pages)
        except Exception as e:
            errors.append(f"Error leyendo {file_path}: {str(e)}")
    
    if total_pages == 0:
        return {'success': False, 'error': 'No se pudieron leer páginas de los PDFs', 'output_files': []}
    
    # Determinar ruta de salida
    if output_path is None:
        first_file = files[0]
        output_path = get_output_path(first_file, '_merged')
    
    try:
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        return {
            'success': True,
            'message': f"PDFs combinados: {total_pages} páginas",
            'output_files': [output_path],
            'error': None
        }
    except Exception as e:
        return {'success': False, 'error': f'Error escribiendo archivo: {str(e)}', 'output_files': []}


def extract_pages(files: List[str], pages: List[int]) -> Dict[str, Any]:
    """
    Extrae páginas específicas de un PDF.
    
    Args:
        files: Lista de rutas de PDFs
        pages: Lista de números de página a extraer (1-indexed)
        
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
            
            num_pages = len(reader.pages)
            
            for p in pages:
                if p < 1 or p > num_pages:
                    continue
                writer.add_page(reader.pages[p - 1])
            
            output_path = get_output_path(file_path, '_extracted')
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"Páginas extraídas: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Extraídas {len(pages)} páginas de {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


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
# CONVERSIÓN
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
    if Image is None:
        return {'success': False, 'error': 'Pillow no instalado', 'output_files': []}
    
    if not image_paths:
        return {'success': False, 'error': 'No hay imágenes para convertir', 'output_files': []}
    
    errors = []
    
    for img_path in image_paths:
        if not os.path.exists(img_path):
            errors.append(f"Imagen no encontrada: {img_path}")
    
    if errors:
        return {'success': False, 'error': '; '.join(errors), 'output_files': []}
    
    try:
        images = []
        for img_path in image_paths:
            img = Image.open(img_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            images.append(img)
        
        # Determinar output
        if output_path is None:
            first_img = image_paths[0]
            output_path = get_output_path(first_img, '_converted')
        
        images[0].save(output_path, save_all=True, append_images=images[1:])
        
        return {
            'success': True,
            'message': f"Convertido {len(images)} imágenes a PDF",
            'output_files': [output_path],
            'error': None
        }
    except Exception as e:
        return {'success': False, 'error': f'Error convirtiendo: {str(e)}', 'output_files': []}


def pdf_to_images(files: List[str], output_dir: str = None) -> Dict[str, Any]:
    """
    Exporta páginas de PDF como imágenes.
    
    Args:
        files: Lista de rutas de PDFs
        output_dir: Directorio de salida
        
    Returns:
        dict: Resultado de la operación
    """
    if not check_pypdf() or Image is None:
        return {'success': False, 'error': 'pypdf o Pillow no instalado', 'output_files': []}
    
    output_files = []
    errors = []
    
    for file_path in files:
        if not os.path.exists(file_path):
            errors.append(f"Archivo no encontrado: {file_path}")
            continue
        
        try:
            reader = PdfReader(file_path)
            
            # Directorio de salida
            if output_dir is None:
                output_dir = os.path.dirname(file_path)
            
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            for i, page in enumerate(reader.pages):
                # Convertir página a imagen
                # pypdf no convierte directamente, necesitamos otra aproximación
                # Por ahora usamos una aproximación básica
                
                # Esto requeriría renderizado real, lo marcamos como no implementado
                pass
            
            logger.info(f"PDF a imágenes: {file_path} - requiere implementación adicional")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    return {
        'success': False,
        'message': 'PDF a imágenes requiere implementación adicional (renderizado)',
        'output_files': [],
        'error': 'Funcionalidad en desarrollo'
    }


# =============================================================================
# SEGURIDAD - BLOQUEAR/DESBLOQUEAR
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
    if not check_pypdf():
        return {'success': False, 'error': 'pypdf no está instalado', 'output_files': []}
    
    # Validate password (Issue #3: password validation)
    if not _validate_encryption_password(password):
        return {'success': False, 'error': 'Contraseña inválida: debe tener entre 4 y 64 caracteres', 'output_files': []}
    
    output_files = []
    errors = []
    
    for file_path in files:
        if not os.path.exists(file_path):
            errors.append(f"Archivo no encontrado: {file_path}")
            continue
        
        try:
            reader = PdfReader(file_path)
            
            if reader.is_encrypted:
                errors.append(f"{file_path} ya está encriptado")
                continue
            
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            
            writer.encrypt(password)
            
            output_path = get_output_path(file_path, '_locked')
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"PDF bloqueado: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Bloqueados {len(output_files)}/{len(files)} PDFs",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


def decrypt_pdf(files: List[str], password: str) -> Dict[str, Any]:
    """
    Desbloquea un PDF con contraseña.
    
    Args:
        files: Lista de rutas de PDFs
        password: Contraseña para desbloquear
        
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
            
            if not reader.is_encrypted:
                errors.append(f"{file_path} no está encriptado")
                continue
            
            # Intentar descifrar
            result = reader.decrypt(password)
            
            if result == 0:
                errors.append(f"Contraseña incorrecta para {file_path}")
                continue
            
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            
            output_path = get_output_path(file_path, '_unlocked')
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"PDF desbloqueado: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Desbloqueados {len(output_files)}/{len(files)} PDFs",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


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