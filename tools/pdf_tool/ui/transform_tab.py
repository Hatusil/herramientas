"""
Transform Tab - Rotar y reordenar páginas.

Funciones:
- setup_transform_tab: configura la UI del tab
- rotate_pages: rota páginas
- reorder_pages: reordena páginas
"""

import customtkinter as ctk
from core.constants import COLORS
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.pdf_tool.ui.main_ui import PDFToolUI


def setup_transform_tab(ui: 'PDFToolUI') -> None:
    """Configura el tab de Transformar."""
    frame = ui.tab_transform

    # Rotar
    rotate_frame = ctk.CTkFrame(frame)
    rotate_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(rotate_frame, text="Rotar páginas:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)

    rot_opts = ctk.CTkFrame(rotate_frame, fg_color="transparent")
    rot_opts.pack(fill="x", padx=5)

    ui.rotate_var = ctk.StringVar(value="90")

    for deg in ["90", "180", "270"]:
        ctk.CTkRadioButton(
            rot_opts,
            text=f"{deg}°",
            variable=ui.rotate_var,
            value=deg
        ).pack(side="left", padx=10)

    ctk.CTkLabel(rot_opts, text="Páginas (vacío=todas):").pack(side="left", padx=(20, 5))
    ui.rotate_pages = ctk.CTkEntry(rot_opts, width=100)
    ui.rotate_pages.pack(side="left", padx=5)

    ctk.CTkButton(
        rotate_frame,
        text="Rotar",
        command=lambda: ui._rotate_pages()
    ).pack(pady=5)

    # Reordenar
    reorder_frame = ctk.CTkFrame(frame)
    reorder_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(reorder_frame, text="Reordenar páginas:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)

    ctk.CTkLabel(reorder_frame, text="Nuevo orden (ej: 3,1,2):").pack(anchor="w", padx=10)
    ui.reorder_input = ctk.CTkEntry(reorder_frame, width=200)
    ui.reorder_input.pack(padx=10, pady=5)

    ctk.CTkButton(
        reorder_frame,
        text="Reordenar",
        command=lambda: ui._reorder_pages()
    ).pack(pady=5)


# Handlers

def rotate_pages(ui: 'PDFToolUI') -> None:
    """Rota las páginas del PDF."""
    if not ui._check_files():
        return

    degrees = int(ui.rotate_var.get())

    pages = None
    if ui.rotate_pages.get().strip():
        pages = [int(p) for p in ui.rotate_pages.get().split(',')]

    ui.status_label.configure(text="Procesando...", text_color="blue")

    result = ui.process_async('rotate', ui.files, {
        'degrees': degrees,
        'pages': pages
    })

    ui._show_result(result)


def reorder_pages(ui: 'PDFToolUI') -> None:
    """Reordena las páginas del PDF."""
    if not ui._check_files():
        return

    order_str = ui.reorder_input.get().strip()
    if not order_str:
        ui.status_label.configure(text="Ingrese el orden de páginas", text_color=COLORS.get("warning"))
        return

    try:
        new_order = [int(p) for p in order_str.split(',')]
    except ValueError:
        ui.status_label.configure(text="Orden inválido", text_color="red")
        return

    ui.status_label.configure(text="Procesando...", text_color="blue")

    result = ui.process_async('reorder', ui.files, {
        'new_order': new_order
    })

    ui._show_result(result)