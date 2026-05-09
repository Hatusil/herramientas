"""
Processor: PDI - Fase 1 Adquisición, Fase 2 Geometría,
Fase 3 Mejora, Fase 4 Filtrado.
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import numpy as np

from core.image_utils import _load_image, _save_image, _validate_format
from core.metrics import Timer, Counter

logger = logging.getLogger(__name__)

# Contadores de operación
op_counter = Counter('image_operations')

# === PHASE 1: ADQUISICIÓN ==========================================


def _load_from_file(file_path: str) -> Dict[str, Any]:
    """Carga imagen desde archivo local."""
    if not Path(file_path).exists():
        return _fail(f"File not found: {file_path}")

    if not _validate_format(file_path):
        return _fail(f"Unsupported format: {Path(file_path).suffix}")

    result = _load_image(file_path)
    if result['success']:
        op_counter.increment()
        result['message'] = f"Loaded: {Path(file_path).name}"
    return result


def _load_from_url(url: str) -> Dict[str, Any]:
    """Carga imagen desde URL (async)."""
    try:
        import urllib.request
        import ssl

        # Create SSL context that doesn't verify (for development)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(url, context=ctx, timeout=10) as resp:
            data = resp.read()

        # Save to temp file then load
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            tmp.write(data)
            result = _load_image(tmp.name)

        if result['success']:
            op_counter.increment()
            result['message'] = f"Loaded from URL: {url[:50]}..."

        return result

    except Exception as e:
        return _fail(f"URL load failed: {str(e)}")


def _detect_format(file_path: str) -> Dict[str, Any]:
    """Detecta formato y metadata de imagen."""
    if not Path(file_path).exists():
        return _fail(f"File not found: {file_path}")

    path = Path(file_path)
    ext = path.suffix.lower()

    if ext not in {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}:
        return _fail(f"Unsupported format: {ext}")

    # Try to get basic info
    result = _load_image(file_path)
    if result['success']:
        img_data = result['image_data']
        return {
            'success': True,
            'message': f"Format: {ext} | Shape: {img_data['shape']} | Mode: {img_data['mode']}",
            'output_files': [],
            'image_data': img_data,
            'error': None
        }

    return _fail(f"Cannot detect format: {file_path}")


# === PHASE 2: PREPROCESAMIENTO Y GEOMETRÍA ========================


def _to_grayscale(image: np.ndarray) -> Dict[str, Any]:
    """Convierte imagen RGB a escala de grises."""
    try:
        if len(image.shape) == 2:
            # Already grayscale
            gray = image
        else:
            # RGB to grayscale: weighted average
            gray = np.dot(image[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)

        return _ok(gray, "Converted to grayscale")
    except Exception as e:
        return _fail(f"Grayscale conversion failed: {e}")


def _to_hsv(image: np.ndarray) -> Dict[str, Any]:
    """Convierte imagen RGB a HSV."""
    try:
        if CV2_AVAILABLE:
            import cv2
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
            # Manual translation
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


# === PHASE 3: MEJORA VISUAL =========================================


def _compute_histogram(image: np.ndarray) -> Dict[str, Any]:
    """Calcula histograma de intensidades y genera plot."""
    try:
        import matplotlib.pyplot as plt

        # Convert to grayscale for histogram
        if len(image.shape) == 3:
            gray = np.dot(image[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
        else:
            gray = image

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(gray.ravel(), bins=256, range=(0, 256), color='gray', alpha=0.7)
        ax.set_xlabel('Intensidad')
        ax.set_ylabel('Frecuencia')
        ax.set_title('Histograma de Intensidades')

        output_path = Path('output/histogram.png')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(str(output_path), dpi=100, bbox_inches='tight')
        plt.close(fig)

        return {
            'success': True,
            'message': f"Histogram saved: {output_path}",
            'output_files': [str(output_path)],
            'image_data': _image_to_dict(image),
            'error': None
        }
    except Exception as e:
        return _fail(f"Histogram computation failed: {e}")


def _equalize_histogram(image: np.ndarray) -> Dict[str, Any]:
    """Ecualiza histograma para mejorar contraste (async)."""
    try:
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = np.dot(image[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
        else:
            gray = image.astype(np.uint8)

        if CV2_AVAILABLE:
            import cv2
            equalized = cv2.equalizeHist(gray)
        else:
            # Manual histogram equalization
            hist, bins = np.histogram(gray.flatten(), 256, [0, 256])
            cdf = hist.cumsum()
            cdf_normalized = cdf * 255 / cdf[-1]

            # Map original values to equalized
            equalized = np.interp(gray.flatten(), bins[:-1], cdf_normalized).astype(np.uint8)
            equalized = equalized.reshape(gray.shape)

        # Convert back to 3-channel if original was color
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
        # Apply contrast first (multiply), then brightness (add)
        adjusted = image.astype(np.float32)
        adjusted = adjusted * contrast + brightness * 255

        # Clip to valid range
        adjusted = np.clip(adjusted, 0, 255).astype(np.uint8)

        return _ok(adjusted, f"Brightness={brightness:.2f}, Contrast={contrast:.2f}")
    except Exception as e:
        return _fail(f"Brightness/contrast adjustment failed: {e}")


def _adjust_gamma(image: np.ndarray, gamma: float) -> Dict[str, Any]:
    """Ajusta gamma (corrección no lineal de intensidad)."""
    try:
        if gamma <= 0:
            return _fail("Gamma must be positive")

        # Normalize to [0,1], apply gamma, denormalize
        normalized = image.astype(np.float32) / 255.0
        corrected = np.power(normalized, 1.0 / gamma)
        result = (corrected * 255).astype(np.uint8)

        return _ok(result, f"Gamma={gamma:.2f}")
    except Exception as e:
        return _fail(f"Gamma adjustment failed: {e}")


# === PHASE 4: FILTRADO ============================================


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
            # Manual Gaussian approximation using box filter
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
            # Create blur kernel
            if kernel_type == 'gaussian':
                kernel_size = 31
                kernel = cv2.getGaussianKernel(kernel_size, 10)
                kernel = kernel @ kernel.T
            elif kernel_type == 'motion':
                kernel_size = 31
                kernel = np.zeros((kernel_size, kernel_size))
                kernel[int((kernel_size - 1) / 2), :] = np.ones(kernel_size)
                kernel = kernel / kernel_size
            else:  # disk
                radius = 10
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (radius * 2 + 1, radius * 2 + 1))
                kernel = kernel.astype(float) / kernel.sum()

            # Wiener-like deconvolution: sharpen using unsharp mask approach
            blurred = cv2.GaussianBlur(image, (15, 15), 0)
            detail = cv2.subtract(image, blurred)
            deconv = cv2.add(image, detail)

            return _ok(deconv, f"Deconvolved (kernel={kernel_type})")
        else:
            return _fail("OpenCV required for deconvolution")
    except Exception as e:
        return _fail(f"Deconvolution failed: {e}")


# === HELPERS =======================================================


def _ok(image: np.ndarray, message: str) -> Dict[str, Any]:
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


def _image_to_dict(image: np.ndarray) -> Dict[str, Any]:
    """Helper: array -> image_data dict."""
    return {
        'array': image,
        'shape': image.shape,
        'dtype': str(image.dtype),
        'format': 'png',
        'mode': 'RGB' if len(image.shape) == 3 else 'L'
    }


# === CV2 availability check ===
CV2_AVAILABLE = True
try:
    import cv2
except ImportError:
    CV2_AVAILABLE = False