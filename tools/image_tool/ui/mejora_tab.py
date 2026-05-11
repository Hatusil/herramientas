"""
Mejora Tab - Histograma, brillo, contraste, gamma.

Funciones:
- setup_tab: configura la UI del tab
- on_adjust_bc: aplica brillo y contraste
"""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.image_tool.ui.main_ui import ImageToolUI


def setup_tab(ui: 'ImageToolUI') -> None:
    """Configura el tab de Mejora."""
    tab = ui.tab_view.tab("Mejora")

    ctk.CTkButton(tab, text="\U0001F4CA Calcular histograma",
                   command=lambda: ui._process_phase('_compute_histogram', {})).pack(pady=5, padx=10, fill="x")

    ctk.CTkButton(tab, text="\U0001F4C8 Ecualizar histograma",
                   command=lambda: ui._process_phase('_equalize_histogram', {})).pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(tab, text="--- Ajustes ---").pack(pady=5)

    bc_frame = ctk.CTkFrame(tab, fg_color="transparent")
    bc_frame.pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(bc_frame, text="Brillo (-1.0 a 1.0):").pack()
    ui.brightness_slider = ctk.CTkSlider(bc_frame, from_=-1.0, to=1.0, number_of_steps=20)
    ui.brightness_slider.set(0.0)
    ui.brightness_slider.pack(fill="x", padx=10)

    ctk.CTkLabel(bc_frame, text="Contraste (0.5 a 2.0):").pack()
    ui.contrast_slider = ctk.CTkSlider(bc_frame, from_=0.5, to=2.0, number_of_steps=15)
    ui.contrast_slider.set(1.0)
    ui.contrast_slider.pack(fill="x", padx=10)

    ctk.CTkButton(bc_frame, text="\u2600\ufe0f Aplicar brillo/contraste", command=lambda: ui._on_adjust_bc()).pack(pady=5)

    gamma_frame = ctk.CTkFrame(tab, fg_color="transparent")
    gamma_frame.pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(gamma_frame, text="Gamma (0.1 a 3.0):").pack()
    ui.gamma_slider = ctk.CTkSlider(gamma_frame, from_=0.1, to=3.0, number_of_steps=29)
    ui.gamma_slider.set(1.0)
    ui.gamma_slider.pack(fill="x", padx=10)

    ctk.CTkButton(gamma_frame, text="\U0001F506 Aplicar gamma",
                   command=lambda: ui._process_phase('_adjust_gamma', {'gamma': ui.gamma_slider.get()})).pack(pady=5)

    preview_label = ctk.CTkLabel(tab, text="", fg_color="transparent")
    ui._preview_labels["Mejora"] = preview_label

    ui._histogram_label = ctk.CTkLabel(tab, text="", fg_color="transparent")


# Handlers

def on_adjust_bc(ui: 'ImageToolUI') -> None:
    """Ajusta brillo y contraste."""
    ui._process_phase('_adjust_brightness_contrast', {
        'brightness': ui.brightness_slider.get(),
        'contrast': ui.contrast_slider.get(),
    })