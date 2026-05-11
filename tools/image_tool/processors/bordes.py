"""Phase 6: Detección de Bordes."""
from pathlib import Path
from typing import Dict, Any

import numpy as np

from ._ok import _ok, _fail, _image_to_dict, CV2_AVAILABLE


def _to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convierte a grayscale si es necesario."""
    if len(image.shape) == 3:
        return np.dot(image[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
    return image


def _edge_sobel(image: np.ndarray) -> Dict[str, Any]:
    """Detector Sobel."""
    try:
        if CV2_AVAILABLE:
            import cv2
            gray = _to_grayscale(image) if len(image.shape) == 3 else image
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            magnitude = np.sqrt(sobelx**2 + sobely**2)
            magnitude = np.uint8(np.clip(magnitude, 0, 255))
        else:
            gray = _to_grayscale(image)
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
            gray = _to_grayscale(image) if len(image.shape) == 3 else image
            kernelx = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
            kernely = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]])
            prewittx = cv2.filter2D(gray, cv2.CV_64F, kernelx)
            prewitty = cv2.filter2D(gray, cv2.CV_64F, kernely)
            magnitude = np.sqrt(prewittx**2 + prewitty**2)
            magnitude = np.uint8(np.clip(magnitude, 0, 255))
        else:
            gray = _to_grayscale(image)
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
            gray = _to_grayscale(image) if len(image.shape) == 3 else image
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            laplacian = np.uint8(np.clip(np.abs(laplacian), 0, 255))
        else:
            gray = _to_grayscale(image)
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
            gray = _to_grayscale(image) if len(image.shape) == 3 else image
            edges = cv2.Canny(gray, threshold1, threshold2)
        else:
            gray = _to_grayscale(image)
            gx = np.abs(np.gradient(gray.astype(float), axis=1))
            gy = np.abs(np.gradient(gray.astype(float), axis=0))
            magnitude = np.clip(gx + gy, 0, 255).astype(np.uint8)
            edges = np.zeros_like(magnitude)
            edges[magnitude > threshold2] = 255
            edges[(magnitude > threshold1) & (magnitude <= threshold2)] = 128

        return _ok(edges, f"Canny edges (t1={threshold1}, t2={threshold2})")
    except Exception as e:
        return _fail(f"Canny failed: {e}")


def _find_contours(image: np.ndarray) -> Dict[str, Any]:
    """Encuentra contornos en imagen binarizada."""
    try:
        if not CV2_AVAILABLE:
            return _fail("OpenCV required for findContours")

        import cv2
        gray = _to_grayscale(image) if len(image.shape) == 3 else image
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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
    except Exception as e:
        return _fail(f"Find contours failed: {e}")


def _bounding_boxes(image: np.ndarray, min_area: int = 100) -> Dict[str, Any]:
    """Calcula bounding boxes de contornos."""
    try:
        if not CV2_AVAILABLE:
            return _fail("OpenCV required for bounding boxes")

        import cv2
        gray = _to_grayscale(image) if len(image.shape) == 3 else image
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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
    except Exception as e:
        return _fail(f"Bounding boxes failed: {e}")