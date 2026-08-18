import os
from pathlib import Path
from typing import List, Dict, Any

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
    from io import BytesIO
except ImportError:
    canvas = None
    BytesIO = None

from core.utils import get_output_path, check_pypdf


def add_image_watermark(files: List[str], image_path: str, **options) -> Dict[str, Any]:
    if not check_pypdf() or Image is None:
        return {'success': False, 'error': 'pypdf o Pillow no instalado', 'output_files': []}

    output_files = []
    errors = []

    scale = options.get('scale', 0.5)
    opacity = options.get('opacity', 0.3)
    position = options.get('position', 'center')
    position_x = options.get('position_x')
    position_y = options.get('position_y')

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

                scaled_width = page_width * scale
                scaled_height = scaled_width * (img_height / img_width)

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
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")

    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Watermark de imagen aplicado a {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }
