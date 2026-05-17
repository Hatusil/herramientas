"""
Funciones async para pdf_tool - no bloquean la UI.
Separado de processor.py por SRP (máxima R0: clases <300 líneas).
"""
from core.async_utils import run_in_background


def rotate_pages_async(files: list, callback, degrees: int = 90, pages: list = None):
    """Versión async de rotate_pages()."""
    from tools.pdf_tool.processor import rotate_pages
    return run_in_background(rotate_pages, files, callback=callback, degrees=degrees, pages=pages)


def merge_pdfs_async(files: list, callback, output_path: str = None):
    """Versión async de merge_pdfs()."""
    from tools.pdf_tool.processor import merge_pdfs
    return run_in_background(merge_pdfs, files, callback=callback, output_path=output_path)


def extract_pages_async(files: list, callback, pages: list):
    """Versión async de extract_pages()."""
    from tools.pdf_tool.processor import extract_pages
    return run_in_background(extract_pages, files, callback=callback, pages=pages)