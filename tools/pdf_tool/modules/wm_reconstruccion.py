"""Reconstrucción de PDFs desde imágenes."""
import os
import logging
from io import BytesIO
from typing import List, Any

from tools.pdf_tool.modules import wm_validacion as val

logger = logging.getLogger(__name__)


def images_to_pdf(images: List[Any], output_path: str) -> dict:
    """Reconstruye un PDF desde una lista de imágenes."""
    if not val.check_fitz():
        return _images_to_pdf_pillow(images, output_path)

    try:
        doc = val.fitz.open()
        for img in images:
            img_data = None
            if hasattr(img, 'size'):
                width, height = img.size
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                buf = BytesIO()
                img.save(buf, format='PNG')
                img_data = buf.getvalue()
            elif hasattr(img, 'tobytes'):
                width, height = img.width, img.height
                img_data = img.tobytes("png")
            elif isinstance(img, str) and os.path.exists(img):
                pix = val.fitz.Pixmap(img)
                width, height = pix.width, pix.height
                img_data = pix.tobytes("png")

            if img_data:
                page = doc.new_page(width=width, height=height)
                doc.insert_image(page.rect, stream=img_data)

        doc.save(output_path)
        doc.close()
        logger.info(f"Reconstruido PDF: {output_path}")
        return {
            'success': True, 'message': f"PDF con {len(images)} páginas",
            'output_files': [output_path], 'error': None
        }
    except Exception as e:
        logger.error(f"Error reconstruyendo PDF: {e}")
        return {'success': False, 'error': str(e), 'output_files': []}


def _images_to_pdf_pillow(images: List[Any], output_path: str) -> dict:
    """Fallback a Pillow para reconstruir PDF."""
    try:
        from PIL import Image
    except ImportError:
        return {'success': False, 'error': 'Pillow no instalado', 'output_files': []}

    try:
        pil_images = []
        for img in images:
            if isinstance(img, str) and os.path.exists(img):
                pil_img = Image.open(img)
            elif hasattr(img, 'convert'):
                pil_img = img
            else:
                continue
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')
            pil_images.append(pil_img)

        if pil_images:
            pil_images[0].save(output_path, save_all=True, append_images=pil_images[1:])
            return {
                'success': True,
                'message': f"PDF reconstruido ({len(pil_images)} páginas - fallback)",
                'output_files': [output_path], 'error': None
            }
        return {'success': False, 'error': 'Sin imágenes válidas', 'output_files': []}
    except Exception as e:
        return {'success': False, 'error': str(e), 'output_files': []}