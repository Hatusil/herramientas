"""Procesadores de imagen - Phase 1-7."""
from ._ok import _ok, _fail, _image_to_dict, CV2_AVAILABLE, op_counter

from .adquisicion import _load_from_file, _load_from_url, _detect_format
from .geometria import _to_grayscale, _to_hsv, _crop_region, _resize, _translate, _rotate
from .mejora import _compute_histogram, _equalize_histogram, _adjust_brightness_contrast, _adjust_gamma
from .filtros import _filter_gaussian, _filter_median, _filter_mean, _deconvolve
from .morfologia import _erode, _dilate, _open, _close
from .bordes import _edge_sobel, _edge_prewitt, _edge_laplacian, _edge_canny, _find_contours, _bounding_boxes
from .analisis import _template_match, _pseudocolor, _haar_detect

__all__ = [
    '_ok', '_fail', '_image_to_dict', 'CV2_AVAILABLE', 'op_counter',
    '_load_from_file', '_load_from_url', '_detect_format',
    '_to_grayscale', '_to_hsv', '_crop_region', '_resize', '_translate', '_rotate',
    '_compute_histogram', '_equalize_histogram', '_adjust_brightness_contrast', '_adjust_gamma',
    '_filter_gaussian', '_filter_median', '_filter_mean', '_deconvolve',
    '_erode', '_dilate', '_open', '_close',
    '_edge_sobel', '_edge_prewitt', '_edge_laplacian', '_edge_canny', '_find_contours', '_bounding_boxes',
    '_template_match', '_pseudocolor', '_haar_detect',
]