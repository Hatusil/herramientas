"""
Info Tab - Información del PDF.

Funciones:
- setup_info_tab: configura la UI del tab
- show_pdf_info: muestra información del PDF
"""

import tkinter as tk
import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.pdf_tool.ui.main_ui import PDFToolUI


def setup_info_tab(ui: 'PDFToolUI') -> None:
    """Configura el tab de Info."""
    frame = ui.tab_info

    info_frame = ctk.CTkFrame(frame)
    info_frame.pack(fill="both", expand=True, padx=10, pady=10)

    ctk.CTkLabel(info_frame, text="Información del PDF:", font=ctk.CTkFont(weight="bold")).pack(anchor="n", pady=5)

    ui.info_text = ctk.CTkTextbox(info_frame, width=400, height=200)
    ui.info_text.pack(padx=10, pady=10, fill="both", expand=True)

    ctk.CTkButton(
        info_frame,
        text="Ver Información",
        command=lambda: ui._show_pdf_info()
    ).pack(pady=5)


# Handlers

def show_pdf_info(ui: 'PDFToolUI') -> None:
    """Muestra información del PDF."""
    if not ui._check_files():
        return

    if not ui.files:
        ui.status_label.configure(text="Seleccione un PDF", text_color="#FFA500")
        return

    from tools.pdf_tool.processor import get_pdf_info

    ui.info_text.delete("1.0", tk.END)

    for file_path in ui.files:
        info = get_pdf_info(file_path)

        if info.get('success'):
            ui.info_text.insert(tk.END, f"""Información del PDF:
────────────────────────────────────
Archivo: {info.get('file_name', 'N/A')}
Tamaño: {info.get('file_size', 0)} bytes
Páginas: {info.get('num_pages', 0)}
Encriptado: {'Sí' if info.get('is_encrypted') else 'No'}

Metadatos:
────────────────────────────────────
Título: {info.get('title', 'N/A')}
Autor: {info.get('author', 'N/A')}
Creador: {info.get('creator', 'N/A')}
Productor: {info.get('producer', 'N/A')}
Fecha creación: {info.get('creation_date', 'N/A')}
""")

            pages = info.get('pages', [])
            if pages:
                ui.info_text.insert(tk.END, "\nPáginas:\n─────────────────────────────────\n")
                for p in pages[:10]:
                    ui.info_text.insert(tk.END, f"Página {p['page_num']}: Rotación={p['rotation']}°\n")

            ui.info_text.insert(tk.END, "\n" + "="*35 + "\n\n")
        else:
            ui.info_text.insert(tk.END, f"Error con {info.get('file_name', file_path)}: {info.get('error', 'Error desconocido')}\n\n")