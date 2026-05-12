"""Hub de re-export para eliminación de watermarks visuales."""
import os
import logging
from typing import List, Dict, Any

from core.utils import get_output_path
from tools.pdf_tool.modules import wm_validacion as val
from tools.pdf_tool.modules import wm_deteccion as det
from tools.pdf_tool.modules import wm_remocion as rem

logger = logging.getLogger(__name__)

__all__ = [
    'check_fitz',
    'detect_watermarks', 'detect_watermarks_auto', 'detect_watermarks_manual',
    'remove_watermark_from_page', 'remove_watermark', 'remove_watermark_fallback',
    'pdf_to_images', 'pdf_to_images_list', 'images_to_pdf',
    'remove_watermark_visual_workflow'
]

check_fitz = val.check_fitz
detect_watermarks = det.detect_watermarks
detect_watermarks_auto = det.detect_watermarks_auto
detect_watermarks_manual = det.detect_watermarks_manual
remove_watermark_from_page = rem.remove_watermark_from_page

from tools.pdf_tool.modules import wm_conversion as conv
from tools.pdf_tool.modules import wm_reconstruccion as recon
from tools.pdf_tool.modules import wm_workflow as wf

pdf_to_images = conv.pdf_to_images
pdf_to_images_list = conv.pdf_to_images_list
images_to_pdf = recon.images_to_pdf
remove_watermark_visual_workflow = wf.remove_watermark_visual_workflow
remove_watermark_fallback = wf.remove_watermark_fallback


def remove_watermark(files: List[str], **options) -> Dict[str, Any]:
    """Elimina watermarks visuales de PDFs."""
    if not val.check_fitz():
        return {'success': False, 'error': 'Fitz no instalado', 'output_files': []}

    mode = options.get('detection_mode', 'auto')
    manual_region = options.get('manual_region', None)
    output_files = []
    errors = []

    for file_path in files:
        if not os.path.exists(file_path):
            errors.append(f"No encontrado: {file_path}")
            continue

        try:
            doc = val.fitz.open(file_path)
            if doc.is_encrypted:
                doc.close()
                errors.append(f"PDF encriptado: {file_path}")
                continue

            if mode == 'auto':
                regions = det.detect_watermarks_auto(doc)
                if not regions:
                    out = get_output_path(file_path, '_clean')
                    doc.save(out)
                    doc.close()
                    output_files.append(out)
                    continue
                for page_num in range(len(doc)):
                    region = next((r for r in regions if r.get('page') == page_num), None)
                    if region:
                        rem.remove_watermark_from_page(doc[page_num], [region])
            else:
                if not manual_region:
                    doc.close()
                    errors.append(f"Región manual requerida para {file_path}")
                    continue
                for page in doc:
                    rem.remove_watermark_from_page(page, [manual_region])

            out = get_output_path(file_path, '_no_wm')
            doc.save(out)
            doc.close()
            output_files.append(out)
            logger.info(f"Watermark removido: {file_path}")

        except Exception as e:
            errors.append(f"{os.path.basename(file_path)}: {str(e)}")
            logger.error(f"Error: {e}")

    return {
        'success': len(output_files) > 0,
        'message': f"Watermark removido de {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }