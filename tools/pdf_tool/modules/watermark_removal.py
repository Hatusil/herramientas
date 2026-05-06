"""
Módulo de eliminación de watermarks visuales para PDFs.
Utiliza Fitz (PyMuPDF MIT) para detectar y eliminar watermarks mergeados
en el contenido visual de las páginas (no solo anotaciones).
"""
import logging
import os
from typing import List, Dict, Any, Tuple, Optional

# Importar función compartida de core
from core.utils import get_output_path

logger = logging.getLogger(__name__)

# Intentar importar Fitz (PyMuPDF MIT)
try:
    import fitz
except ImportError:
    fitz = None


# =============================================================================
# VALIDACIÓN
# =============================================================================

def check_fitz() -> bool:
    """Verifica si Fitz está instalado."""
    return fitz is not None


def _is_watermark_region(x: float, y: float, width: float, height: float, 
                        page_width: float, page_height: float) -> bool:
    """
    Determina si una región es probablemente un watermark.
    
    Usa heurísticas: watermarks suelen ser pequeños comparado con la página,
    posicionados en el centro o diagonales, y con texto repetitivo.
    
    Args:
        x, y: Coordenadas de la región
        width, height: Dimensiones de la región
        page_width, page_height: Dimensiones de la página
        
    Returns:
        bool: True si la región es probablemente un watermark
    """
    # Calcular área relativa
    area_ratio = (width * height) / (page_width * page_height)
    
    # Watermarks típicos ocupan menos del 50% de la página
    if area_ratio > 0.5:
        return False
    
    # Verificar posición: centro o esquinas (posiciones típicas de watermarks)
    center_x = page_width / 2
    center_y = page_height / 2
    
    # Distancia al centro
    dist_to_center = ((x + width/2 - center_x)**2 + 
                      (y + height/2 - center_y)**2) ** 0.5
    
    # Normalizar por tamaño de página
    normalized_dist = dist_to_center / ((page_width**2 + page_height**2) ** 0.5)
    
    # Si está cerca del centro o en posición diagonal, es probable watermark
    if normalized_dist < 0.3:  # Cerca del centro
        return True
    
    # Esquina superior o inferior
    margin = page_width * 0.1
    if x < margin or x > page_width - width - margin:
        if y < margin or y > page_height - height - margin:
            return True
    
    return False


# =============================================================================
# DETECCIÓN DE WATERMARKS
# =============================================================================

def detect_watermarks(page) -> List[Dict[str, Any]]:
    """
    Detecta contenido de watermark en una página PDF.
    
    Analiza los objetos en la página para identificar elementos que son
    probablemente watermarks (texto pequeño, repetido, en posiciones típicas).
    
    Args:
        page: Objeto página de Fitz
        
    Returns:
        Lista de regiones con posibles watermarks:
        [{'x': float, 'y': float, 'width': float, 'height': float, 
          'type': str, 'text': str}, ...]
    """
    if not check_fitz():
        return []
    
    watermark_regions = []
    
    page_width = page.rect.width
    page_height = page.rect.height
    
    # Obtener todos los objetos en la página
    try:
        # Obtener imágenes
        image_list = page.get_images(full=True)
        for img in image_list:
            xref = img[0]
            rects = page.get_image_rects(xref)
            for rect in rects:
                if _is_watermark_region(rect.x0, rect.y0, rect.width, rect.height,
                                       page_width, page_height):
                    watermark_regions.append({
                        'x': rect.x0,
                        'y': rect.y0,
                        'width': rect.width,
                        'height': rect.height,
                        'type': 'image',
                        'text': ''
                    })
        
        # Obtener texto por bloques
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        for block in blocks.get('blocks', []):
            if block.get('type') == 0:  # Texto
                bbox = block.get('bbox', [0, 0, 0, 0])
                x, y, w, h = bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]
                
                if _is_watermark_region(x, y, w, h, page_width, page_height):
                    # Extraer texto
                    text = block.get('text', '').strip()
                    if len(text) > 0:
                        watermark_regions.append({
                            'x': x,
                            'y': y,
                            'width': w,
                            'height': h,
                            'type': 'text',
                            'text': text[:100]  # Limitar longitud
                        })
    
    except Exception as e:
        logger.warning(f"Error detectando watermarks en página: {e}")
    
    return watermark_regions


def detect_watermarks_auto(pdf_document) -> List[Dict[str, Any]]:
    """
    Detecta automáticamente watermarks en todo el documento.
    
    Usa heurística: contenido pequeño repetido en múltiples páginas
    es probablemente un watermark.
    
    Args:
        pdf_document: Documento Fitz
        
    Returns:
        Lista de regiones de watermarks detectados:
        [{'page': int, 'x': float, 'y': float, 'width': float, 'height': float}, ...]
    """
    if not check_fitz():
        return []
    
    # Recolectar todas las regiones de todas las páginas
    all_regions = []
    
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        regions = detect_watermarks(page)
        
        for region in regions:
            region['page'] = page_num
            all_regions.append(region)
    
    # Agrupar regiones similares (mismo tamaño y posición aproximada)
    # Watermarks típicos aparecen en todas o muchas páginas
    similar_groups = {}
    
    for region in all_regions:
        key = (round(region['width'], 1), round(region['height'], 1))
        if key not in similar_groups:
            similar_groups[key] = []
        similar_groups[key].append(region)
    
    # Filtrar: grupos con muchas páginas = watermarks
    page_count = len(pdf_document)
    detected_watermarks = []
    
    for key, regions in similar_groups.items():
        if len(regions) >= page_count * 0.5:  # En al menos 50% de las páginas
            # Tomar la primera como representativa
            detected_watermarks.append(regions[0])
    
    return detected_watermarks


