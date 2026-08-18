import os
from typing import List, Dict, Any

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    PdfReader = None
    PdfWriter = None

from core.utils import get_output_path, check_pypdf
from tools.pdf_tool.modules._watermark_text import add_text_watermark
from tools.pdf_tool.modules._watermark_image import add_image_watermark

import logging
logger = logging.getLogger(__name__)


def remove_annotations(files: List[str]) -> Dict[str, Any]:
    if not check_pypdf():
        return {'success': False, 'error': 'pypdf no está instalado', 'output_files': []}

    output_files = []
    errors = []

    for file_path in files:
        if not os.path.exists(file_path):
            errors.append(f"Archivo no encontrado: {file_path}")
            continue

        try:
            reader = PdfReader(file_path)
            writer = PdfWriter()

            for page in reader.pages:
                if '/Annots' in page:
                    del page['/Annots']
                writer.add_page(page)

            output_path = get_output_path(file_path, '_clean')
            with open(output_path, 'wb') as f:
                writer.write(f)

            output_files.append(output_path)
            logger.info(f"Anotaciones eliminadas: {file_path}")

        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")

    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Anotaciones eliminadas de {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


def remove_watermarks(files: List[str], **options) -> Dict[str, Any]:
    mode = options.get('mode', 'auto')

    from tools.pdf_tool.modules.watermark_removal import check_fitz, remove_watermark as remove_watermark_visual

    if mode in ('auto', 'visual'):
        if check_fitz():
            detection_mode = options.get('detection_mode', 'auto')
            manual_region = options.get('manual_region', None)

            result = remove_watermark_visual(
                files,
                detection_mode=detection_mode,
                preserve_layout=True,
                manual_region=manual_region
            )

            if result.get('success'):
                return result

            if mode == 'visual':
                return result

    return remove_annotations(files)
