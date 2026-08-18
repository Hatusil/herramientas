import os
from pathlib import Path
from typing import List, Dict, Any, Tuple

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    PdfReader = None
    PdfWriter = None

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    from io import BytesIO
except ImportError:
    canvas = None
    inch = None
    BytesIO = None

from core.utils import get_output_path, check_pypdf


def _create_text_watermark_pdf(text: str, page_size: Tuple, position: str = 'center', **options) -> bytes:
    if canvas is None or BytesIO is None:
        raise ImportError("reportlab no está instalado")

    width, height = page_size
    packet = BytesIO()

    font_size = options.get('font_size', 48)
    color = options.get('color', '#888888')
    opacity = options.get('opacity', 0.3)
    rotation = options.get('rotation', 45)
    position_x = options.get('position_x')
    position_y = options.get('position_y')

    r = int(color[1:3], 16) / 255
    g = int(color[3:5], 16) / 255
    b = int(color[5:7], 16) / 255

    c = canvas.Canvas(packet, pagesize=(width, height))
    c.setFont("Helvetica-Bold", font_size)
    c.setFillColorRGB(r, g, b, alpha=opacity)

    c.saveState()

    if position == 'custom' and position_x is not None and position_y is not None:
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
        c.translate(width / 2, height / 2)
        c.rotate(rotation)
        c.drawCentredString(0, 0, text)

    c.restoreState()
    c.save()
    packet.seek(0)
    return packet.read()


def add_text_watermark(files: List[str], text: str, **options) -> Dict[str, Any]:
    if not check_pypdf():
        return {'success': False, 'error': 'pypdf no está instalado', 'output_files': []}

    output_files = []
    errors = []
    position = options.get('position', 'center')

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
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")

    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Watermark aplicado a {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }
