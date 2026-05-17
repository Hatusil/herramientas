"""
Operaciones de transformación de PDFs: rotate, reorder, merge, extract.
Separado de transform.py por SRP (máxima R0: clases <300 líneas).
"""
import logging
import os
from typing import List, Dict, Any

from pypdf import PdfReader, PdfWriter

from core.utils import get_output_path, check_pypdf
from tools.pdf_tool.modules.validation import validate_page_range, validate_new_order

logger = logging.getLogger(__name__)


def rotate_pages(files: List[str], degrees: int = 90, pages: List[int] = None) -> Dict[str, Any]:
    """Rota páginas del PDF."""
    if not check_pypdf():
        return {'success': False, 'error': 'pypdf no está instalado', 'output_files': []}
    
    if degrees not in [90, 180, 270]:
        return {'success': False, 'error': 'Degrees debe ser 90, 180 o 270', 'output_files': []}
    
    output_files = []
    errors = []
    
    for file_path in files:
        if not os.path.exists(file_path):
            errors.append(f"Archivo no encontrado: {file_path}")
            continue
        
        try:
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            for i, page in enumerate(reader.pages):
                if pages is None or (i + 1) in pages:
                    try:
                        current_rotation = 0
                        if '/Rotate' in page:
                            rot_obj = page['/Rotate']
                            try:
                                current_rotation = int(rot_obj)
                            except (TypeError, ValueError):
                                current_rotation = 0
                        
                        new_rotation = (current_rotation + degrees) % 360
                        page['/Rotate'] = new_rotation
                    except Exception as e:
                        logger.warning(f"Error rotando página {i}: {e}")
                
                writer.add_page(page)
            
            output_path = get_output_path(file_path, f'_rotated_{degrees}')
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"Páginas rotadas: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Rotación aplicada a {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


def reorder_pages(files: List[str], new_order: List[int]) -> Dict[str, Any]:
    """Reordena las páginas de un PDF."""
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
            
            num_pages = len(reader.pages)
            
            for p in new_order:
                if p < 1 or p > num_pages:
                    return {'success': False, 'error': f'Número de página inválido: {p}', 'output_files': []}
            
            for new_pos in new_order:
                page = reader.pages[new_pos - 1]
                writer.add_page(page)
            
            output_path = get_output_path(file_path, '_reordered')
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"Páginas reordenadas: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Páginas reordenadas en {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


def merge_pdfs(files: List[str], output_path: str = None) -> Dict[str, Any]:
    """Combina múltiples PDFs en uno."""
    if not check_pypdf():
        return {'success': False, 'error': 'pypdf no está instalado', 'output_files': []}
    
    if len(files) < 2:
        return {'success': False, 'error': 'Se necesitan al menos 2 PDFs para combinar', 'output_files': []}
    
    errors = []
    writer = PdfWriter()
    total_pages = 0
    
    for file_path in files:
        if not os.path.exists(file_path):
            errors.append(f"Archivo no encontrado: {file_path}")
            continue
        
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                writer.add_page(page)
            total_pages += len(reader.pages)
        except Exception as e:
            errors.append(f"Error leyendo {file_path}: {str(e)}")
    
    if total_pages == 0:
        return {'success': False, 'error': 'No se pudieron leer páginas de los PDFs', 'output_files': []}
    
    if output_path is None:
        output_path = get_output_path(files[0], '_merged')
    
    try:
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        return {
            'success': True,
            'message': f"PDFs combinados: {total_pages} páginas",
            'output_files': [output_path],
            'error': None
        }
    except Exception as e:
        return {'success': False, 'error': f'Error escribiendo archivo: {str(e)}', 'output_files': []}


def extract_pages(files: List[str], pages: List[int]) -> Dict[str, Any]:
    """Extrae páginas específicas de un PDF."""
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
            
            num_pages = len(reader.pages)
            
            for p in pages:
                if p < 1 or p > num_pages:
                    continue
                writer.add_page(reader.pages[p - 1])
            
            output_path = get_output_path(file_path, '_extracted')
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"Páginas extraídas: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Extraídas {len(pages)} páginas de {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


# =============================================================================
# FUNCIONES AVANZADAS
# =============================================================================

def extract_page(files: List[str], page_number: int) -> Dict[str, Any]:
    """Extrae una página específica de un PDF."""
    if not check_pypdf():
        return {'success': False, 'error': 'pypdf no está instalado', 'output_files': []}
    return extract_range(files, start_page=page_number, end_page=page_number)


def extract_range(files: List[str], start_page: int, end_page: int) -> Dict[str, Any]:
    """Extrae un rango de páginas de un PDF."""
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
            
            num_pages = len(reader.pages)
            
            valid, error_msg = validate_page_range(start_page, end_page, num_pages)
            if not valid:
                errors.append(f"Error en {os.path.basename(file_path)}: {error_msg}")
                continue
            
            for i in range(start_page - 1, end_page):
                writer.add_page(reader.pages[i])
            
            output_path = get_output_path(file_path, f'_page_{start_page}-{end_page}')
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"Páginas {start_page}-{end_page} extraídas: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Extraídas páginas {start_page}-{end_page} de {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


def reorder_pages_advanced(files: List[str], new_order: List[int]) -> Dict[str, Any]:
    """Reordena las páginas de un PDF con validación mejorada."""
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
            
            num_pages = len(reader.pages)
            
            valid, error_msg = validate_new_order(new_order, num_pages)
            if not valid:
                errors.append(f"Error en {os.path.basename(file_path)}: {error_msg}")
                continue
            
            for new_pos in new_order:
                page = reader.pages[new_pos - 1]
                writer.add_page(page)
            
            output_path = get_output_path(file_path, '_reordered')
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"Páginas reordenadas: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Páginas reordenadas en {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }