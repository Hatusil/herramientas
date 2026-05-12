"""Workflows completos para remoción de watermarks."""
import os
import logging
from typing import Dict, Optional

from core.utils import get_output_path
from tools.pdf_tool.modules import wm_validacion as val
from tools.pdf_tool.modules import wm_deteccion as det
from tools.pdf_tool.modules import wm_remocion as rem

logger = logging.getLogger(__name__)


def remove_watermark_visual_workflow(
    pdf_path: str,
    output_path: Optional[str] = None,
    detection_mode: str = 'auto',
    manual_region: Optional[Dict] = None
) -> dict:
    """Workflow completo: PDF -> procesar -> PDF."""
    if not val.check_fitz():
        return {'success': False, 'error': 'Fitz no instalado', 'output_files': []}
    if not os.path.exists(pdf_path):
        return {'success': False, 'error': f'No encontrado: {pdf_path}', 'output_files': []}

    try:
        doc = val.fitz.open(pdf_path)
        if output_path is None:
            output_path = get_output_path(pdf_path, '_no_wm')

        if detection_mode == 'auto':
            regions = det.detect_watermarks_auto(doc)
        else:
            if not manual_region:
                doc.close()
                return {'success': False, 'error': 'Región manual requerida', 'output_files': []}
            regions = [manual_region]

        for page_num in range(len(doc)):
            page = doc[page_num]
            region = None
            if detection_mode == 'auto':
                region = next((r for r in regions if r.get('page') == page_num), None)
            else:
                region = manual_region
            if region:
                rem.remove_watermark_from_page(page, [region])

        doc.save(output_path)
        doc.close()
        return {
            'success': True,
            'message': f"Watermark removido: {output_path}",
            'output_files': [output_path], 'error': None
        }
    except Exception as e:
        logger.error(f"Error en workflow: {e}")
        return {'success': False, 'error': str(e), 'output_files': []}


def remove_watermark_fallback(files: list) -> dict:
    """Elimina solo anotaciones (/Annots) usando pypdf."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        return {'success': False, 'error': 'pypdf no instalado', 'output_files': []}

    output_files = []
    errors = []

    for file_path in files:
        if not os.path.exists(file_path):
            errors.append(f"No encontrado: {file_path}")
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
        except Exception as e:
            errors.append(f"{os.path.basename(file_path)}: {str(e)}")

    return {
        'success': len(output_files) > 0,
        'message': f"Anotaciones eliminadas de {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }