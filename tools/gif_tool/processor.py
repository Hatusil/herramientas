"""
Processor: Crear GIFs animados.
"""
import os
from pathlib import Path
from PIL import Image, ImageSequence
from typing import List, Dict, Any

# Importar función compartida de core (máxima C2: Consistency)
from core.utils import get_output_path, get_output_path_format
from core.file_utils import validate_input_file

# Métricas
from core.metrics import Counter, Timer, increment

# Contadores de operaciones
gif_operations_total = Counter('gif_operations_total')
gif_errors = Counter('gif_errors')


def create_gif(image_paths: List[str], output_path: str = None, duration: int = 500, loop: int = 0) -> Dict[str, Any]:
    """
    Crea un GIF animado desde una lista de imágenes.
    
    Args:
        image_paths: Lista de rutas de imágenes
        output_path: Ruta de salida (opcional)
        duration: Duración de cada frame en ms
        loop: Veces que repite (0 = infinito)
        
    Returns:
        dict: Resultado
    """
    with Timer('gif_tool.create_gif'):
        if not image_paths:
            increment('gif_errors')
            return {'success': False, 'error': 'No hay imágenes', 'output_files': []}
        
        # Verificar si cada imagen ya es GIF
        skipped = []
        valid_images = []
        for path in image_paths:
            if path.lower().endswith('.gif'):
                skipped.append(f"{Path(path).name} - Ya es GIF")
            else:
                valid_images.append(path)
        
        # Skip si todos son GIFs
        if not valid_images:
            increment('gif_operations_total')
            return {
                'success': True,
                'message': f'Todas las entradas ya son GIF ({len(skipped)} omitidos)',
                'output_files': [],
                'skipped': skipped,
                'error': None
            }
        
        try:
            # Abrir todas las imágenes
            images = []
            for path in image_paths:
                try:
                    img = Image.open(path)
                    # Convertir a modo compatible con GIF
                    if img.mode != 'RGBA' and img.mode != 'RGB':
                        img = img.convert('RGBA')
                    images.append(img)
                except Exception:
                    continue
            
            if not images:
                increment('gif_errors')
                return {'success': False, 'error': 'No se pudieron cargar imágenes', 'output_files': []}
            
            # Redimensionar todas al mismo tamaño (la primera)
            first_size = images[0].size
            resized = []
            for img in images:
                if img.size != first_size:
                    img = img.resize(first_size, Image.LANCZOS)
                resized.append(img)
            
            # Determinar output usando get_output_path (máxima C2: Consistency)
            if output_path is None:
                output_path = get_output_path(image_paths[0], '_animated')
            
            # Guardar como GIF
            resized[0].save(
                output_path,
                save_all=True,
                append_images=resized[1:],
                duration=duration,
                loop=loop,
                optimize=True
            )
            
            increment('gif_operations_total')
            
            return {
                'success': True,
                'message': f'GIF creado: {Path(output_path).name}',
                'output_files': [output_path],
                'skipped': skipped if skipped else None,
                'error': None
            }
            
        except Exception as e:
            increment('gif_errors')
            return {'success': False, 'error': str(e), 'output_files': []}


def extract_frames(gif_path: str, output_dir: str = None) -> Dict[str, Any]:
    """
    Extrae los frames de un GIF.
    """
    with Timer('gif_tool.extract_frames'):
        if not os.path.exists(gif_path):
            increment('gif_errors')
            return {'success': False, 'error': 'Archivo no encontrado', 'output_files': []}
        
        # Skip if input is already an image format (not gif)
        ext = os.path.splitext(gif_path)[1].lower()
        image_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.ico'}
        if ext in image_exts:
            increment('gif_errors')
            return {'success': False, 'error': 'Entrada es imagen, no gif', 'output_files': []}
        
        try:
            gif = Image.open(gif_path)
            
            # Usar get_output_path para consistencia (máxima C2)
            if output_dir is None:
                output_dir = get_output_path_format(gif_path, '_frames', '')
            
            os.makedirs(output_dir, exist_ok=True)
            
            frames = []
            for i, frame in enumerate(ImageSequence.Iterator(gif)):
                frame_path = os.path.join(output_dir, f"frame_{i:03d}.png")
                frame.save(frame_path)
                frames.append(frame_path)
            
            gif.close()
            
            increment('gif_operations_total')
            
            return {
                'success': True,
                'message': f'Extraídos {len(frames)} frames',
                'output_files': frames,
                'error': None
            }
            
        except Exception as e:
            increment('gif_errors')
            return {'success': False, 'error': str(e), 'output_files': []}


def get_gif_info(gif_path: str) -> Dict[str, Any]:
    """Obtiene información de un GIF."""
    if not os.path.exists(gif_path):
        return {'success': False, 'error': 'Archivo no encontrado'}
    
    try:
        gif = Image.open(gif_path)
        
        info = {
            'success': True,
            'file_name': os.path.basename(gif_path),
            'file_size': os.path.getsize(gif_path),
            'size': gif.size,
            'mode': gif.mode,
            'frames': 0,
            'duration': 0
        }
        
        # Contar frames
        try:
            while True:
                info['frames'] += 1
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass
        
        # Duración total
        if 'duration' in gif.info:
            info['duration'] = gif.info['duration'] * info['frames']
        
        # Loop
        info['loops'] = gif.info.get('loop', 'infinite')
        
        gif.close()
        
        return info
        
    except Exception as e:
        return {'success': False, 'error': str(e)}