def detect_watermarks_manual(page, x: float, y: float, 
                             width: float, height: float) -> List[Dict[str, Any]]:
    """
    Define manualmente una región de watermark a remover.
    
    Args:
        page: Objeto página de Fitz
        x, y: Coordenadas de la esquina superior izquierda
        width, height: Dimensiones de la región
        
    Returns:
        Lista con la región definida (siempre retornará la región especificada)
    """
    return [{
        'x': x,
        'y': y,
        'width': width,
        'height': height,
        'type': 'manual',
        'text': ''
    }]


# =============================================================================
# REMOCIÓN DE WATERMARKS
# =============================================================================

def remove_watermark_from_page(page, watermark_regions: List[Dict[str, Any]]) -> bool:
    """
    Remueve las regiones de watermark de una página.
    
    Args:
        page: Objeto página de Fitz
        watermark_regions: Lista de regiones a remover
        
    Returns:
        bool: True si se removió correctamente
    """
    if not check_fitz():
        return False
    
    try:
        for region in watermark_regions:
            x = region['x']
            y = region['y']
            width = region['width']
            height = region['height']
            
            # Crear rectángulo de la región
            rect = fitz.Rect(x, y, x + width, y + height)
            
            # Eliminar contenido en esa región
            # Primero probar con redact (más preciso)
            page.add_redact_annot(rect, fill=(1, 1, 1))  # Blanco como fondo
        
        # Aplicar-redact elimina el contenido y llena con color
        page.apply_redactions(images=fitz.PDF_REdaction_IMAGE_REMOVE)
        
        return True
        
    except Exception as e:
        logger.warning(f"Error removiendo watermark de página: {e}")
        return False


# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

def remove_watermark(files: List[str], **options) -> Dict[str, Any]:
    """
    Elimina watermarks visuales de PDFs.
    
    Args:
        files: Lista de rutas de PDFs
        **options:
            - detection_mode: 'auto' | 'manual' (default: 'auto')
            - preserve_layout: bool (default: True)
            - manual_region: dict con x, y, width, height (para modo manual)
            
    Returns:
        dict: Resultado de la operación
    """
    if not check_fitz():
        return {
            'success': False, 
            'error': 'Fitz (PyMuPDF) no está instalado', 
            'output_files': []
        }
    
    detection_mode = options.get('detection_mode', 'auto')
    preserve_layout = options.get('preserve_layout', True)
    manual_region = options.get('manual_region', None)
    
    output_files = []
    errors = []
    
    for file_path in files:
        if not os.path.exists(file_path):
            errors.append(f"Archivo no encontrado: {file_path}")
            continue
        
        try:
            # Abrir documento
            doc = fitz.open(file_path)
            
            if detection_mode == 'auto':
                # Detección automática de watermarks
                watermark_regions = detect_watermarks_auto(doc)
                
                if not watermark_regions:
                    logger.info(f"No se detectaron watermarks en {file_path}")
                    # Copiar archivo sin cambios
                    output_path = get_output_path(file_path, '_clean')
                    doc.save(output_path)
                    doc.close()
                    output_files.append(output_path)
                    continue
                
                # Procesar páginas
                for page_num in watermark_regions:
                    region = next(r for r in watermark_regions if r.get('page') == page_num)
                    if region:
                        page = doc[page_num]
                        remove_watermark_from_page(page, [region])
                
            else:
                # Detección manual: usar región especificada
                if not manual_region:
                    errors.append(f"Región manual no especificada para {file_path}")
                    continue
                
                for page in doc:
                    remove_watermark_from_page(page, [manual_region])
            
            # Guardar resultado
            output_path = get_output_path(file_path, '_no_wm')
            doc.save(output_path)
            doc.close()
            
            output_files.append(output_path)
            logger.info(f"Watermark removido: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Watermark removido de {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


# =============================================================================
# FALLBACK A PYPDF (ANNOTATIONS)
# =============================================================================

def remove_watermark_fallback(files: List[str]) -> Dict[str, Any]:
    """
    Elimina solo anotaciones (/Annots) usando pypdf.
    
    Esta es la función de fallback cuando no se pueden remover watermarks visuales.
    
    Args:
        files: Lista de rutas de PDFs
        
    Returns:
        dict: Resultado de la operación
    """
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        return {
            'success': False,
            'error': 'pypdf no está instalado',
            'output_files': []
        }
    
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
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Anotaciones eliminadas de {len(output_files)}/{len(files)} archivos",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }