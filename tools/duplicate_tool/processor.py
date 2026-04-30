"""
Processor: Encontrar archivos duplicados.
"""
import logging
import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any

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