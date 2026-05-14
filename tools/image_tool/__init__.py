"""
ImageTool: Plugin para procesamiento digital de imágenes (PDI).
"""
import logging

from core.base_tool import BaseTool

logger = logging.getLogger(__name__)


class ImageTool(BaseTool):
    """Herramienta de procesamiento digital de imágenes."""

    def __init__(self):
        self.ui = None

    def get_name(self) -> str:
        return "Imagen"

    def get_icon(self) -> str:
        return "🖼️"

    def get_description(self) -> str:
        return "Procesamiento Digital de Imágenes — 7 fases"

    def build_ui(self, parent_frame):
        from tools.image_tool.ui import ImageToolUI
        self.ui = ImageToolUI(parent_frame, on_process=self.process)
        self.ui.pack(fill="both", expand=True)

    def process(self, files: list, options: dict) -> dict:
        """Procesa imágenes según la operación seleccionada."""
        from tools.image_tool import processor
        action = options.get('action', 'info')

        if not files:
            return {'success': False, 'error': 'No hay archivos para procesar'}

        image_path = files[0]

        if action == 'load':
            # Just return info about the loaded image
            return processor._image_to_dict(processor._load_from_file(image_path))
        elif action == 'resize':
            img = processor._load_from_file(image_path)
            resized = processor._resize(img, options.get('width', 800), options.get('height', 600))
            return processor._image_to_dict(resized)
        elif action == 'crop':
            img = processor._load_from_file(image_path)
            cropped = processor._crop_region(img, options.get('x', 0), options.get('y', 0),
                                            options.get('width', 100), options.get('height', 100))
            return processor._image_to_dict(cropped)
        elif action == 'rotate':
            img = processor._load_from_file(image_path)
            rotated = processor._rotate(img, options.get('angle', 90))
            return processor._image_to_dict(rotated)
        elif action == 'grayscale':
            img = processor._load_from_file(image_path)
            gray = processor._to_grayscale(img)
            return processor._image_to_dict(gray)
        elif action == 'blur':
            img = processor._load_from_file(image_path)
            blurred = processor._filter_gaussian(img, options.get('kernel', 5))
            return processor._image_to_dict(blurred)
        elif action == 'edge':
            img = processor._load_from_file(image_path)
            edges = processor._edge_canny(img, options.get('threshold1', 50), options.get('threshold2', 150))
            return processor._image_to_dict(edges)
        elif action == 'histogram':
            img = processor._load_from_file(image_path)
            return processor._compute_histogram(img)
        elif action == 'brightness':
            img = processor._load_from_file(image_path)
            adjusted = processor._adjust_brightness_contrast(img,
                options.get('brightness', 1.0), options.get('contrast', 1.0))
            return processor._image_to_dict(adjusted)
        elif action == 'info':
            img = processor._load_from_file(image_path)
            fmt = processor._detect_format(image_path)
            return {
                'success': True,
                'format': fmt,
                'shape': img.shape if hasattr(img, 'shape') else None,
                'dtype': str(img.dtype) if hasattr(img, 'dtype') else None
            }
        else:
            return {'success': False, 'error': f'Unknown action: {action}'}