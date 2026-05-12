"""
core/image_utils.py — Core image utilities, shared between all image tool phases.
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import numpy as np

logger = logging.getLogger(__name__)

# === Library availability ===
PIL_AVAILABLE = True
try:
    from PIL import Image
except ImportError:
    PIL_AVAILABLE = False

CV2_AVAILABLE = True
try:
    import cv2
except ImportError:
    CV2_AVAILABLE = False

# === Supported formats ===
SUPPORTED_FORMATS = frozenset({'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'})


def _validate_format(file_path: str) -> bool:
    """Valida que el formato del archivo sea soportado."""
    ext = Path(file_path).suffix.lower()
    return ext in SUPPORTED_FORMATS


def _load_image(file_path: str) -> Dict[str, Any]:
    """
    Carga imagen usando OpenCV con fallback a PIL.

    Returns:
        operations_dict: {success, message, image_data, error}
    """
    path = Path(file_path)

    if not path.exists():
        return {
            'success': False,
            'message': '',
            'output_files': [],
            'image_data': None,
            'error': f"File not found: {file_path}"
        }

    if not _validate_format(str(path)):
        return {
            'success': False,
            'message': '',
            'output_files': [],
            'image_data': None,
            'error': f"Unsupported format: {path.suffix}"
        }

    # Try OpenCV first
    if CV2_AVAILABLE:
        image = cv2.imread(str(path))
        if image is not None:
            # OpenCV loads as BGR, convert to RGB for consistency
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return {
                'success': True,
                'message': 'Loaded with OpenCV',
                'output_files': [],
                'image_data': {
                    'array': image,
                    'shape': image.shape,
                    'dtype': str(image.dtype),
                    'format': path.suffix.lower(),
                    'mode': 'RGB'
                },
                'error': None
            }

    # Fallback to PIL
    if PIL_AVAILABLE:
        pil_image = Image.open(str(path))
        # Convert to RGB if needed
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        image = np.array(pil_image)
        return {
            'success': True,
            'message': 'Loaded with PIL fallback',
            'output_files': [],
            'image_data': {
                'array': image,
                'shape': image.shape,
                'dtype': str(image.dtype),
                'format': path.suffix.lower(),
                'mode': pil_image.mode
            },
            'error': None
        }

    return {
        'success': False,
        'message': '',
        'output_files': [],
        'image_data': None,
        'error': 'No image library available (cv2 or PIL)'
    }


def _save_image(
    image: np.ndarray,
    output_path: str,
    format: Optional[str] = None
) -> bool:
    """
    Guarda imagen a archivo usando OpenCV, fallback PIL.

    Args:
        image: numpy array (H, W, C) en formato RGB
        output_path: ruta de salida
        format: formato override (ej: 'png', 'jpg')

    Returns:
        True si exitoso, False si falló
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Determine format
    fmt = format or path.suffix.lower().lstrip('.')
    if fmt == 'jpg':
        fmt = 'jpeg'

    # Convert RGB to BGR for OpenCV
    if CV2_AVAILABLE and len(image.shape) == 3:
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    else:
        image_bgr = image

    if CV2_AVAILABLE:
        success = cv2.imwrite(str(path), image_bgr)
        if success:
            return True

    # Fallback PIL
    if PIL_AVAILABLE:
        pil_image = Image.fromarray(image.astype('uint8'))
        pil_image.save(str(path), format=fmt.upper())
        return True

    return False


def _image_to_dict(image: np.ndarray, format: str = 'png', mode: str = 'RGB') -> Dict[str, Any]:
    """Helper: numpy array -> image_data dict."""
    return {
        'array': image,
        'shape': image.shape,
        'dtype': str(image.dtype),
        'format': format,
        'mode': mode
    }