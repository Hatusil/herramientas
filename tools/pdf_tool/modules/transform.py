"""
Módulo de transformación de PDFs.
Proporciona funciones para rotar, reordenar, combinar y extraer páginas de PDFs.
"""
import logging
import os
from typing import List, Dict, Any

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    PdfReader = None
    PdfWriter = None

# Importar función compartida de core (máxima C2: Consistency)
from core.utils import get_output_path, check_pypdf

logger = logging.getLogger(__name__)


# =============================================================================
# VALIDACIÓN
# =============================================================================


# =============================================================================
# VALIDACIÓN DE PÁGINAS
# =============================================================================

def validate_page_number(page_num: int, total_pages: int) -> tuple[bool, str]:
    """
    Valida un número de página.
    
    Args:
        page_num: Número de página (1-indexed)
        total_pages: Total de páginas en el documento
        
    Returns:
        tuple: (es_válido, mensaje_error)
    """
    if page_num < 1:
        return False, f"Número de página inválido: {page_num} (debe ser >= 1)"
    if page_num > total_pages:
        return False, f"Número de página {page_num} excede el total de páginas ({total_pages})"
    return True, ""


def validate_page_range(start: int, end: int, total_pages: int) -> tuple[bool, str]:
    """
    Valida un rango de páginas.
    
    Args:
        start: Página inicial (1-indexed)
        end: Página final (1-indexed)
        total_pages: Total de páginas en el documento
        
    Returns:
        tuple: (es_válido, mensaje_error)
    """
    if start < 1:
        return False, f"Página inicial inválida: {start} (debe ser >= 1)"
    if end > total_pages:
        return False, f"Página final {end} excede el total de páginas ({total_pages})"
    if start > end:
        return False, f"Página inicial ({start}) no puede ser mayor que la final ({end})"
    return True, ""


def validate_new_order(new_order: List[int], total_pages: int) -> tuple[bool, str]:
    """
    Valida una lista de nuevo orden para páginas.
    
    Args:
        new_order: Lista con el nuevo orden de páginas (1-indexed)
        total_pages: Total de páginas en el documento
        
    Returns:
        tuple: (es_válido, mensaje_error)
    """
    if len(new_order) != total_pages:
        return False, f"La lista debe tener {total_pages} elementos, tiene {len(new_order)}"
    
    seen = set()
    for p in new_order:
        if p < 1 or p > total_pages:
            return False, f"Número de página inválido: {p} (debe estar entre 1 y {total_pages})"
        if p in seen:
            return False, f"Página duplicada: {p}"
        seen.add(p)
    
    return True, ""


# =============================================================================
# TRANSFORMACIONES
# =============================================================================

def rotate_pages(files: List[str], degrees: int = 90, pages: List[int] = None) -> Dict[str, Any]:
    """
    Rota páginas del PDF.
    
    Args:
        files: Lista de rutas de PDFs
        degrees: Grados de rotación (90, 180, 270)
        pages: Lista de números de página a rotar (None = todas)
        
    Returns:
        dict: Resultado de la operación
    """
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
                        # Obtener rotación actual (manejar diferentes tipos)
                        current_rotation = 0
                        if '/Rotate' in page:
                            rot_obj = page['/Rotate']
                            # Puede ser int o indirect object
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
    """
    Reordena las páginas de un PDF.
    
    Args:
        files: Lista de rutas de PDFs
        new_order: Lista con el nuevo orden de páginas (1-indexed)
        
    Returns:
        dict: Resultado de la operación
    """
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
            
            # Validar que los números de página sean válidos
            for p in new_order:
                if p < 1 or p > num_pages:
                    return {'success': False, 'error': f'Número de página inválido: {p}', 'output_files': []}
            
            # Reordenar según el nuevo orden
            for new_pos in new_order:
                page = reader.pages[new_pos - 1]  # Convertir a 0-indexed
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
    """
    Combina múltiples PDFs en uno.
    
    Args:
        files: Lista de rutas de PDFs a combinar
        output_path: Ruta de salida (opcional)
        
    Returns:
        dict: Resultado de la operación
    """
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
    
    # Determinar ruta de salida
    if output_path is None:
        first_file = files[0]
        output_path = get_output_path(first_file, '_merged')
    
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
    """
    Extrae páginas específicas de un PDF.
    
    Args:
        files: Lista de rutas de PDFs
        pages: Lista de números de página a extraer (1-indexed)
        
    Returns:
        dict: Resultado de la operación
    """
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
# EXTRACCIÓN DE PÁGINAS (NUEVAS FUNCIONES)
# =============================================================================

def extract_page(files: List[str], page_number: int) -> Dict[str, Any]:
    """
    Extrae una página específica de un PDF.
    
    Args:
        files: Lista de rutas de PDFs
        page_number: Número de página a extraer (1-indexed)
        
    Returns:
        dict: Resultado de la operación
    """
    if not check_pypdf():
        return {'success': False, 'error': 'pypdf no está instalado', 'output_files': []}
    
    return extract_range(files, start=page_number, end=page_number)


def extract_range(files: List[str], start_page: int, end_page: int) -> Dict[str, Any]:
    """
    Extrae un rango de páginas de un PDF.
    
    Args:
        files: Lista de rutas de PDFs
        start_page: Página inicial (1-indexed)
        end_page: Página final (1-indexed)
        
    Returns:
        dict: Resultado de la operación
    """
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
            
            # Validar rango
            valid, error_msg = validate_page_range(start_page, end_page, num_pages)
            if not valid:
                errors.append(f"Error en {os.path.basename(file_path)}: {error_msg}")
                continue
            
            # Extraer páginas en el rango
            for i in range(start_page - 1, end_page):  # Convertir a 0-indexed
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
    """
    Reordena las páginas de un PDF con validación mejorada.
    
    Args:
        files: Lista de rutas de PDFs
        new_order: Lista con el nuevo orden de páginas (1-indexed)
        
    Returns:
        dict: Resultado de la operación
    """
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
            
            # Validar nuevo orden
            valid, error_msg = validate_new_order(new_order, num_pages)
            if not valid:
                errors.append(f"Error en {os.path.basename(file_path)}: {error_msg}")
                continue
            
            # Reordenar según el nuevo orden
            for new_pos in new_order:
                page = reader.pages[new_pos - 1]  # Convertir a 0-indexed
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