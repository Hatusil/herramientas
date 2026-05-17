"""
Annotations module - Text annotations for PDFs.
"""
import logging
import os
from io import BytesIO
from typing import List, Dict, Any

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    NameObject,
    TextStringObject,
    NumberObject,
)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from core.utils import get_output_path
from tools.pdf_tool.utils import check_pypdf

logger = logging.getLogger(__name__)

# Check for reportlab
try:
    from reportlab.lib.pagesizes import letter
    canvas_available = True
except ImportError:
    canvas_available = False


def _create_text_annotation(text: str, x: float, y: float, width: float = 200,
                            height: float = 50, font_size: int = 12,
                            font_color: str = '000000',
                            bg_color: str = 'FFFF00') -> DictionaryObject:
    """Create a text annotation using PDF stream."""
    annotation = DictionaryObject()
    annotation[NameObject('/Type')] = NameObject('/Annot')
    annotation[NameObject('/Subtype')] = NameObject('/Text')
    annotation[NameObject('/Rect')] = ArrayObject([
        NumberObject(x), NumberObject(y),
        NumberObject(x + width), NumberObject(y + height)
    ])
    annotation[NameObject('/Contents')] = TextStringObject(text)
    annotation[NameObject('/F')] = NumberObject(4)  # Printable
    return annotation


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

    if not canvas_available:
        return {'success': False, 'error': 'reportlab no está instalado', 'output_files': []}
    
    output_files = []
    errors = []
    
    font_size = options.get('font_size', 12)
    font_color = options.get('font_color', '#000000')
    bg_color = options.get('background_color', '#FFFF00')
    
    # Convertir colores
    r = int(font_color[0:2], 16) / 255
    g = int(font_color[2:4], 16) / 255
    b = int(font_color[4:6], 16) / 255
    
    for file_path in files:
        if not os.path.exists(file_path):
            errors.append(f"Archivo no encontrado: {file_path}")
            continue
        
        try:
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            for i, page_obj in enumerate(reader.pages):
                if i == page:
                    # Crear annotation con overlay de texto
                    annotation = _create_text_annotation(
                        text, x, y, font_size=font_size,
                        font_color=font_color, bg_color=bg_color
                    )
                    page_obj[NameObject('/Annots')] = ArrayObject([annotation])
                
                writer.add_page(page_obj)
            
            output_path = get_output_path(file_path, '_annotated', _exists_ok=False)
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