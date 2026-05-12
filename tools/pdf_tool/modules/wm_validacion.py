"""Validación de dependencias para watermark removal."""
from typing import List, Dict, Any

try:
    import fitz
except ImportError:
    fitz = None


def check_fitz() -> bool:
    """Verifica si Fitz está instalado."""
    return fitz is not None


def _is_watermark_region(x: float, y: float, width: float, height: float,
                         page_width: float, page_height: float) -> bool:
    """Determina si una región es probablemente un watermark."""
    area_ratio = (width * height) / (page_width * page_height)
    if area_ratio > 0.5:
        return False

    center_x = page_width / 2
    center_y = page_height / 2
    dist_to_center = ((x + width/2 - center_x)**2 +
                      (y + height/2 - center_y)**2) ** 0.5
    normalized_dist = dist_to_center / ((page_width**2 + page_height**2) ** 0.5)

    if normalized_dist < 0.3:
        return True

    margin = page_width * 0.1
    if x < margin or x > page_width - width - margin:
        if y < margin or y > page_height - height - margin:
            return True

    return False