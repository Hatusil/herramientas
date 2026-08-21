"""Phase 7: Análisis Avanzado."""
from pathlib import Path
from typing import Dict, Any

import numpy as np

from core.image_utils import _load_image

from ._ok import _ok, _fail, _image_to_dict, CV2_AVAILABLE
from core.constants import OUTPUT_DIR


def _template_match(image: np.ndarray, template_path: str) -> Dict[str, Any]:
    """Template matching (async)."""
    try:
        if not Path(template_path).exists():
            return _fail(f"Template not found: {template_path}")

        if not CV2_AVAILABLE:
            return _fail("OpenCV required for template matching")

        import cv2

        template = _load_image(template_path)
        if not template['success']:
            return _fail(f"Cannot load template: {template.get('error')}")

        template_img = template['image_data']['array']
        if len(template_img.shape) == 3:
            template_gray = cv2.cvtColor(template_img, cv2.COLOR_RGB2GRAY)
        else:
            template_gray = template_img

        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image

        result = cv2.matchTemplate(gray, template_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        h, w = template_gray.shape
        output = image.copy()
        if len(output.shape) == 2:
            output = cv2.cvtColor(output, cv2.COLOR_GRAY2RGB)
        cv2.rectangle(output, max_loc, (max_loc[0] + w, max_loc[1] + h), (0, 255, 0), 3)

        output_path = OUTPUT_DIR / 'template_match.png'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), cv2.cvtColor(output, cv2.COLOR_RGB2BGR))

        return {
            'success': True,
            'message': f"Best match at ({max_loc[0]}, {max_loc[1]}) with confidence {max_val:.3f}",
            'output_files': [str(output_path)],
            'image_data': _image_to_dict(output),
            'error': None
        }
    except Exception as e:
        return _fail(f"Template matching failed: {e}")


def _pseudocolor(image: np.ndarray, colormap: str = 'jet') -> Dict[str, Any]:
    """Asigna pseudocolores a imagen en escala de grises."""
    try:
        if len(image.shape) == 3:
            gray = np.dot(image[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
        else:
            gray = image

        if CV2_AVAILABLE:
            import cv2
            colormap_dict = {
                'jet': cv2.COLORMAP_JET,
                'ocean': cv2.COLORMAP_OCEAN,
                'summer': cv2.COLORMAP_SUMMER,
                'winter': cv2.COLORMAP_WINTER,
                'autumn': cv2.COLORMAP_AUTUMN,
                'bone': cv2.COLORMAP_BONE,
                'cool': cv2.COLORMAP_COOL,
                'copper': cv2.COLORMAP_COPPER,
                'flag': cv2.COLORMAP_FLAG,
                'hsv': cv2.COLORMAP_HSV,
                'inferno': cv2.COLORMAP_INFERNO,
                'magma': cv2.COLORMAP_MAGMA,
                'plasma': cv2.COLORMAP_PLASMA,
                'turbo': cv2.COLORMAP_TURBO,
                'viridis': cv2.COLORMAP_VIRIDIS,
            }
            if colormap.lower() not in colormap_dict:
                return _fail(f"Unknown colormap: {colormap}")
            colored = cv2.applyColorMap(gray, colormap_dict[colormap.lower()])
        else:
            normalized = gray.astype(float) / 255.0
            colored = np.zeros((gray.shape[0], gray.shape[1], 3), dtype=np.uint8)
            colored[..., 0] = (normalized * 255).astype(np.uint8)
            colored[..., 1] = ((1 - normalized) * 127).astype(np.uint8)
            colored[..., 2] = ((1 - normalized) * 255).astype(np.uint8)

        return _ok(colored, f"Pseudocolor applied ({colormap})")
    except Exception as e:
        return _fail(f"Pseudocolor failed: {e}")


def _haar_detect(image: np.ndarray, cascade_path: str) -> Dict[str, Any]:
    """Detección con Haar cascades (async)."""
    try:
        if not CV2_AVAILABLE:
            return _fail("OpenCV required for Haar detection")

        import cv2

        cascade_file = Path(cascade_path)
        if not cascade_file.exists():
            opencv_cascades = {
                'face': cv2.data.haarcascades + 'haarcascade_frontalface_default.xml',
                'eye': cv2.data.haarcascades + 'haarcascade_eye.xml',
                'smile': cv2.data.haarcascades + 'haarcascade_smile.xml',
            }
            if cascade_path.lower() in opencv_cascades:
                cascade_file = Path(opencv_cascades[cascade_path.lower()])
            else:
                return _fail(f"Cascade not found: {cascade_path}")

        cascade = cv2.CascadeClassifier(str(cascade_file))
        if cascade.empty():
            return _fail(f"Cannot load cascade: {cascade_path}")

        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image

        detections = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        result = image.copy()
        if len(result.shape) == 2:
            result = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)

        for (x, y, w, h) in detections:
            cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 3)

        output_path = OUTPUT_DIR / 'haar_detect.png'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), cv2.cvtColor(result, cv2.COLOR_RGB2BGR))

        return {
            'success': True,
            'message': f"Detected {len(detections)} objects",
            'output_files': [str(output_path)],
            'image_data': _image_to_dict(result),
            'error': None
        }
    except Exception as e:
        return _fail(f"Haar detection failed: {e}")