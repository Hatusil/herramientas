"""
Módulo de conversión para PDFs.
Proporciona funciones para convertir entre PDFs e imágenes, y redactar áreas.
"""
import logging
import os
from pathlib import Path
from typing import List, Dict, Any

from core.utils import get_output_path, ensure_directory, check_pypdf

logger = logging.getLogger(__name__)


# =============================================================================
# VALIDACIÓN
# =============================================================================

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
    try:
        from PIL import Image
    except ImportError:
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


def pdf_to_images(files: List[str], output_dir: str = None, dpi: int = 200) -> Dict[str, Any]:
    """
    Exporta páginas de PDF como imágenes.
    
    Requiere pdf2image y poppler (ver_install.md para instalación).
    Si no están disponibles, retorna mensaje claro indicando la dependencia.
    
    Args:
        files: Lista de rutas de PDFs
        output_dir: Directorio de salida (default: mismo directorio que el PDF)
        dpi: Resolución de las imágenes (default: 200)
        
    Returns:
        dict: Resultado de la operación con lista de imágenes generadas
    """
    if not check_pypdf():
        return {'success': False, 'error': 'pypdf no instalado', 'output_files': []}
    
    try:
        from PIL import Image
    except ImportError:
        return {'success': False, 'error': 'Pillow no instalado', 'output_files': []}
    
    try:
        from pdf2image import convert_from_path
    except ImportError:
        return {
            'success': False,
            'error': 'pdf2image no está instalado. Instalar con: pip install pdf2image',
            'output_files': [],
            'info': 'También se requiere poppler. Ver instrucciones en docs/INSTALL.md'
        }
    
    output_files = []
    errors = []
    
    for file_path in files:
        if not os.path.exists(file_path):
            errors.append(f"Archivo no encontrado: {file_path}")
            continue
        
        try:
            # Directorio de salida
            if output_dir is None:
                output_dir = os.path.dirname(file_path)
            
            # Asegurar que existe el directorio
            ensure_directory(output_dir)
            
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Convertir PDF a imágenes
            images = convert_from_path(file_path, dpi=dpi)
            
            # Guardar cada página como imagen
            for i, image in enumerate(images):
                output_image_path = os.path.join(output_dir, f"{base_name}_page_{i+1:03d}.png")
                image.save(output_image_path, 'PNG')
                output_files.append(output_image_path)
                logger.info(f"Guardada página {i+1}: {output_image_path}")
            
            logger.info(f"PDF a imágenes completado: {file_path} -> {len(images)} imágenes")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Convertidas {len(output_files)} páginas a imágenes",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


def redact_area(files: List[str], page: int = 0, x: float = 100, y: float = 100,
                width: float = 100, height: float = 50, color: str = '#000000') -> Dict[str, Any]:
    """
    Crea un rectángulo de censura (redaction) en un área del PDF.
    
    El área especificada se cubre con un rectángulo de color sólido.
    Nota: Esta función dibuja un rectángulo sobre el contenido existente,
    pero NO elimina el contenido subyacente. Para censor completo,
    se requiere pdf_to_images() + procesamiento de imagen + images_to_pdf().
    
    Args:
        files: Lista de rutas de PDFs
        page: Número de página (0-indexed)
        x, y: Posición superior izquierda del área a censurar
        width, height: Dimensiones del área
        color: Color del rectángulo de censura (default: '#000000' negro)
        
    Returns:
        dict: Resultado de la operación
    """
    if not check_pypdf():
        return {'success': False, 'error': 'pypdf no instalado', 'output_files': []}
    
    try:
        from reportlab.pdfgen import canvas
    except ImportError:
        return {'success': False, 'error': 'reportlab no instalado', 'output_files': []}
    
    try:
        from io import BytesIO
    except ImportError:
        return {'success': False, 'error': 'io no disponible', 'output_files': []}
    
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        return {'success': False, 'error': 'pypdf no instalado', 'output_files': []}
    
    output_files = []
    errors = []
    
    # Convertir color hex a RGB
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
            
            for i, page_obj in enumerate(reader.pages):
                if i == page:
                    page_width = float(page_obj.mediabox.width)
                    page_height = float(page_obj.mediabox.height)
                    
                    # Crear overlay con rectángulo de censura
                    packet = BytesIO()
                    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
                    c.setFillColorRGB(r, g, b)
                    c.rect(x, page_height - y - height, width, height, fill=1, stroke=0)
                    c.save()
                    packet.seek(0)
                    
                    # Merge con la página
                    overlay_reader = PdfReader(packet)
                    overlay_page = overlay_reader.pages[0]
                    page_obj.merge_page(overlay_page)
                
                writer.add_page(page_obj)
            
            output_path = get_output_path(file_path, '_redacted')
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"Área censurada: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Área censurada en {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }