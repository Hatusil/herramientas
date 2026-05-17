"""
Búsqueda completa: orquesta filtros, extracción de contenido y formateo.
Separado de processor.py por SRP (máxima R0: clases <300 líneas).
"""
import os
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional

from core.metrics import Timer, get_metric
from tools.search_tool.filters import (
    search_by_name, search_by_date, filter_by_size, filter_by_extension
)
from tools.search_tool.content_extractors import get_file_content


def _collect_files_recursive(folder: str) -> List[str]:
    """1. Recolectar archivos del directorio recursivamente."""
    all_files = []
    for root, dirs, files in os.walk(folder):
        for name in files:
            all_files.append(os.path.join(root, name))
    return all_files


def _apply_name_filter(results: List[str], name_pattern: str, name_mode: str, case_sensitive: bool) -> List[str]:
    """2. Filtrar por nombre."""
    return search_by_name(results, name_pattern, name_mode, case_sensitive)


def _apply_date_filter(results: List[str], date_from: Optional[str], date_to: Optional[str]) -> List[str]:
    """3. Filtrar por fecha."""
    if date_from or date_to:
        return search_by_date(results, date_from, date_to)
    return results


def _apply_size_filter(results: List[str], min_size: Optional[int], max_size: Optional[int]) -> List[str]:
    """4. Filtrar por tamaño."""
    if min_size or max_size:
        return filter_by_size(results, min_size, max_size)
    return results


def _apply_extension_filter(results: List[str], extensions: List[str]) -> List[str]:
    """5. Filtrar por extensión."""
    if extensions:
        return filter_by_extension(results, extensions)
    return results


def _search_content_in_files(results: List[str], pattern: str, case_sensitive: bool) -> Dict[str, Dict]:
    """6. Buscar contenido en archivos."""
    content_results = {}
    for f in results:
        try:
            content = get_file_content(f)
            if not content:
                continue
            
            if case_sensitive:
                if pattern in content:
                    count = content.count(pattern)
                    content_results[f] = {'matches': count, 'content': content[:500]}
            else:
                lower_content = content.lower()
                lower_pattern = pattern.lower()
                if lower_pattern in lower_content:
                    count = lower_content.count(lower_pattern)
                    content_results[f] = {'matches': count, 'content': content[:500]}
        except Exception:
            continue
    return content_results


def _format_search_results(files: List[str], content_matches: Dict[str, Dict]) -> List[Dict]:
    """7. Formatear resultados finales."""
    final_results = []
    for f in files:
        is_file = os.path.isfile(f)
        stat = os.stat(f) if is_file else None
        
        result = {
            'path': f,
            'name': os.path.basename(f),
            'size': stat.st_size if stat else 0,
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M') if stat else '',
            'matches': content_matches.get(f, {}).get('matches', 0) if f in content_matches else 0
        }
        final_results.append(result)
    return final_results


def search_all(folder: str, options: Dict[str, Any],
               cancel_flag: threading.Event = None) -> Dict[str, Any]:
    """
    Función principal de búsqueda.
    
    options: {
        'name_pattern': str,
        'name_mode': 'exact'|'contains'|'regex',
        'case_sensitive': bool,
        'date_from': str|null,
        'date_to': str|null,
        'extensions': list,
        'min_size': int|null,
        'max_size': int|null,
        'search_content': bool,
        'content_pattern': str,
    }
    """
    files_counter = get_metric('search_files_processed')
    errors_counter = get_metric('search_errors')
    
    with Timer('search_all'):
        if not os.path.exists(folder):
            errors_counter.increment()
            return {'success': False, 'error': 'Carpeta no encontrada'}
        
        # 1. Recolectar archivos
        all_files = _collect_files_recursive(folder)
        files_counter.increment(len(all_files))
        
        if cancel_flag and cancel_flag.is_set():
            return {'success': True, 'cancelled': True, 'results': [], 'count': 0}
        
        # 2. Aplicar filtros en cadena
        results = all_files
        
        if options.get('name_pattern'):
            results = _apply_name_filter(
                results,
                options['name_pattern'],
                options.get('name_mode', 'contains'),
                options.get('case_sensitive', False)
            )
            if cancel_flag and cancel_flag.is_set():
                return {'success': True, 'cancelled': True, 'results': [], 'count': 0}
        
        results = _apply_date_filter(results, options.get('date_from'), options.get('date_to'))
        results = _apply_size_filter(results, options.get('min_size'), options.get('max_size'))
        results = _apply_extension_filter(results, options.get('extensions', []))
        
        # 3. Buscar contenido
        content_results = {}
        if options.get('search_content') and options.get('content_pattern'):
            content_results = _search_content_in_files(
                results,
                options['content_pattern'],
                options.get('case_sensitive', False)
            )
            
            if cancel_flag and cancel_flag.is_set():
                return {'success': True, 'cancelled': True, 'results': [], 'count': 0}
            
            if content_results:
                results = list(content_results.keys())
        
        # 4. Formatear resultados
        final_results = _format_search_results(results, content_results)
        
        return {
            'success': True,
            'results': final_results,
            'count': len(final_results),
            'content_matches': content_results
        }