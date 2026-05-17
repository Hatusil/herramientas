"""
Combine Tab - Combinar y extraer páginas.

Funciones:
- setup_combine_tab: configura la UI del tab
- merge_pdfs: combina múltiples PDFs
- extract_pages: extrae páginas específicas
"""

import customtkinter as ctk
from core.constants import COLORS
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.pdf_tool.ui.main_ui import PDFToolUI


def setup_combine_tab(ui: 'PDFToolUI') -> None:
    """Configura el tab de Combinar."""
    frame = ui.tab_combine

    # Combinar
    merge_frame = ctk.CTkFrame(frame)
    merge_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(merge_frame, text="Combinar PDFs:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)

    ctk.CTkLabel(
        merge_frame,
        text="Seleccione múltiples PDFs en el selector de archivos",
        text_color="gray"
    ).pack(anchor="w", padx=10)

    ctk.CTkButton(
        merge_frame,
        text="Combinar en un PDF",
        command=lambda: ui._merge_pdfs(),
        height=40
    ).pack(pady=5)

    # Extraer
    extract_frame = ctk.CTkFrame(frame)
    extract_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(extract_frame, text="Extraer páginas:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)

    ctk.CTkLabel(extract_frame, text="Páginas (ej: 1,3,5 o 1-5):").pack(anchor="w", padx=10)
    ui.extract_pages = ctk.CTkEntry(extract_frame, width=200)
    ui.extract_pages.pack(padx=10, pady=5)

    ctk.CTkButton(
        extract_frame,
        text="Extraer",
        command=lambda: ui._extract_pages()
    ).pack(pady=5)


# Handlers

def merge_pdfs(ui: 'PDFToolUI') -> None:
    """Combina múltiples PDFs en uno."""
    if not ui._check_files() or len(ui.files) < 2:
        ui.status_label.configure(text="Seleccione al menos 2 PDFs", text_color=COLORS.get("warning"))
        return

    ui.status_label.configure(text="Procesando...", text_color="blue")

    result = ui.process_async('merge', ui.files, {})

    ui._show_result(result)


def extract_pages(ui: 'PDFToolUI') -> None:
    """Extrae páginas específicas del PDF."""
    if not ui._check_files():
        return

    pages_str = ui.extract_pages.get().strip()
    if not pages_str:
        ui.status_label.configure(text="Ingrese las páginas a extraer", text_color=COLORS.get("warning"))
        return

    pages = []
    try:
        if '-' in pages_str:
            parts = pages_str.split('-')
            start = int(parts[0])
            end = int(parts[1])
            pages = list(range(start, end + 1))
        else:
            pages = [int(p.strip()) for p in pages_str.split(',')]
    except ValueError:
        ui.status_label.configure(text="Formato de páginas inválido", text_color="red")
        return

    ui.status_label.configure(text="Procesando...", text_color="blue")

    result = ui.process_async('extract', ui.files, {'pages': pages})

    ui._show_result(result)