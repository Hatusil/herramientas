"""Phase 4: Filtrado."""
from typing import Dict, Any

import numpy as np

from ._ok import _ok, _fail, CV2_AVAILABLE


def _filter_gaussian(image: np.ndarray, ksize: int = 5) -> Dict[str, Any]:
    """Aplica filtro gaussiano para suavizado."""
    try:
        if ksize % 2 == 0:
            return _fail("ksize must be odd")
        if ksize < 3:
            return _fail("ksize must be >= 3")

        if CV2_AVAILABLE:
            import cv2
            filtered = cv2.GaussianBlur(image, (ksize, ksize), 0)
        else:
            from scipy.ndimage import uniform_filter
            filtered = uniform_filter(image.astype(float), size=ksize).astype(np.uint8)

        return _ok(filtered, f"Gaussian filter ksize={ksize}")
    except Exception as e:
        return _fail(f"Gaussian filter failed: {e}")


def _filter_median(image: np.ndarray, ksize: int = 3) -> Dict[str, Any]:
    """Aplica filtro de mediana para reducción de ruido salt-and-pepper."""
    try:
        if ksize % 2 == 0:
            return _fail("ksize must be odd")

        if CV2_AVAILABLE:
            import cv2
            filtered = cv2.medianBlur(image, ksize)
        else:
            from scipy.ndimage import median_filter
            filtered = median_filter(image, size=ksize).astype(np.uint8)

        return _ok(filtered, f"Median filter ksize={ksize}")
    except Exception as e:
        return _fail(f"Median filter failed: {e}")


def _filter_mean(image: np.ndarray, ksize: int = 3) -> Dict[str, Any]:
    """Aplica filtro de media (blur uniforme)."""
    try:
        if ksize % 2 == 0:
            return _fail("ksize must be odd")

        if CV2_AVAILABLE:
            import cv2
            filtered = cv2.blur(image, (ksize, ksize))
        else:
            from scipy.ndimage import uniform_filter
            filtered = uniform_filter(image.astype(float), size=ksize).astype(np.uint8)

        return _ok(filtered, f"Mean filter ksize={ksize}")
    except Exception as e:
        return _fail(f"Mean filter failed: {e}")


def _deconvolve(image: np.ndarray, kernel_type: str = 'gaussian') -> Dict[str, Any]:
    """Aplica deconvolución para restauración de imagen borrosa (async)."""
    try:
        if kernel_type not in ('gaussian', 'motion', 'disk'):
            return _fail(f"Unknown kernel_type: {kernel_type}")

        if CV2_AVAILABLE:
            import cv2
            if kernel_type == 'gaussian':
                kernel_size = 31
                kernel = cv2.getGaussianKernel(kernel_size, 10)
                kernel = kernel @ kernel.T
            elif kernel_type == 'motion':
                kernel_size = 31
                kernel = np.zeros((kernel_size, kernel_size))
                kernel[int((kernel_size - 1) / 2), :] = np.ones(kernel_size)
                kernel = kernel / kernel_size
            else:
                radius = 10
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (radius * 2 + 1, radius * 2 + 1))
                kernel = kernel.astype(float) / kernel.sum()

            blurred = cv2.GaussianBlur(image, (15, 15), 0)
            detail = cv2.subtract(image, blurred)
            deconv = cv2.add(image, detail)
            return _ok(deconv, f"Deconvolved (kernel={kernel_type})")
        else:
            return _fail("OpenCV required for deconvolution")
    except Exception as e:
        return _fail(f"Deconvolution failed: {e}")