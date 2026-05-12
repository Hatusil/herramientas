"""
Analisis Tab - Análisis de imagen.

Funciones:
- setup_tab: configura la UI del tab
- on_select_template, on_pseudocolor, on_haar_detect
"""

import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.image_tool.ui.main_ui import ImageToolUI

# Constante local para evitar acceso a ui.COLORMAP_OPTIONS (que es de módulo)
_COLORMAP_OPTIONS = [
    'jet', 'ocean', 'summer', 'winter', 'autumn', 'bone',
    'cool', 'copper', 'flag', 'hsv', 'inferno', 'magma',
    'plasma', 'turbo', 'viridis'
]


def setup_tab(ui: 'ImageToolUI') -> None:
    """Configura el tab de Análisis."""
    tab = ui.tab_view.tab("An\u00e1lisis")

    template_frame = ctk.CTkFrame(tab, fg_color="transparent")
    template_frame.pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(template_frame, text="Template Matching:").pack()

    ctk.CTkButton(template_frame, text="\U0001F4C1 Seleccionar template", command=lambda: ui._on_select_template()).pack(pady=5)

    ui.template_path_label = ctk.CTkLabel(template_frame, text="Sin template", text_color="gray", font=ctk.CTkFont(size=10))
    ui.template_path_label.pack()

    ui.template_path: str = None

    pseudo_frame = ctk.CTkFrame(tab, fg_color="transparent")
    pseudo_frame.pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(pseudo_frame, text="Pseudocolor:").pack()

    ui.colormap_var = ctk.StringVar(value="jet")
    colormap_menu = ctk.CTkOptionMenu(pseudo_frame, values=_COLORMAP_OPTIONS, variable=ui.colormap_var, width=200)
    colormap_menu.pack(pady=5)

    ctk.CTkButton(pseudo_frame, text="\U0001F308 Aplicar pseudocolor", command=lambda: ui._on_pseudocolor()).pack(pady=5)

    haar_frame = ctk.CTkFrame(tab, fg_color="transparent")
    haar_frame.pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(haar_frame, text="Detecci\u00f3n Haar:").pack()

    ui.haar_cascade_var = ctk.StringVar(value="face")
    haar_menu = ctk.CTkOptionMenu(haar_frame, values=['face', 'eye', 'smile'], variable=ui.haar_cascade_var, width=200)
    haar_menu.pack(pady=5)

    ctk.CTkButton(haar_frame, text="\U0001F916 Detectar objetos", command=lambda: ui._on_haar_detect()).pack(pady=5)

    preview_label = ctk.CTkLabel(tab, text="", fg_color="transparent")
    ui._preview_labels["An\u00e1lisis"] = preview_label


# Handlers

def on_select_template(ui: 'ImageToolUI') -> None:
    """Selecciona un template para matching."""
    file = filedialog.askopenfilename(
        title="Seleccionar template",
        filetypes=[("Im\u00e1genes", "*.jpg *.jpeg *.png *.bmp"), ("Todos los archivos", "*.*")],
    )
    if file:
        ui.template_path = file
        ui.template_path_label.configure(text=Path(file).name, text_color="green")


def on_pseudocolor(ui: 'ImageToolUI') -> None:
    """Aplica pseudocolor a la imagen."""
    ui._process_phase('_pseudocolor', {'colormap': ui.colormap_var.get()})


def on_haar_detect(ui: 'ImageToolUI') -> None:
    """Detecta objetos usando Haar cascades."""
    ui._process_phase('_haar_detect', {'cascade_path': ui.haar_cascade_var.get()})