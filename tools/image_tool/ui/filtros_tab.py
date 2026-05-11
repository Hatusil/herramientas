"""
Filtros Tab - Filtros de suavizado.

Funciones:
- setup_tab: configura la UI del tab
- on_filter_gaussian, on_filter_median, on_filter_mean, on_deconvolve
"""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.image_tool.ui.main_ui import ImageToolUI


def setup_tab(ui: 'ImageToolUI') -> None:
    """Configura el tab de Filtros."""
    tab = ui.tab_view.tab("Filtros")

    ksize_frame = ctk.CTkFrame(tab, fg_color="transparent")
    ksize_frame.pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(ksize_frame, text="Kernel size (3-21, impar):").pack()
    ui.ksize_slider = ctk.CTkSlider(ksize_frame, from_=3, to=21, number_of_steps=9)
    ui.ksize_slider.set(5)
    ui.ksize_slider.pack(fill="x", padx=10)

    ui.ksize_label = ctk.CTkLabel(ksize_frame, text="ksize: 5")
    ui.ksize_label.pack()

    ksize_slider = ui.ksize_slider
    ksize_label = ui.ksize_label

    def update_ksize(value):
        odd_val = int(value)
        if odd_val % 2 == 0:
            odd_val += 1
        ksize_label.configure(text=f"ksize: {odd_val}")

    ui.ksize_slider.configure(command=update_ksize)

    ctk.CTkButton(tab, text="\U0001F535 Filtro Gaussiano", command=lambda: ui._on_filter_gaussian()).pack(pady=5, padx=10, fill="x")
    ctk.CTkButton(tab, text="\u2B21 Filtro de Mediana", command=lambda: ui._on_filter_median()).pack(pady=5, padx=10, fill="x")
    ctk.CTkButton(tab, text="\U0001F518 Filtro de Media", command=lambda: ui._on_filter_mean()).pack(pady=5, padx=10, fill="x")
    ctk.CTkButton(tab, text="\U0001F527 Deconvoluci\u00f3n", command=lambda: ui._on_deconvolve()).pack(pady=5, padx=10, fill="x")

    preview_label = ctk.CTkLabel(tab, text="", fg_color="transparent")
    ui._preview_labels["Filtros"] = preview_label


# Handlers

def on_filter_gaussian(ui: 'ImageToolUI') -> None:
    """Aplica filtro gaussiano."""
    ksize = int(ui.ksize_slider.get())
    if ksize % 2 == 0:
        ksize += 1
    ui._process_phase('_filter_gaussian', {'ksize': ksize})


def on_filter_median(ui: 'ImageToolUI') -> None:
    """Aplica filtro de mediana."""
    ksize = int(ui.ksize_slider.get())
    if ksize % 2 == 0:
        ksize += 1
    ui._process_phase('_filter_median', {'ksize': ksize})


def on_filter_mean(ui: 'ImageToolUI') -> None:
    """Aplica filtro de media."""
    ksize = int(ui.ksize_slider.get())
    if ksize % 2 == 0:
        ksize += 1
    ui._process_phase('_filter_mean', {'ksize': ksize})


def on_deconvolve(ui: 'ImageToolUI') -> None:
    """Aplica deconvolución."""
    ui._process_phase('_deconvolve', {'kernel_type': 'gaussian'})