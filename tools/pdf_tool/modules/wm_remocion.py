"""Remoción de watermarks de páginas PDF."""
import logging
from typing import List, Dict, Any

from tools.pdf_tool.modules import wm_validacion as val

logger = logging.getLogger(__name__)


def remove_watermark_from_page(page, watermark_regions: List[Dict[str, Any]]) -> bool:
    """Remueve las regiones de watermark de una página."""
    if not val.check_fitz():
        return False

    try:
        for region in watermark_regions:
            rect = val.fitz.Rect(
                region['x'], region['y'],
                region['x'] + region['width'],
                region['y'] + region['height']
            )
            page.add_redact_annot(rect, fill=(1, 1, 1))
        page.apply_redactions(images=val.fitz.PDF_REdaction_IMAGE_REMOVE)
        return True
    except Exception as e:
        logger.warning(f"Error removiendo watermark: {e}")
        return False