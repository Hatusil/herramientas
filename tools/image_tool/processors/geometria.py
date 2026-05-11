"""Phase 2: Preprocesamiento y Geometría."""
from typing import Dict, Any

import numpy as np

from ._ok import _ok, _fail, CV2_AVAILABLE


def _to_grayscale(image: np.ndarray) -> Dict[str, Any]:
    """Convierte imagen RGB a escala de grises."""
    try:
        if len(image.shape) == 2:
            gray = image
        else:
            gray = np.dot(image[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
        return _ok(gray, "Converted to grayscale")
    except Exception as e:
        return _fail(f"Grayscale conversion failed: {e}")


def _to_hsv(image: np.ndarray) -> Dict[str, Any]:
    """Convierte imagen RGB a HSV."""
    try:
        if CV2_AVAILABLE:
            import cv2
            if len(image.shape) == 2:
                rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
                hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
                return _ok(hsv, "Grayscale→RGB→HSV")
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            return _ok(hsv, "Converted to HSV")
        return _fail("OpenCV not available for HSV conversion")
    except Exception as e:
        return _fail(f"HSV conversion failed: {e}")


def _crop_region(image: np.ndarray, x: int, y: int, w: int, h: int) -> Dict[str, Any]:
    """Recorta región de la imagen (ROI)."""
    try:
        h_img, w_img = image.shape[:2]
        if x < 0 or y < 0 or w <= 0 or h <= 0:
            return _fail("Invalid crop dimensions: all values must be positive")
        if x + w > w_img or y + h > h_img:
            return _fail("Crop region exceeds image boundaries")
        cropped = image[y:y + h, x:x + w]
        return _ok(cropped, f"Cropped region ({x},{y},{w},{h})")
    except Exception as e:
        return _fail(f"Crop failed: {e}")


def _resize(image: np.ndarray, scale: float) -> Dict[str, Any]:
    """Redimensiona imagen por factor de escala."""
    try:
        if scale <= 0:
            return _fail("Scale must be positive")
        h, w = image.shape[:2]
        new_h = int(h * scale)
        new_w = int(w * scale)

        if CV2_AVAILABLE:
            import cv2
            resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        else:
            from PIL import Image as PILImage
            pil_img = PILImage.fromarray(image)
            pil_img = pil_img.resize((new_w, new_h), PILImage.LANCZOS)
            resized = np.array(pil_img)

        return _ok(resized, f"Resized to {new_w}x{new_h} (scale={scale:.2f})")
    except Exception as e:
        return _fail(f"Resize failed: {e}")


def _translate(image: np.ndarray, dx: int, dy: int) -> Dict[str, Any]:
    """Traslada imagen por (dx, dy) pixels."""
    try:
        if CV2_AVAILABLE:
            import cv2
            h, w = image.shape[:2]
            M = np.float32([[1, 0, dx], [0, 1, dy]])
            translated = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        else:
            translated = np.zeros_like(image)
            src_x = max(0, dx)
            src_y = max(0, dy)
            dst_x = max(0, -dx)
            dst_y = max(0, -dy)
            copy_h = min(image.shape[0] - src_y, translated.shape[0] - dst_y)
            copy_w = min(image.shape[1] - src_x, translated.shape[1] - dst_x)
            if copy_h > 0 and copy_w > 0:
                translated[dst_y:dst_y + copy_h, dst_x:dst_x + copy_w] = \
                    image[src_y:src_y + copy_h, src_x:src_x + copy_w]

        return _ok(translated, f"Translated by ({dx}, {dy})")
    except Exception as e:
        return _fail(f"Translation failed: {e}")


def _rotate(image: np.ndarray, angle: float) -> Dict[str, Any]:
    """Rota imagen por ángulo en grados."""
    try:
        if CV2_AVAILABLE:
            import cv2
            h, w = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        else:
            from scipy.ndimage import rotate as scipy_rotate
            rotated = scipy_rotate(image, angle, reshape=False, mode='reflect')
        return _ok(rotated, f"Rotated {angle}°")
    except Exception as e:
        return _fail(f"Rotation failed: {e}")