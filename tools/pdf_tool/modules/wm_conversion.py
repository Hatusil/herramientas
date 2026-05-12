"""Conversión de PDFs a imágenes."""
import os
import logging
from io import BytesIO
from typing import List

from tools.pdf_tool.modules import wm_validacion as val

logger = logging.getLogger(__name__)


def pdf_to_images(pdf_path: str, dpi: int = 150) -> List:
    """Convierte un PDF a lista de imágenes (PIL Image o Pixmap)."""
    if not val.check_fitz():
        return []

    images = []
    try:
        doc = val.fitz.open(pdf_path)
        for page_num in range(len(doc)):
            pix = doc[page_num].get_pixmap(dpi=dpi)
            img_data = pix.tobytes("png")
            try:
                from PIL import Image
                images.append(Image.open(BytesIO(img_data)))
            except ImportError:
                images.append(pix)
        doc.close()
        logger.info(f"Convertido {pdf_path} a {len(images)} imágenes")
    except Exception as e:
        logger.error(f"Error convirtiendo PDF a imágenes: {e}")

    return images


def pdf_to_images_list(pdf_path: str, output_dir: str = None, dpi: int = 150) -> List[str]:
    """Convierte un PDF a imágenes y las guarda en disco."""
    if not val.check_fitz():
        return []

    image_paths = []
    try:
        if output_dir is None:
            output_dir = os.path.dirname(pdf_path)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        doc = val.fitz.open(pdf_path)
        for page_num in range(len(doc)):
            pix = doc[page_num].get_pixmap(dpi=dpi)
            img_name = f"{base_name}_page_{page_num + 1:03d}.png"
            img_path = os.path.join(output_dir, img_name)
            pix.save(img_path)
            image_paths.append(img_path)
        doc.close()
        logger.info(f"Guardadas {len(image_paths)} imágenes en {output_dir}")
    except Exception as e:
        logger.error(f"Error guardando imágenes: {e}")

    return image_paths