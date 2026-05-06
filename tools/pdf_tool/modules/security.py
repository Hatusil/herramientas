"""
Módulo de seguridad para PDFs.
Proporciona funciones para encriptar y desencriptar archivos PDF.
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

def _validate_encryption_password(password: str) -> bool:
    """
    Valida la contraseña para encriptación de PDF.
    
    Args:
        password: Contraseña a validar
        
    Returns:
        bool: True si la contraseña es válida
    """
    if not password or len(password) < 4 or len(password) > 64:
        return False
    return True


# =============================================================================
# SEGURIDAD
# =============================================================================

def encrypt_pdf(files: List[str], password: str) -> Dict[str, Any]:
    """
    Bloquea un PDF con contraseña.
    
    Args:
        files: Lista de rutas de PDFs
        password: Contraseña para bloquear (4-64 caracteres)
        
    Returns:
        dict: Resultado de la operación
    """
    if not check_pypdf():
        return {'success': False, 'error': 'pypdf no está instalado', 'output_files': []}
    
    # Validar contraseña
    if not _validate_encryption_password(password):
        return {'success': False, 'error': 'Contraseña inválida: debe tener entre 4 y 64 caracteres', 'output_files': []}
    
    output_files = []
    errors = []
    
    for file_path in files:
        if not os.path.exists(file_path):
            errors.append(f"Archivo no encontrado: {file_path}")
            continue
        
        try:
            reader = PdfReader(file_path)
            
            if reader.is_encrypted:
                errors.append(f"{file_path} ya está encriptado")
                continue
            
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            
            writer.encrypt(password)
            
            output_path = get_output_path(file_path, '_locked')
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"PDF bloqueado: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Bloqueados {len(output_files)}/{len(files)} PDFs",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }


def decrypt_pdf(files: List[str], password: str) -> Dict[str, Any]:
    """
    Desbloquea un PDF con contraseña.
    
    Args:
        files: Lista de rutas de PDFs
        password: Contraseña para desbloquear
        
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
            
            if not reader.is_encrypted:
                errors.append(f"{file_path} no está encriptado")
                continue
            
            # Intentar descifrar
            result = reader.decrypt(password)
            
            if result == 0:
                errors.append(f"Contraseña incorrecta para {file_path}")
                continue
            
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            
            output_path = get_output_path(file_path, '_unlocked')
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
            logger.info(f"PDF desbloqueado: {file_path}")
            
        except Exception as e:
            errors.append(f"Error en {os.path.basename(file_path)}: {str(e)}")
    
    success = len(output_files) > 0
    return {
        'success': success,
        'message': f"Desbloqueados {len(output_files)}/{len(files)} PDFs",
        'output_files': output_files,
        'error': '; '.join(errors) if errors else None
    }