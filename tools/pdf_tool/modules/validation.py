"""
Validaciones para transformación de PDFs.
Separado de transform.py por SRP (máxima R0: clases <300 líneas).
"""
from typing import List, Tuple


def validate_page_number(page_num: int, total_pages: int) -> Tuple[bool, str]:
    """Valida un número de página."""
    if page_num < 1:
        return False, f"Número de página inválido: {page_num} (debe ser >= 1)"
    if page_num > total_pages:
        return False, f"Número de página {page_num} excede el total de páginas ({total_pages})"
    return True, ""


def validate_page_range(start: int, end: int, total_pages: int) -> Tuple[bool, str]:
    """Valida un rango de páginas."""
    if start < 1:
        return False, f"Página inicial inválida: {start} (debe ser >= 1)"
    if end > total_pages:
        return False, f"Página final {end} excede el total de páginas ({total_pages})"
    if start > end:
        return False, f"Página inicial ({start}) no puede ser mayor que la final ({end})"
    return True, ""


def validate_new_order(new_order: List[int], total_pages: int) -> Tuple[bool, str]:
    """Valida una lista de nuevo orden para páginas."""
    if len(new_order) != total_pages:
        return False, f"La lista debe tener {total_pages} elementos, tiene {len(new_order)}"
    
    seen = set()
    for p in new_order:
        if p < 1 or p > total_pages:
            return False, f"Número de página inválido: {p} (debe estar entre 1 y {total_pages})"
        if p in seen:
            return False, f"Página duplicada: {p}"
        seen.add(p)
    
    return True, ""