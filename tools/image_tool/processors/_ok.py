"""Módulo base: flag cv2 + helpers."""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# === CV2 availability check ===
CV2_AVAILABLE = True
try:
    import cv2
except ImportError:
    CV2_AVAILABLE = False

# === Contadores de operación ===
from core.metrics import Counter
op_counter = Counter('image_operations')


def _ok(image, message: str) -> Dict[str, Any]:
    """Helper: construye operations_dict de éxito."""
    return {
        'success': True,
        'message': message,
        'output_files': [],
        'image_data': _image_to_dict(image),
        'error': None
    }


def _fail(error: str) -> Dict[str, Any]:
    """Helper: construye operations_dict de error."""
    return {
        'success': False,
        'message': '',
        'output_files': [],
        'image_data': None,
        'error': error
    }


def _image_to_dict(image) -> Dict[str, Any]:
    """Helper: array -> image_data dict."""
    return {
        'array': image,
        'shape': image.shape,
        'dtype': str(image.dtype),
        'format': 'png',
        'mode': 'RGB' if len(image.shape) == 3 else 'L'
    }