"""
Filtros de búsqueda: nombre, fecha, tamaño, extensión.
Separado de processor.py por SRP (máxima R0: clases <300 líneas).
"""
import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Optional


def search_by_name(files: List[str], pattern: str, mode: str = 'contains', 
                  case_sensitive: bool = False) -> List[str]:
    """Busca archivos por nombre."""
    results = []
    
    if not pattern:
        return files
    
    for f in files:
        name = os.path.basename(f)
        
        if mode == 'exact':
            match = (name == pattern) if case_sensitive else (name.lower() == pattern.lower())
        elif mode == 'contains':
            match = (pattern in name) if case_sensitive else (pattern.lower() in name.lower())
        elif mode == 'regex':
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                match = bool(re.search(pattern, name, flags))
            except re.error:
                match = False
        else:
            match = pattern.lower() in name.lower()
        
        if match:
            results.append(f)
    
    return results


def search_by_date(files: List[str], date_from: Optional[str] = None,
                   date_to: Optional[str] = None) -> List[str]:
    """Filtra archivos por fecha de modificación."""
    results = []
    
    from_date = None
    to_date = None
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%d/%m/%Y')
        except ValueError:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d')
            except ValueError as e:
                pass  # Invalid date format
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%d/%m/%Y')
        except ValueError:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d')
            except ValueError as e:
                pass  # Invalid date format
    
    for f in files:
        if not os.path.exists(f):
            continue
        
        mtime = datetime.fromtimestamp(os.path.getmtime(f))
        
        if from_date and mtime < from_date:
            continue
        if to_date and mtime > to_date:
            continue
        
        results.append(f)
    
    return results


def filter_by_size(files: List[str], min_size: Optional[int] = None,
                  max_size: Optional[int] = None) -> List[str]:
    """Filtra archivos por tamaño en bytes."""
    results = []
    
    for f in files:
        if not os.path.exists(f):
            continue
        
        size = os.path.getsize(f)
        
        if min_size and size < min_size:
            continue
        if max_size and size > max_size:
            continue
        
        results.append(f)
    
    return results


def filter_by_extension(files: List[str], extensions: List[str]) -> List[str]:
    """Filtra por extensión."""
    if not extensions:
        return files
    
    extensions = [e.lower().replace('.', '') for e in extensions]
    
    results = []
    for f in files:
        ext = Path(f).suffix.lower().replace('.', '')
        if ext in extensions:
            results.append(f)
    
    return results