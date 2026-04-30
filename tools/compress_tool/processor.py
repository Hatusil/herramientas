"""
Processor: Funciones para comprimir y descomprimir archivos.
"""
import zipfile
import tarfile
import os
from pathlib import Path
from typing import List, Dict, Any


def compress_to_zip(files: List[str], output_path: str = None, level: int = 6) -> Dict[str, Any]:
    """
    Comprime archivos a formato ZIP.
    
    Args:
        files: Lista de archivos a comprimir
        output_path: Ruta de salida (opcional)
        level: Nivel de compresión (0-9)
        
    Returns:
        dict: Resultado
    """
    if not files:
        return {'success': False, 'error': 'No hay archivos', 'output_files': []}
    
    try:
        # Determinar nombre de salida
        if output_path is None:
            first_file = files[0]
            output_path = Path(first_file).parent / f"{Path(first_file).stem}_compressed.zip"
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=level) as zf:
            for f in files:
                if os.path.isfile(f):
                    zf.write(f, arcname=os.path.basename(f))
                elif os.path.isdir(f):
                    for root, dirs, filenames in os.walk(f):
                        for filename in filenames:
                            file_path = os.path.join(root, filename)
                            arcname = os.path.relpath(file_path, os.path.dirname(f))
                            zf.write(file_path, arcname=arcname)
        
        return {
            'success': True,
            'message': f'Creado: {os.path.basename(output_path)}',
            'output_files': [output_path],
            'error': None
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e), 'output_files': []}


def compress_to_tar(files: List[str], output_path: str = None, compression: str = 'gz') -> Dict[str, Any]:
    """
    Comprime archivos a formato TAR.
    
    Args:
        files: Lista de archivos a comprimir
        output_path: Ruta de salida
        compression: None, 'gz', 'bz2', 'xz'
        
    Returns:
        dict: Resultado
    """
    if not files:
        return {'success': False, 'error': 'No hay archivos', 'output_files': []}
    
    try:
        if output_path is None:
            first_file = files[0]
            output_path = Path(first_file).parent / f"{Path(first_file).stem}.tar"
        
        mode = f'w:{compression}' if compression else 'w'
        
        with tarfile.open(output_path, mode) as tf:
            for f in files:
                tf.add(f, arcname=os.path.basename(f))
        
        return {
            'success': True,
            'message': f'Creado: {os.path.basename(output_path)}',
            'output_files': [output_path],
            'error': None
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e), 'output_files': []}


def decompress_zip(zip_path: str, output_dir: str = None) -> Dict[str, Any]:
    """
    Extrae un archivo ZIP.
    """
    if not os.path.exists(zip_path):
        return {'success': False, 'error': 'Archivo no encontrado', 'output_files': []}
    
    try:
        if output_dir is None:
            output_dir = os.path.splitext(zip_path)[0]
        
        os.makedirs(output_dir, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(output_dir)
        
        return {
            'success': True,
            'message': f'Extraídos en: {output_dir}',
            'output_files': [output_dir],
            'error': None
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e), 'output_files': []}


def decompress_tar(tar_path: str, output_dir: str = None) -> Dict[str, Any]:
    """
    Extrae un archivo TAR.
    """
    if not os.path.exists(tar_path):
        return {'success': False, 'error': 'Archivo no encontrado', 'output_files': []}
    
    try:
        if output_dir is None:
            output_dir = os.path.splitext(tar_path)[0]
        
        os.makedirs(output_dir, exist_ok=True)
        
        with tarfile.open(tar_path, 'r:*') as tf:
            tf.extractall(output_dir)
        
        return {
            'success': True,
            'message': f'Extraídos en: {output_dir}',
            'output_files': [output_dir],
            'error': None
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e), 'output_files': []}


def list_zip_contents(zip_path: str) -> Dict[str, Any]:
    """Lista contenido de un ZIP."""
    if not os.path.exists(zip_path):
        return {'success': False, 'error': 'Archivo no encontrado'}
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            files = zf.namelist()
            total_size = sum(zf.getinfo(f).file_size for f in files)
            
        return {
            'success': True,
            'files': files,
            'count': len(files),
            'total_size': total_size
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}