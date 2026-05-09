"""
Processor: Funciones para renombrar archivos en masa.
"""
import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Any

# Importar funciones compartidas de core (máxima C2: Consistency)
from core.file_utils import validate_input_file, get_output_path
# Métricas
from core.metrics import Counter, Timer, increment

# Contadores de operaciones
rename_operations_total = Counter('rename_operations_total')
rename_errors = Counter('rename_errors')


def rename_with_prefix(files: List[str], prefix: str) -> Dict[str, Any]:
    """Agregar prefijo a archivos."""
    with Timer('rename_tool.rename_with_prefix'):
        renamed = []
        errors = []
        
        for f in files:
            try:
                p = Path(f)
                new_name = f"{prefix}{p.name}"
                new_path = p.parent / new_name
                shutil.copy2(f, new_path)  # A8: copy instead of rename for idempotency
                renamed.append((f, str(new_path)))
            except Exception as e:
                errors.append(f"Error: {p.name} - {str(e)}")
                increment('rename_errors')
        
        if len(renamed) > 0:
            increment('rename_operations_total')
        
        success = len(renamed) > 0
        msg = f"✓ Prefijo '{prefix}' agregado a {len(renamed)} archivos"
        if errors:
            msg += f" ({len(errors)} errores)"
        
        return {
            'success': success,
            'message': msg,
            'renamed': renamed,
            'errors': errors
        }


def rename_with_suffix(files: List[str], suffix: str) -> Dict[str, Any]:
    """Agregar sufijo antes de la extensión."""
    with Timer('rename_tool.rename_with_suffix'):
        renamed = []
        errors = []
        
        for f in files:
            try:
                p = Path(f)
                new_name = f"{p.stem}{suffix}{p.suffix}"
                new_path = p.parent / new_name
                shutil.copy2(f, new_path)  # A8: copy instead of rename for idempotency
                renamed.append((f, str(new_path)))
            except Exception as e:
                errors.append(f"Error: {p.name} - {str(e)}")
                increment('rename_errors')
        
        if len(renamed) > 0:
            increment('rename_operations_total')
        
        success = len(renamed) > 0
        msg = f"✓ Sufijo '{suffix}' agregado a {len(renamed)} archivos"
        if errors:
            msg += f" ({len(errors)} errores)"
        
        return {
            'success': success,
            'message': msg,
            'renamed': renamed,
            'errors': errors
        }


def rename_replace(files: List[str], find: str, replace: str) -> Dict[str, Any]:
    """Reemplazar texto en nombres."""
    with Timer('rename_tool.rename_replace'):
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
                shutil.copy2(f, new_path)  # A8: copy instead of rename for idempotency
                renamed.append((f, str(new_path)))
            except Exception as e:
                errors.append(f"Error: {p.name} - {str(e)}")
                increment('rename_errors')
        
        if len(renamed) > 0:
            increment('rename_operations_total')
        
        success = len(renamed) > 0
        msg = f"✓ '{find}' → '{replace}' en {len(renamed)} archivos"
        if errors:
            msg += f" ({len(errors)} errores)"
        
        return {
            'success': success,
            'message': msg,
            'renamed': renamed,
            'errors': errors
        }


def rename_numbered(files: List[str], start: int = 1, pattern: str = "{name}_{n}") -> Dict[str, Any]:
    """Renombrar con números secuenciales."""
    with Timer('rename_tool.rename_numbered'):
        renamed = []
        errors = []
        
        for i, f in enumerate(files, start=start):
            try:
                p = Path(f)
                ext = p.suffix
                new_name = pattern.format(name=p.stem, n=i) + ext
                new_path = p.parent / new_name
                shutil.copy2(f, new_path)  # A8: copy instead of rename for idempotency
                renamed.append((f, str(new_path)))
            except Exception as e:
                errors.append(f"Error: {p.name} - {str(e)}")
                increment('rename_errors')
        
        if len(renamed) > 0:
            increment('rename_operations_total')
        
        success = len(renamed) > 0
        msg = f"✓ Numerados {len(renamed)} archivos (inicio: {start})"
        if errors:
            msg += f" ({len(errors)} errores)"
        
        return {
            'success': success,
            'message': msg,
            'renamed': renamed,
            'errors': errors
        }


def rename_case(files: List[str], case: str) -> Dict[str, Any]:
    """Cambiar mayúsculas/minúsculas."""
    with Timer('rename_tool.rename_case'):
        renamed = []
        errors = []
        
        case_labels = {'lower': 'minúsculas', 'upper': 'MAYÚSCULAS', 'title': 'Título'}
        
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
                
                # A8: Si el nombre no cambia, incluir en lista pero sin copiar
                if new_name == p.name:
                    renamed.append((f, str(p)))  # Incluir como "sin cambio"
                    continue
                
                new_path = p.parent / new_name
                shutil.copy2(f, new_path)  # A8: copy instead of rename for idempotency
                renamed.append((f, str(new_path)))
            except Exception as e:
                errors.append(f"Error: {p.name} - {str(e)}")
                increment('rename_errors')
        
        if len(renamed) > 0:
            increment('rename_operations_total')
        
        success = len(errors) == 0 and len(renamed) > 0  # A8: success si se procesó al menos un archivo
        case_name = case_labels.get(case, case)
        msg = f"✓ Convertidos a {case_name}: {len(renamed)} archivos"
        if errors:
            msg += f" ({len(errors)} errores)"
        
        return {
            'success': success,
            'message': msg,
            'renamed': renamed,
            'errors': errors
        }


def rename_regex(files: List[str], pattern: str, replace: str) -> Dict[str, Any]:
    """Renombrar usando expresiones regulares."""
    with Timer('rename_tool.rename_regex'):
        renamed = []
        errors = []
        
        try:
            regex = re.compile(pattern)
            
            for f in files:
                try:
                    p = Path(f)
                    new_name = regex.sub(replace, p.name)
                    # A8: Si el nombre no cambia (no hay match), no hacer copy
                    if new_name == p.name:
                        renamed.append((f, str(p)))  # Registrar como "sin cambio"
                        continue
                    new_path = p.parent / new_name
                    shutil.copy2(f, new_path)  # A8: copy instead of rename for idempotency
                    renamed.append((f, str(new_path)))
                except Exception as e:
                    errors.append(f"Error: {p.name} - {str(e)}")
                    increment('rename_errors')
        
        except re.error as e:
            increment('rename_errors')
            return {'success': False, 'error': f'Expresión regular inválida: {e}'}
        
        if len(renamed) > 0:
            increment('rename_operations_total')
        
        success = len(renamed) > 0
        msg = f"✓ Regex '{pattern}' → '{replace}' en {len(renamed)} archivos"
        if errors:
            msg += f" ({len(errors)} errores)"
        
        return {
            'success': success,
            'message': msg,
            'renamed': renamed,
            'errors': errors
        }