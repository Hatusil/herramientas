"""
PDF Tool UI - Interfaz de usuario para procesamiento de PDFs.

Este módulo es un HUB DE RE-EXPORT para backwards compatibility.
El código real está en tools/pdf_tool/ui/.

Para imports directos:
    from tools.pdf_tool.ui import PDFToolUI

Para backwards compatibility (código旧的 que importa de pdf_tool.ui):
    from tools.pdf_tool import ui
    ui.PDFToolUI(...)  # Funciona igual
"""

from tools.pdf_tool.ui import PDFToolUI, get_pdf_thumbnail

__all__ = ['PDFToolUI', 'get_pdf_thumbnail']