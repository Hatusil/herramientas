"""
Optimize Tab - Comprimir y limpiar metadatos.

Funciones:
- setup_optimize_tab: configura la UI del tab
- compress_pdf: comprime el PDF
- clean_metadata: limpia metadatos
"""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.pdf_tool.ui.main_ui import PDFToolUI


def setup_optimize_tab(ui: 'PDFToolUI') -> None:
    """Configura el tab de Optimizar."""
    frame = ui.tab_optimize

    # Comprimir
    compress_frame = ctk.CTkFrame(frame)
    compress_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(compress_frame, text="Comprimir PDF:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)

    comp_opts = ctk.CTkFrame(compress_frame, fg_color="transparent")
    comp_opts.pack(fill="x", padx=5)

    ctk.CTkLabel(comp_opts, text="Nivel:").pack(side="left", padx=5)
    ui.compress_level = ctk.CTkOptionMenu(comp_opts, values=["low", "medium", "high"], width=100)
    ui.compress_level.set("medium")
    ui.compress_level.pack(side="left", padx=5)

    ctk.CTkButton(
        compress_frame,
        text="Comprimir",
        command=lambda: ui._compress_pdf(),
        height=40
    ).pack(pady=5)

    # Limpiar metadatos
    clean_frame = ctk.CTkFrame(frame)
    clean_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(clean_frame, text="Limpiar metadatos:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)

    ctk.CTkButton(
        clean_frame,
        text="Limpiar Metadatos",
        command=lambda: ui._clean_metadata(),
        height=40
    ).pack(pady=5)


# Handlers

def compress_pdf(ui: 'PDFToolUI') -> None:
    """Comprime el PDF."""
    if not ui._check_files():
        return

    ui.status_label.configure(text="Procesando...", text_color="blue")

    result = ui.process_async('compress', ui.files, {
        'level': ui.compress_level.get()
    })

    ui._show_result(result)


def clean_metadata(ui: 'PDFToolUI') -> None:
    """Limpia los metadatos del PDF."""
    if not ui._check_files():
        return

    ui.status_label.configure(text="Procesando...", text_color="blue")

    result = ui.process_async('clean_metadata', ui.files, {})

    ui._show_result(result)