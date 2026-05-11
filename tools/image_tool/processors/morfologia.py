"""Phase 5: Morfología."""
from typing import Dict, Any

import numpy as np

from ._ok import _ok, _fail, CV2_AVAILABLE


def _erode(image: np.ndarray, kernel_size: int = 3) -> Dict[str, Any]:
    """Erosión con elemento estructurante cuadrangular."""
    try:
        if kernel_size % 2 == 0:
            return _fail("kernel_size must be odd")
        if kernel_size < 3:
            return _fail("kernel_size must be >= 3")

        if CV2_AVAILABLE:
            import cv2
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
            eroded = cv2.erode(image, kernel, iterations=1)
        else:
            from scipy.ndimage import minimum_filter
            eroded = minimum_filter(image, size=kernel_size).astype(np.uint8)

        return _ok(eroded, f"Erosion with kernel={kernel_size}")
    except Exception as e:
        return _fail(f"Erosion failed: {e}")


def _dilate(image: np.ndarray, kernel_size: int = 3) -> Dict[str, Any]:
    """Dilatación con elemento estructurante cuadrangular."""
    try:
        if kernel_size % 2 == 0:
            return _fail("kernel_size must be odd")
        if kernel_size < 3:
            return _fail("kernel_size must be >= 3")

        if CV2_AVAILABLE:
            import cv2
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
            dilated = cv2.dilate(image, kernel, iterations=1)
        else:
            from scipy.ndimage import maximum_filter
            dilated = maximum_filter(image, size=kernel_size).astype(np.uint8)

        return _ok(dilated, f"Dilation with kernel={kernel_size}")
    except Exception as e:
        return _fail(f"Dilation failed: {e}")


def _open(image: np.ndarray, kernel_size: int = 3) -> Dict[str, Any]:
    """Apertura: erosión seguida de dilatación."""
    try:
        if kernel_size % 2 == 0:
            return _fail("kernel_size must be odd")

        if CV2_AVAILABLE:
            import cv2
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
            opened = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        else:
            from scipy.ndimage import minimum_filter, maximum_filter
            eroded = minimum_filter(image, size=kernel_size)
            opened = maximum_filter(eroded, size=kernel_size).astype(np.uint8)

        return _ok(opened, f"Opening (erode+dilate) with kernel={kernel_size}")
    except Exception as e:
        return _fail(f"Opening failed: {e}")


def _close(image: np.ndarray, kernel_size: int = 3) -> Dict[str, Any]:
    """Cierre: dilatación seguida de erosión."""
    try:
        if kernel_size % 2 == 0:
            return _fail("kernel_size must be odd")

        if CV2_AVAILABLE:
            import cv2
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
            closed = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        else:
            from scipy.ndimage import maximum_filter, minimum_filter
            dilated = maximum_filter(image, size=kernel_size)
            closed = minimum_filter(dilated, size=kernel_size).astype(np.uint8)

        return _ok(closed, f"Closing (dilate+erode) with kernel={kernel_size}")
    except Exception as e:
        return _fail(f"Closing failed: {e}")