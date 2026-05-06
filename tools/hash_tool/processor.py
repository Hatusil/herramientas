"""
Processor: Funciones para calcular y verificar checksums.
"""
import hashlib
import os
from typing import List, Dict, Any

# Importar validación de core (máxima C2: Consistency)
from core.utils import validate_input_file, validate_file_size

# Métricas
from core.metrics import Counter, Timer, increment

MAX_HASH_SIZE_MB = 10000  # 10GB max for hash calculation

# Contadores de operaciones
hash_operations_total = Counter('hash_operations_total')
hash_errors = Counter('hash_errors')


def calculate_hash(file_path: str, algorithm: str = 'sha256') -> Dict[str, Any]:
    """
    Calcula el hash de un archivo.
    
    Args:
        file_path: Ruta al archivo
        algorithm: md5, sha1, sha256, sha512
        
    Returns:
        dict: hash calculado
    """
    with Timer('hash_tool.calculate_hash'):
        if not os.path.exists(file_path):
            increment('hash_errors')
            return {'success': False, 'error': 'Archivo no encontrado'}
        
        algorithms = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'sha512': hashlib.sha512
        }
        
        if algorithm not in algorithms:
            increment('hash_errors')
            return {'success': False, 'error': f'Algoritmo no soportado: {algorithm}'}
        
        try:
            hasher = algorithms[algorithm]()
            
            with open(file_path, 'rb') as f:
                # Leer en chunks para archivos grandes
                for chunk in iter(lambda: f.read(8192), b''):
                    hasher.update(chunk)
            
            hash_value = hasher.hexdigest()
            
            increment('hash_operations_total')
            
            return {
                'success': True,
                'file_name': os.path.basename(file_path),
                'file_size': os.path.getsize(file_path),
                'algorithm': algorithm,
                'hash': hash_value
            }
            
        except Exception as e:
            increment('hash_errors')
            return {'success': False, 'error': str(e)}


def calculate_all_hashes(file_path: str) -> Dict[str, Any]:
    """
    Calcula todos los hashes de un archivo.
    """
    if not os.path.exists(file_path):
        return {'success': False, 'error': 'Archivo no encontrado'}
    
    try:
        hashes = {}
        
        for algo in ['md5', 'sha1', 'sha256', 'sha512']:
            hasher = hashlib.new(algo)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hasher.update(chunk)
            hashes[algo] = hasher.hexdigest()
        
        return {
            'success': True,
            'file_name': os.path.basename(file_path),
            'file_size': os.path.getsize(file_path),
            'hashes': hashes
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


def verify_hash(file_path: str, expected_hash: str, algorithm: str = 'sha256') -> Dict[str, Any]:
    """
    Verifica que el hash de un archivo coincida con el esperado.
    """
    with Timer('hash_tool.verify_hash'):
        result = calculate_hash(file_path, algorithm)
        
        if not result['success']:
            increment('hash_errors')
            return result
        
        match = result['hash'].lower() == expected_hash.lower()
        
        increment('hash_operations_total')
        
        return {
            'success': True,
            'match': match,
            'expected': expected_hash,
            'actual': result['hash'],
            'algorithm': algorithm,
            'file_name': result['file_name']
        }


def calculate_file_hash_list(files: List[str], algorithm: str = 'sha256') -> Dict[str, Any]:
    """
    Calcula hashes de una lista de archivos.
    """
    results = []
    
    for file_path in files:
        if not os.path.exists(file_path):
            continue
            
        result = calculate_hash(file_path, algorithm)
        if result['success']:
            results.append(result)
    
    return {
        'success': True,
        'files': results,
        'count': len(results)
    }