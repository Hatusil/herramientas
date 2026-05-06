"""
Processor: Encontrar archivos duplicados.
"""
import logging
import os
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional

logger = logging.getLogger(__name__)


def find_duplicates_by_hash(folder_path: str, extensions: List[str] = None) -> Dict[str, Any]:
    """
    Encuentra archivos duplicados comparando hashes.
    
    Args:
        folder_path: Carpeta a escanear
        extensions: Lista de extensiones a incluir (ej: ['.jpg', '.png'])
        
    Returns:
        dict: Archivos duplicados encontrados
    """
    if not os.path.exists(folder_path):
        return {'success': False, 'error': 'Carpeta no encontrada'}
    
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.mp3', '.mp4', '.pdf', '.doc', '.docx', '.xls', '.xlsx']
    
    # Diccionario de hash -> lista de archivos
    hash_dict: Dict[str, List[str]] = {}
    
    # Escanear carpeta
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            ext = Path(filename).suffix.lower()
            if ext not in extensions:
                continue
            
            file_path = os.path.join(root, filename)
            
            try:
                # Calcular hash del archivo
                hasher = hashlib.sha256()
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(8192), b''):
                        hasher.update(chunk)
                
                file_hash = hasher.hexdigest()
                
                if file_hash not in hash_dict:
                    hash_dict[file_hash] = []
                hash_dict[file_hash].append(file_path)
                
            except Exception as e:
                # Loguear error pero continuar con otros archivos
                logger.debug(f"Error procesando {file_path}: {e}")
                continue
    
    # Filtrar solo duplicados (más de un archivo con el mismo hash)
    duplicates = {h: files for h, files in hash_dict.items() if len(files) > 1}
    
    return {
        'success': True,
        'duplicates': duplicates,
        'count': len(duplicates),
        'total_duplicates': sum(len(files) - 1 for files in duplicates.values())
    }


def find_duplicates_by_size(folder_path: str) -> Dict[str, Any]:
    """
    Encuentra archivos duplicados por tamaño (más rápido).
    """
    if not os.path.exists(folder_path):
        return {'success': False, 'error': 'Carpeta no encontrada'}
    
    size_dict: Dict[int, List[str]] = {}
    
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                size = os.path.getsize(file_path)
                if size == 0:
                    continue
                    
                if size not in size_dict:
                    size_dict[size] = []
                size_dict[size].append(file_path)
            except Exception as e:
                logger.debug(f"Error processing file: {e}")
                continue
    
    # Solo archivos con mismo tamaño
    potential = {s: files for s, files in size_dict.items() if len(files) > 1}
    
    return {
        'success': True,
        'potential_duplicates': potential,
        'count': len(potential),
        'total_files': sum(len(files) for files in potential.values())
    }


def _hash_file_worker(file_path: str) -> tuple:
    """
    Worker function para calcular hash de un archivo en paralelo.
    
    Args:
        file_path: Ruta del archivo a hashear
        
    Returns:
        tuple: (file_path, file_hash) o (file_path, None) en caso de error
    """
    try:
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return (file_path, hasher.hexdigest())
    except Exception as e:
        logger.debug(f"Error hashing {file_path}: {e}")
        return (file_path, None)


def find_duplicates_async(
    folder_path: str,
    extensions: List[str] = None,
    max_workers: int = 4,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> Dict[str, Any]:
    """
    Encuentra archivos duplicados usando hashing paralelo con ThreadPoolExecutor.
    
    Args:
        folder_path: Carpeta a escanear
        extensions: Lista de extensiones a incluir (ej: ['.jpg', '.png'])
        max_workers: Número de workers paralelos (default: 4)
        progress_callback: Función callback para progreso (completed, total)
        
    Returns:
        dict: Archivos duplicados encontrados
    """
    if not os.path.exists(folder_path):
        return {'success': False, 'error': 'Carpeta no encontrada'}
    
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.mp3', '.mp4', '.pdf', '.doc', '.docx', '.xls', '.xlsx']
    
    # Recolectar archivos a procesar
    files_to_hash: List[str] = []
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            ext = Path(filename).suffix.lower()
            if ext in extensions:
                files_to_hash.append(os.path.join(root, filename))
    
    total_files = len(files_to_hash)
    if total_files == 0:
        return {'success': True, 'duplicates': {}, 'count': 0, 'total_duplicates': 0}
    
    # Diccionario de hash -> lista de archivos
    hash_dict: Dict[str, List[str]] = {}
    completed = 0
    
    # Procesar archivos en paralelo
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit todos los trabajos
        future_to_file = {
            executor.submit(_hash_file_worker, file_path): file_path 
            for file_path in files_to_hash
        }
        
        # Recolectar resultados
        for future in as_completed(future_to_file):
            file_path, file_hash = future.result()
            completed += 1
            
            # Reportar progreso
            if progress_callback:
                progress_callback(completed, total_files)
            
            # Agregar al diccionario de hashes
            if file_hash is not None:
                if file_hash not in hash_dict:
                    hash_dict[file_hash] = []
                hash_dict[file_hash].append(file_path)
    
    # Filtrar solo duplicados (más de un archivo con el mismo hash)
    duplicates = {h: files for h, files in hash_dict.items() if len(files) > 1}
    
    return {
        'success': True,
        'duplicates': duplicates,
        'count': len(duplicates),
        'total_duplicates': sum(len(files) - 1 for files in duplicates.values())
    }