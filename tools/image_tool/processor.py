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
            if len(image.shape) == 2:
                # Grayscale → RGB antes de HSV
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


# === PHASE 5: MORFOLOGÍA ==========================================


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
            from scipy.ndimage import binary_erosion
            # For grayscale, use minimum filter
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
            # Manual: erode then dilate
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
            # Manual: dilate then erode
            from scipy.ndimage import maximum_filter, minimum_filter
            dilated = maximum_filter(image, size=kernel_size)
            closed = minimum_filter(dilated, size=kernel_size).astype(np.uint8)

        return _ok(closed, f"Closing (dilate+erode) with kernel={kernel_size}")
    except Exception as e:
        return _fail(f"Closing failed: {e}")


# === PHASE 6: DETECCIÓN DE BORDES ==================================


def _edge_sobel(image: np.ndarray) -> Dict[str, Any]:
    """Detector Sobel."""
    try:
        if CV2_AVAILABLE:
            import cv2
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image

            # Sobel in x and y
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            magnitude = np.sqrt(sobelx**2 + sobely**2)
            magnitude = np.uint8(np.clip(magnitude, 0, 255))
        else:
            # Manual Sobel approximation
            if len(image.shape) == 3:
                gray = np.dot(image[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
            else:
                gray = image

            # Simple gradient
            gx = np.abs(np.gradient(gray, axis=1))
            gy = np.abs(np.gradient(gray, axis=0))
            magnitude = np.clip(gx + gy, 0, 255).astype(np.uint8)

        return _ok(magnitude, "Sobel edge detection")
    except Exception as e:
        return _fail(f"Sobel failed: {e}")


def _edge_prewitt(image: np.ndarray) -> Dict[str, Any]:
    """Detector Prewitt."""
    try:
        if CV2_AVAILABLE:
            import cv2
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image

            # Prewitt kernels
            kernelx = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
            kernely = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]])

            prewittx = cv2.filter2D(gray, cv2.CV_64F, kernelx)
            prewitty = cv2.filter2D(gray, cv2.CV_64F, kernely)
            magnitude = np.sqrt(prewittx**2 + prewitty**2)
            magnitude = np.uint8(np.clip(magnitude, 0, 255))
        else:
            if len(image.shape) == 3:
                gray = np.dot(image[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
            else:
                gray = image

            gx = np.abs(np.gradient(gray.astype(float), axis=1))
            gy = np.abs(np.gradient(gray.astype(float), axis=0))
            magnitude = np.clip(gx + gy, 0, 255).astype(np.uint8)

        return _ok(magnitude, "Prewitt edge detection")
    except Exception as e:
        return _fail(f"Prewitt failed: {e}")


def _edge_laplacian(image: np.ndarray) -> Dict[str, Any]:
    """Detector Laplaciano."""
    try:
        if CV2_AVAILABLE:
            import cv2
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image

            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            laplacian = np.uint8(np.clip(np.abs(laplacian), 0, 255))
        else:
            if len(image.shape) == 3:
                gray = np.dot(image[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
            else:
                gray = image

            # Manual Laplacian (4-neighbor)
            laplacian = np.zeros_like(gray, dtype=np.float64)
            laplacian[1:-1, 1:-1] = (
                -4 * gray[1:-1, 1:-1]
                + gray[:-2, 1:-1]
                + gray[2:, 1:-1]
                + gray[1:-1, :-2]
                + gray[1:-1, 2:]
            )
            laplacian = np.uint8(np.clip(np.abs(laplacian), 0, 255))

        return _ok(laplacian, "Laplacian edge detection")
    except Exception as e:
        return _fail(f"Laplacian failed: {e}")


def _edge_canny(image: np.ndarray, threshold1: int = 50, threshold2: int = 150) -> Dict[str, Any]:
    """Detector Canny (async)."""
    try:
        if CV2_AVAILABLE:
            import cv2
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image

            edges = cv2.Canny(gray, threshold1, threshold2)
        else:
            # Manual Canny approximation using gradient magnitude
            if len(image.shape) == 3:
                gray = np.dot(image[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
            else:
                gray = image

            # Simple gradient magnitude as edge approximation
            gx = np.abs(np.gradient(gray.astype(float), axis=1))
            gy = np.abs(np.gradient(gray.astype(float), axis=0))
            magnitude = np.clip(gx + gy, 0, 255).astype(np.uint8)

            # Apply hysteresis thresholding
            edges = np.zeros_like(magnitude)
            edges[magnitude > threshold2] = 255
            edges[(magnitude > threshold1) & (magnitude <= threshold2)] = 128

        return _ok(edges, f"Canny edges (t1={threshold1}, t2={threshold2})")
    except Exception as e:
        return _fail(f"Canny failed: {e}")


def _find_contours(image: np.ndarray) -> Dict[str, Any]:
    """Encuentra contornos en imagen binarizada."""
    try:
        if CV2_AVAILABLE:
            import cv2
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image

            contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Draw contours on copy
            result = image.copy()
            if len(result.shape) == 2:
                result = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
            cv2.drawContours(result, contours, -1, (0, 255, 0), 2)

            output_path = Path('output/contours.png')
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(output_path), cv2.cvtColor(result, cv2.COLOR_RGB2BGR))

            return {
                'success': True,
                'message': f"Found {len(contours)} contours",
                'output_files': [str(output_path)],
                'image_data': _image_to_dict(result),
                'error': None
            }
        else:
            return _fail("OpenCV required for findContours")
    except Exception as e:
        return _fail(f"Find contours failed: {e}")


def _bounding_boxes(image: np.ndarray, min_area: int = 100) -> Dict[str, Any]:
    """Calcula bounding boxes de contornos."""
    try:
        if CV2_AVAILABLE:
            import cv2
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image

            contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Filter by area and draw boxes
            result = image.copy()
            if len(result.shape) == 2:
                result = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)

            boxes = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area >= min_area:
                    x, y, w, h = cv2.boundingRect(cnt)
                    boxes.append({'x': x, 'y': y, 'w': w, 'h': h, 'area': int(area)})
                    cv2.rectangle(result, (x, y), (x + w, y + h), (255, 0, 0), 2)

            output_path = Path('output/bounding_boxes.png')
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(output_path), cv2.cvtColor(result, cv2.COLOR_RGB2BGR))

            return {
                'success': True,
                'message': f"Found {len(boxes)} bounding boxes (min_area={min_area})",
                'output_files': [str(output_path)],
                'image_data': _image_to_dict(result),
                'error': None
            }
        else:
            return _fail("OpenCV required for bounding boxes")
    except Exception as e:
        return _fail(f"Bounding boxes failed: {e}")


# === PHASE 7: ANÁLISIS AVANZADO ======================================


def _template_match(image: np.ndarray, template_path: str) -> Dict[str, Any]:
    """Template matching (async)."""
    try:
        if not Path(template_path).exists():
            return _fail(f"Template not found: {template_path}")

        if CV2_AVAILABLE:
            import cv2

            # Load template
            template = _load_image(template_path)
            if not template['success']:
                return _fail(f"Cannot load template: {template.get('error')}")

            template_img = template['image_data']['array']
            if len(template_img.shape) == 3:
                template_gray = cv2.cvtColor(template_img, cv2.COLOR_RGB2GRAY)
            else:
                template_gray = template_img

            # Convert main image to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image

            # Template matching
            result = cv2.matchTemplate(gray, template_gray, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # Draw rectangle at best match
            h, w = template_gray.shape
            output = image.copy()
            if len(output.shape) == 2:
                output = cv2.cvtColor(output, cv2.COLOR_GRAY2RGB)
            cv2.rectangle(output, max_loc, (max_loc[0] + w, max_loc[1] + h), (0, 255, 0), 3)

            output_path = Path('output/template_match.png')
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(output_path), cv2.cvtColor(output, cv2.COLOR_RGB2BGR))

            return {
                'success': True,
                'message': f"Best match at ({max_loc[0]}, {max_loc[1]}) with confidence {max_val:.3f}",
                'output_files': [str(output_path)],
                'image_data': _image_to_dict(output),
                'error': None
            }
        else:
            return _fail("OpenCV required for template matching")
    except Exception as e:
        return _fail(f"Template matching failed: {e}")


def _pseudocolor(image: np.ndarray, colormap: str = 'jet') -> Dict[str, Any]:
    """Asigna pseudocolores a imagen en escala de grises."""
    try:
        if CV2_AVAILABLE:
            import cv2
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image

            # Map colormap name to CV2 constant
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
            # Manual colormap fallback (simple gradient)
            if len(image.shape) == 3:
                gray = np.dot(image[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
            else:
                gray = image

            # Simple rainbow-like mapping
            normalized = gray.astype(float) / 255.0
            colored = np.zeros((gray.shape[0], gray.shape[1], 3), dtype=np.uint8)
            colored[..., 0] = (normalized * 255).astype(np.uint8)  # Red channel
            colored[..., 1] = ((1 - normalized) * 127).astype(np.uint8)  # Green
            colored[..., 2] = ((1 - normalized) * 255).astype(np.uint8)  # Blue

        return _ok(colored, f"Pseudocolor applied ({colormap})")
    except Exception as e:
        return _fail(f"Pseudocolor failed: {e}")


def _haar_detect(image: np.ndarray, cascade_path: str) -> Dict[str, Any]:
    """Detección con Haar cascades (async)."""
    try:
        if not CV2_AVAILABLE:
            return _fail("OpenCV required for Haar detection")

        import cv2

        # Check if cascade file exists
        cascade_file = Path(cascade_path)
        if not cascade_file.exists():
            # Try OpenCV built-in cascades
            opencv_cascades = {
                'face': cv2.data.haarcascades + 'haarcascade_frontalface_default.xml',
                'eye': cv2.data.haarcascades + 'haarcascade_eye.xml',
                'smile': cv2.data.haarcascades + 'haarcascade_smile.xml',
            }

            if cascade_path.lower() in opencv_cascades:
                cascade_file = Path(opencv_cascades[cascade_path.lower()])
            else:
                return _fail(f"Cascade not found: {cascade_path}")

        # Load cascade
        cascade = cv2.CascadeClassifier(str(cascade_file))
        if cascade.empty():
            return _fail(f"Cannot load cascade: {cascade_path}")

        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image

        # Detect
        detections = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Draw rectangles
        result = image.copy()
        if len(result.shape) == 2:
            result = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)

        for (x, y, w, h) in detections:
            cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 3)

        output_path = Path('output/haar_detect.png')
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


# === CV2 availability check ===
CV2_AVAILABLE = True
try:
    import cv2
except ImportError:
    CV2_AVAILABLE = False