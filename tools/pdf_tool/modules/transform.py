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
from core.utils import get_output_path

logger = logging.getLogger(__name__)


# =============================================================================
# VALIDACIÓN
# =============================================================================

def check_pypdf() -> bool:
    """Verifica si pypdf está instalado."""
    return PdfReader is not None


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