"""
Módulo de watermarks (marcas de agua) para PDFs.
Proporciona funciones para agregar y eliminar watermarks de documentos PDF.
"""
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple

try:
    from pypdf import PdfReader, PdfWriter
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
    letter = None
    inch = None
    BytesIO = None

# Importar función compartida de core (máxima C2: Consistency)
from core.utils import get_output_path

logger = logging.getLogger(__name__)


# =============================================================================
# VALIDACIÓN
# =============================================================================

def check_pypdf() -> bool:
    """Verifica si pypdf está instalado."""
    return PdfReader is not None


def _create_text_watermark_pdf(text: str, page_size: Tuple, position: str = 'center', **options) -> bytes:
    """
    Crea un PDF temporal con el texto del watermark.
    
    Args:
        text: Texto del watermark
        page_size: Tupla (width, height) de la página
        position: Posición del watermark ('center', 'top-left', 'top-right', 'bottom-left', 'bottom-right', 'diagonal', 'custom')
        **options: font_size, color, opacity, rotation, position_x, position_y
        
    Returns:
        bytes: Contenido del PDF temporal
    """
    if canvas is None or BytesIO is None:
        raise ImportError("reportlab no está instalado")
    
    width, height = page_size
    packet = BytesIO()
    
    # Configuración
    font_size = options.get('font_size', 48)
    color = options.get('color', '#888888')
    opacity = options.get('opacity', 0.3)
    rotation = options.get('rotation', 45)
    position_x = options.get('position_x')
    position_y = options.get('position_y')
    
    # Convertir color hex a RGB
    r = int(color[1:3], 16) / 255
    g = int(color[3:5], 16) / 255
    b = int(color[5:7], 16) / 255
    
    c = canvas.Canvas(packet, pagesize=(width, height))
    c.setFont("Helvetica-Bold", font_size)
    c.setFillColorRGB(r, g, b, alpha=opacity)
    
    # Posicionar según el parámetro
    c.saveState()
    
    if position == 'custom' and position_x is not None and position_y is not None:
        # Posición personalizada exacta
        c.translate(position_x, position_y)
        c.rotate(rotation)
        c.drawCentredString(0, 0, text)
    elif position == 'center':
        c.translate(width / 2, height / 2)
        c.rotate(rotation)
        c.drawCentredString(0, 0, text)
    elif position == 'top-left':
        c.drawString(50, height - 50, text)
    elif position == 'top-right':
        text_width = c.stringWidth(text, "Helvetica-Bold", font_size)
        c.drawString(width - text_width - 50, height - 50, text)
    elif position == 'bottom-left':
        c.drawString(50, 50, text)
    elif position == 'bottom-right':
        text_width = c.stringWidth(text, "Helvetica-Bold", font_size)
        c.drawString(width - text_width - 50, 50, text)
    elif position == 'diagonal':
        c.translate(width / 2, height / 2)
        c.rotate(45)
        c.drawCentredString(0, 0, text)
    else:
        # Default: center
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
        **options: 
            - font_size: Tamaño de fuente (default: 48)
            - color: Color hex (default: '#888888')
            - opacity: Opacidad 0-1 (default: 0.3)
            - rotation: Rotación en grados (default: 45)
            - position: Posición - 'center', 'top-left', 'top-right', 'bottom-left', 'bottom-right', 'diagonal', 'custom' (default: 'center')
            - position_x: Coordenada X exacta (solo para position='custom')
            - position_y: Coordenada Y exacta (solo para position='custom')
        
    Returns:
        dict: Resultado de la operación
    """
    if not check_pypdf():
        return {'success': False, 'error': 'pypdf no está instalado', 'output_files': []}
    
    output_files = []
    errors = []
    
    # Extraer posición (nuevo parámetro)
    position = options.get('position', 'center')
    
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
                
                # Pasar posición al creador de watermark
                watermark_data = _create_text_watermark_pdf(
                    text, (page_width, page_height), position=position, **options
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
        **options: 
            - scale: Escala de la imagen (default: 0.5)
            - opacity: Opacidad 0-1 (default: 0.3)
            - position: Posición - 'center', 'top-left', 'top-right', 'bottom-left', 'bottom-right' (default: 'center')
            - position_x: Coordenada X exacta (solo para position='custom')
            - position_y: Coordenada Y exacta (solo para position='custom')
        
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
    position = options.get('position', 'center')
    position_x = options.get('position_x')
    position_y = options.get('position_y')
    
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
                
                # Calcular posición
                if position == 'custom' and position_x is not None and position_y is not None:
                    x = position_x
                    y = position_y
                elif position == 'center':
                    x = (page_width - scaled_width) / 2
                    y = (page_height - scaled_height) / 2
                elif position == 'top-left':
                    x = 50
                    y = page_height - scaled_height - 50
                elif position == 'top-right':
                    x = page_width - scaled_width - 50
                    y = page_height - scaled_height - 50
                elif position == 'bottom-left':
                    x = 50
                    y = 50
                elif position == 'bottom-right':
                    x = page_width - scaled_width - 50
                    y = 50
                else:
                    x = (page_width - scaled_width) / 2
                    y = (page_height - scaled_height) / 2
                
                # Crear watermark PDF temporal
                packet = BytesIO()
                c = canvas.Canvas(packet, pagesize=(page_width, page_height))
                c.setFillAlpha(opacity)
                c.drawImage(image_path, x, y, width=scaled_width, height=scaled_height)
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


def remove_annotations(files: List[str]) -> Dict[str, Any]:
    """
    Elimina anotaciones (/Annots) de PDFs.
    
    Esta función elimina únicamente las anotaciones PDF (notas, comentarios, enlaces, etc.)
    que están almacenadas en el diccionario /Annots de cada página.
    
    Nota: Esta función NO elimina watermarks que fueron mergeados como contenido
    visual en las páginas (como los creados por add_text_watermark).
    Para esos casos, las anotaciones ya forman parte del contenido de la página.
    
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
                # Eliminar anotaciones (/Annots)
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


def remove_watermarks(files: List[str]) -> Dict[str, Any]:
    """
    Alias para remove_annotations() - Mantenido por compatibilidad.
    
    Elimina anotaciones de PDFs. 
    Ver documentación de remove_annotations() para más detalles.
    
    Args:
        files: Lista de rutas de PDFs
        
    Returns:
        dict: Resultado de la operación
    """
    return remove_annotations(files)