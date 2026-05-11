"""Phase 1: Adquisición de imagen."""
from pathlib import Path
from typing import Dict, Any

import numpy as np

from core.image_utils import _load_image, _validate_format
from core.metrics import Counter

from ._ok import _fail, op_counter


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

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(url, context=ctx, timeout=10) as resp:
            data = resp.read()

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