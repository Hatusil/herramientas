"""
Numbers Tab - Agregar números de página.

Funciones:
- setup_numbers_tab: configura la UI del tab
- add_page_numbers: agrega números de página
"""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.pdf_tool.ui.main_ui import PDFToolUI


def setup_numbers_tab(ui: 'PDFToolUI') -> None:
    """Configura el tab de Números de página."""
    frame = ui.tab_numbers

    num_frame = ctk.CTkFrame(frame)
    num_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(num_frame, text="Agregar números de página:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)

    opts = ctk.CTkFrame(num_frame, fg_color="transparent")
    opts.pack(fill="x", padx=5)

    ctk.CTkLabel(opts, text="Posición:").pack(side="left", padx=5)
    ui.num_position = ctk.CTkOptionMenu(opts, values=["footer", "header"], width=100)
    ui.num_position.set("footer")
    ui.num_position.pack(side="left", padx=5)

    ctk.CTkLabel(opts, text="Inicio:").pack(side="left", padx=5)
    ui.num_start = ctk.CTkEntry(opts, width=50)
    ui.num_start.insert(0, "1")
    ui.num_start.pack(side="left", padx=5)

    ctk.CTkLabel(opts, text="Formato:").pack(side="left", padx=5)
    ui.num_format = ctk.CTkEntry(opts, width=120)
    ui.num_format.insert(0, "Página {n} de {total}")
    ui.num_format.pack(side="left", padx=5)

    ctk.CTkButton(
        num_frame,
        text="Agregar Números",
        command=lambda: ui._add_page_numbers(),
        height=40
    ).pack(pady=10)


# Handlers

def add_page_numbers(ui: 'PDFToolUI') -> None:
    """Agrega números de página al PDF."""
    if not ui._check_files():
        return

    ui.status_label.configure(text="Procesando...", text_color="blue")

    result = ui.process_async('page_numbers', ui.files, {
        'position': ui.num_position.get(),
        'start': int(ui.num_start.get() or 1),
        'format': ui.num_format.get() or "Página {n} de {total}",
    })

    ui._show_result(result)