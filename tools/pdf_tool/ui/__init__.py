"""
PDF Tool UI - Módulos especializados por tab.

Este paquete contiene los tabs de la UI de PDF organizados por responsabilidad:
- main_ui: esqueleto principal de PDFToolUI
- watermark_tab: agregar/quitar watermarks
- edit_tab: anotación, censura, extraer páginas
- transform_tab: rotar, reordenar
- combine_tab: combinar, extraer
- numbers_tab: números de página
- security_tab: encriptar/desencriptar
- optimize_tab: comprimir, limpiar metadatos
- pipeline_tab: pipeline de operaciones
- info_tab: información del PDF
- helpers: funciones auxiliares

Backward compatibility: PDFToolUI también se importa desde ui.py
"""

# Re-export PDFToolUI y helpers
from tools.pdf_tool.ui.main_ui import PDFToolUI, get_pdf_thumbnail

__all__ = [
    'PDFToolUI',
    'get_pdf_thumbnail',
]