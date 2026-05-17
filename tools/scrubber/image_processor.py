"""
Processor para imágenes - limpieza de metadatos EXIF.
Separado de processor.py por SRP (máxima R0: clases <300 líneas).
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any

from core.utils import get_output_path
from core.metrics import Counter, Timer, increment

logger = logging.getLogger(__name__)

scrubber_operations_total = Counter('scrubber_operations_total')
scrubber_errors = Counter('scrubber_errors')


def get_image_metadata(file_path: str) -> Dict[str, Any]:
    """Obtiene metadatos EXIF de una imagen."""
    if not os.path.exists(file_path):
        return {'success': False, 'error': 'Archivo no encontrado'}
    
    ext = Path(file_path).suffix.lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.tiff', '.webp']:
        return {'success': False, 'error': 'Formato no soportado para imágenes'}
    
    try:
        from PIL import Image
        
        with Image.open(file_path) as img:
            info = {}
            
            exif_data = img.getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    try:
                        tag_name = str(tag_id)
                        info[f'EXIF_{tag_name}'] = str(value)[:100]
                    except Exception as e:
                        logger.warning(f"Error reading EXIF tag {tag_id}: {e}")
            
            info['format'] = img.format
            info['size'] = img.size
            info['mode'] = img.mode
            
            has_exif = len(exif_data) > 0 if exif_data else False
            
            try:
                exif = img.getexif()
                if exif:
                    if 0x9003 in exif:
                        info['date_taken'] = str(exif[0x9003])
                    if 0x010F in exif:
                        info['camera_make'] = str(exif[0x010F])
                    if 0x0110 in exif:
                        info['camera_model'] = str(exif[0x0110])
                    if 0x8825 in exif:
                        info['has_gps'] = True
            except Exception as e:
                logger.warning(f"Error getting EXIF metadata: {e}")
            
            return {
                'success': True,
                'file_name': os.path.basename(file_path),
                'has_exif': has_exif,
                'metadata': info
            }
            
    except Exception as e:
        logger.error(f"Error leyendo metadatos de imagen: {e}")
        return {'success': False, 'error': str(e)}


def clean_image_metadata(file_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
    """Limpia metadatos de una imagen."""
    with Timer('scrubber.clean_image_metadata'):
        if options is None:
            options = {}
        
        if not os.path.exists(file_path):
            increment('scrubber_errors')
            return {'success': False, 'error': 'Archivo no encontrado', 'output_files': []}
        
        ext = Path(file_path).suffix.lower()
        if ext not in ['.jpg', '.jpeg']:
            increment('scrubber_errors')
            return {'success': False, 'error': 'Solo se soporta JPG/JPEG para eliminar EXIF', 'output_files': []}
        
        try:
            try:
                import piexif
                
                try:
                    exif_dict = piexif.load(file_path)
                except Exception as e:
                    logger.warning(f"Could not load existing EXIF: {e}")
                    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
                
                remove_all = options.get('remove_all', True)
                
                if remove_all:
                    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
                else:
                    if options.get('remove_gps', False):
                        exif_dict['GPS'] = {}
                    if options.get('remove_date', False):
                        if '0th' in exif_dict and piexif.ImageIFD.DateTime in exif_dict['0th']:
                            del exif_dict['0th'][piexif.ImageIFD.DateTime]
                
                exif_bytes = piexif.dump(exif_dict)
                
                from PIL import Image
                with Image.open(file_path) as img:
                    output_path = get_output_path(file_path, '_clean', _exists_ok=False)
                    img.save(output_path, "jpeg", exif=exif_bytes, quality=95)
                
                increment('scrubber_operations_total')
                
                return {
                    'success': True,
                    'message': 'Metadatos eliminados',
                    'output_files': [output_path],
                    'error': None
                }
                
            except ImportError:
                from PIL import Image
                with Image.open(file_path) as img:
                    output_path = get_output_path(file_path, '_clean', _exists_ok=False)
                    data = list(img.getdata())
                    img_no_exif = Image.new(img.mode, img.size)
                    img_no_exif.putdata(data)
                    img_no_exif.save(output_path, "JPEG", quality=95)
                
                increment('scrubber_operations_total')
                
                return {
                    'success': True,
                    'message': 'EXIF eliminado (sin piexif)',
                    'output_files': [output_path],
                    'error': None
                }
                
        except Exception as e:
            increment('scrubber_errors')
            logger.error(f"Error limpiando metadatos: {e}")
            return {'success': False, 'error': str(e), 'output_files': []}