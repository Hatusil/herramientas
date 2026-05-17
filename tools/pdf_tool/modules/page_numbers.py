"""
Page numbers module - Add page numbers to PDFs.
"""
import logging
import os
from io import BytesIO
from typing import List, Dict, Any

from pypdf import PdfReader, PdfWriter
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


def add_page_numbers(files: List[str], **options) -> Dict[str, Any]:
    """
    Agrega números de página al PDF.
    
    Args:
        files: Lista de rutas de PDFs
        **options: position (header/footer), format, start, font_size, color
        
    Returns:
        dict: Resultado de la operación
    """
    if not check_pypdf() or not canvas_available:
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
            
            output_path = get_output_path(file_path, '_numbered', _exists_ok=False)
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