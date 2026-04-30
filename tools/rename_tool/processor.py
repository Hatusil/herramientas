"""
Processor: Funciones para renombrar archivos en masa.
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Any


def rename_with_prefix(files: List[str], prefix: str) -> Dict[str, Any]:
    """Agregar prefijo a archivos."""
    renamed = []
    errors = []
    
    for f in files:
        try:
            p = Path(f)
            new_name = f"{prefix}{p.name}"
            new_path = p.parent / new_name
            os.rename(f, new_path)
            renamed.append((f, str(new_path)))
        except Exception as e:
            errors.append(f"Error: {p.name} - {str(e)}")
    
    return {
        'success': len(renamed) > 0,
        'message': f"Renombrados {len(renamed)} archivos",
        'renamed': renamed,
        'errors': errors
    }


def rename_with_suffix(files: List[str], suffix: str) -> Dict[str, Any]:
    """Agregar sufijo antes de la extensión."""
    renamed = []
    errors = []
    
    for f in files:
        try:
            p = Path(f)
            new_name = f"{p.stem}{suffix}{p.suffix}"
            new_path = p.parent / new_name
            os.rename(f, new_path)
            renamed.append((f, str(new_path)))
        except Exception as e:
            errors.append(f"Error: {p.name} - {str(e)}")
    
    return {
        'success': len(renamed) > 0,
        'message': f"Renombrados {len(renamed)} archivos",
        'renamed': renamed,
        'errors': errors
    }


def rename_replace(files: List[str], find: str, replace: str) -> Dict[str, Any]:
    """Reemplazar texto en nombres."""
    renamed = []
    errors = []
    
    for f in files:
        try:
            p = Path(f)
            new_name = p.name.replace(find, replace)
            new_path = p.parent / new_name
            if new_path.exists():
                errors.append(f"Ya existe: {new_name}")
                continue
            os.rename(f, new_path)
            renamed.append((f, str(new_path)))
        except Exception as e:
            errors.append(f"Error: {p.name} - {str(e)}")
    
    return {
        'success': len(renamed) > 0,
        'message': f"Renombrados {len(renamed)} archivos",
        'renamed': renamed,
        'errors': errors
    }


def rename_numbered(files: List[str], start: int = 1, pattern: str = "{name}_{n}") -> Dict[str, Any]:
    """Renombrar con números secuenciales."""
    renamed = []
    errors = []
    
    for i, f in enumerate(files, start=start):
        try:
            p = Path(f)
            ext = p.suffix
            new_name = pattern.format(name=p.stem, n=i) + ext
            new_path = p.parent / new_name
            os.rename(f, new_path)
            renamed.append((f, str(new_path)))
        except Exception as e:
            errors.append(f"Error: {p.name} - {str(e)}")
    
    return {
        'success': len(renamed) > 0,
        'message': f"Renombrados {len(renamed)} archivos",
        'renamed': renamed,
        'errors': errors
    }


def rename_case(files: List[str], case: str) -> Dict[str, Any]:
    """Cambiar mayúsculas/minúsculas."""
    renamed = []
    errors = []
    
    for f in files:
        try:
            p = Path(f)
            if case == 'lower':
                new_name = p.name.lower()
            elif case == 'upper':
                new_name = p.name.upper()
            elif case == 'title':
                new_name = p.name.title()
            else:
                continue
            
            new_path = p.parent / new_name
            os.rename(f, new_path)
            renamed.append((f, str(new_path)))
        except Exception as e:
            errors.append(f"Error: {p.name} - {str(e)}")
    
    return {
        'success': len(renamed) > 0,
        'message': f"Renombrados {len(renamed)} archivos",
        'renamed': renamed,
        'errors': errors
    }


def rename_regex(files: List[str], pattern: str, replace: str) -> Dict[str, Any]:
    """Renombrar usando expresiones regulares."""
    renamed = []
    errors = []
    
    try:
        regex = re.compile(pattern)
        
        for f in files:
            try:
                p = Path(f)
                new_name = regex.sub(replace, p.name)
                new_path = p.parent / new_name
                os.rename(f, new_path)
                renamed.append((f, str(new_path)))
            except Exception as e:
                errors.append(f"Error: {p.name} - {str(e)}")
    
    except re.error as e:
        return {'success': False, 'error': f'Expresión regular inválida: {e}'}
    
    return {
        'success': len(renamed) > 0,
        'message': f"Renombrados {len(renamed)} archivos",
        'renamed': renamed,
        'errors': errors
    }