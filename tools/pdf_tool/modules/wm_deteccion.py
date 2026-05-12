"""Detección de watermarks en páginas PDF."""
import logging
from typing import List, Dict, Any

from tools.pdf_tool.modules import wm_validacion as val

logger = logging.getLogger(__name__)


def detect_watermarks(page) -> List[Dict[str, Any]]:
    """Detecta contenido de watermark en una página PDF."""
    if not val.check_fitz():
        return []

    watermark_regions = []
    page_width = page.rect.width
    page_height = page.rect.height

    try:
        for img in page.get_images(full=True):
            xref = img[0]
            for rect in page.get_image_rects(xref):
                if val._is_watermark_region(rect.x0, rect.y0, rect.width, rect.height,
                                           page_width, page_height):
                    watermark_regions.append({
                        'x': rect.x0, 'y': rect.y0,
                        'width': rect.width, 'height': rect.height,
                        'type': 'image', 'text': ''
                    })

        blocks = page.get_text("dict", flags=val.fitz.TEXT_PRESERVE_WHITESPACE)
        for block in blocks.get('blocks', []):
            if block.get('type') == 0:
                bbox = block.get('bbox', [0, 0, 0, 0])
                x, y, w, h = bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]
                if val._is_watermark_region(x, y, w, h, page_width, page_height):
                    text = block.get('text', '').strip()
                    if text:
                        watermark_regions.append({
                            'x': x, 'y': y, 'width': w, 'height': h,
                            'type': 'text', 'text': text[:100]
                        })
    except Exception as e:
        logger.warning(f"Error detectando watermarks: {e}")

    return watermark_regions


def detect_watermarks_auto(pdf_document) -> List[Dict[str, Any]]:
    """Detecta automáticamente watermarks en todo el documento."""
    if not val.check_fitz():
        return []

    all_regions = []
    for page_num in range(len(pdf_document)):
        for region in detect_watermarks(pdf_document[page_num]):
            region['page'] = page_num
            all_regions.append(region)

    similar_groups = {}
    for region in all_regions:
        key = (round(region['width'], 1), round(region['height'], 1))
        if key not in similar_groups:
            similar_groups[key] = []
        similar_groups[key].append(region)

    detected_watermarks = []
    threshold = len(pdf_document) * 0.5
    for regions in similar_groups.values():
        if len(regions) >= threshold:
            detected_watermarks.append(regions[0])

    return detected_watermarks


def detect_watermarks_manual(page, x: float, y: float,
                              width: float, height: float) -> List[Dict[str, Any]]:
    """Define manualmente una región de watermark."""
    return [{
        'x': x, 'y': y, 'width': width, 'height': height,
        'type': 'manual', 'text': ''
    }]