"""Phase 3: Mejora Visual."""
from typing import Dict, Any

import numpy as np

from ._ok import _ok, _fail, _image_to_dict, CV2_AVAILABLE
from core.constants import OUTPUT_DIR


def _compute_histogram(image: np.ndarray) -> Dict[str, Any]:
    """Calcula histograma de intensidades y genera plot."""
    try:
        import matplotlib.pyplot as plt

        if len(image.shape) == 3:
            gray = np.dot(image[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
        else:
            gray = image

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(gray.ravel(), bins=256, range=(0, 256), color='gray', alpha=0.7)
        ax.set_xlabel('Intensidad')
        ax.set_ylabel('Frecuencia')
        ax.set_title('Histograma de Intensidades')

        output_path = OUTPUT_DIR / 'histogram.png'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(str(output_path), dpi=100, bbox_inches='tight')
        plt.close(fig)

        return {
            'success': True,
            'message': f"Histogram: {output_path.name}",
            'output_files': [str(output_path)],
            'image_data': _image_to_dict(image),
            'error': None
        }
    except Exception as e:
        return _fail(f"Histogram computation failed: {e}")


def _equalize_histogram(image: np.ndarray) -> Dict[str, Any]:
    """Ecualiza histograma para mejorar contraste (async)."""
    try:
        if len(image.shape) == 3:
            gray = np.dot(image[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
        else:
            gray = image.astype(np.uint8)

        if CV2_AVAILABLE:
            import cv2
            equalized = cv2.equalizeHist(gray)
        else:
            hist, bins = np.histogram(gray.flatten(), 256, [0, 256])
            cdf = hist.cumsum()
            cdf_normalized = cdf * 255 / cdf[-1]
            equalized = np.interp(gray.flatten(), bins[:-1], cdf_normalized).astype(np.uint8)
            equalized = equalized.reshape(gray.shape)

        if len(image.shape) == 3:
            result_img = np.stack([equalized] * 3, axis=-1)
        else:
            result_img = equalized

        return _ok(result_img, "Histogram equalized")
    except Exception as e:
        return _fail(f"Equalization failed: {e}")


def _adjust_brightness_contrast(
    image: np.ndarray,
    brightness: float = 0.0,
    contrast: float = 1.0
) -> Dict[str, Any]:
    """Ajusta brillo (offset) y contraste (factor) linealmente."""
    try:
        adjusted = image.astype(np.float32)
        adjusted = adjusted * contrast + brightness * 255
        adjusted = np.clip(adjusted, 0, 255).astype(np.uint8)
        return _ok(adjusted, f"Brightness={brightness:.2f}, Contrast={contrast:.2f}")
    except Exception as e:
        return _fail(f"Brightness/contrast adjustment failed: {e}")


def _adjust_gamma(image: np.ndarray, gamma: float) -> Dict[str, Any]:
    """Ajusta gamma (corrección no lineal de intensidad)."""
    try:
        if gamma <= 0:
            return _fail("Gamma must be positive")
        normalized = image.astype(np.float32) / 255.0
        corrected = np.power(normalized, 1.0 / gamma)
        result = (corrected * 255).astype(np.uint8)
        return _ok(result, f"Gamma={gamma:.2f}")
    except Exception as e:
        return _fail(f"Gamma adjustment failed: {e}")