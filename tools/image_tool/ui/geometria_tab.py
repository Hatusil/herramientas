"""
Geometria Tab - Transformaciones geométricas.

Funciones:
- setup_tab: configura la UI del tab
- on_crop: recorta la imagen
"""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.image_tool.ui.main_ui import ImageToolUI


def setup_tab(ui: 'ImageToolUI') -> None:
    """Configura el tab de Geometría."""
    tab = ui.tab_view.tab("Geometr\u00eda")

    ctk.CTkButton(tab, text="\u2B1B Convertir a escala de grises",
                   command=lambda: ui._process_phase('_to_grayscale', {})).pack(pady=5, padx=10, fill="x")

    ctk.CTkButton(tab, text="\U0001F3A8 Convertir a HSV",
                   command=lambda: ui._process_phase('_to_hsv', {})).pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(tab, text="--- Transformaciones ---").pack(pady=5)

    crop_frame = ctk.CTkFrame(tab, fg_color="transparent")
    crop_frame.pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(crop_frame, text="Recortar (x, y, w, h):").pack()

    crop_inputs = ctk.CTkFrame(crop_frame, fg_color="transparent")
    crop_inputs.pack()

    ui.crop_x = ctk.CTkEntry(crop_inputs, width=50, placeholder_text="x")
    ui.crop_x.pack(side="left", padx=2)
    ui.crop_y = ctk.CTkEntry(crop_inputs, width=50, placeholder_text="y")
    ui.crop_y.pack(side="left", padx=2)
    ui.crop_w = ctk.CTkEntry(crop_inputs, width=50, placeholder_text="w")
    ui.crop_w.pack(side="left", padx=2)
    ui.crop_h = ctk.CTkEntry(crop_inputs, width=50, placeholder_text="h")
    ui.crop_h.pack(side="left", padx=2)

    ctk.CTkButton(crop_frame, text="\u2702\ufe0f Recortar", command=lambda: ui._on_crop()).pack(pady=5)

    resize_frame = ctk.CTkFrame(tab, fg_color="transparent")
    resize_frame.pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(resize_frame, text="Escalar (0.1 - 3.0):").pack()
    ui.scale_slider = ctk.CTkSlider(resize_frame, from_=0.1, to=3.0, number_of_steps=29)
    ui.scale_slider.set(1.0)
    ui.scale_slider.pack(fill="x", padx=10)

    ctk.CTkButton(resize_frame, text="\U0001F4D0 Redimensionar",
                   command=lambda: ui._process_phase('_resize', {'scale': ui.scale_slider.get()})).pack(pady=5)

    rotate_frame = ctk.CTkFrame(tab, fg_color="transparent")
    rotate_frame.pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(rotate_frame, text="Rotar (0-360\u00b0):").pack()
    ui.rotate_slider = ctk.CTkSlider(rotate_frame, from_=-180, to=180, number_of_steps=36)
    ui.rotate_slider.set(0)
    ui.rotate_slider.pack(fill="x", padx=10)

    ctk.CTkButton(rotate_frame, text="\U0001F504 Rotar",
                   command=lambda: ui._process_phase('_rotate', {'angle': ui.rotate_slider.get()})).pack(pady=5)

    preview_label = ctk.CTkLabel(tab, text="", fg_color="transparent")
    ui._preview_labels["Geometr\u00eda"] = preview_label


# Handlers

def on_crop(ui: 'ImageToolUI') -> None:
    """Recorta la imagen."""
    try:
        x = int(ui.crop_x.get()) if ui.crop_x.get() else 0
        y = int(ui.crop_y.get()) if ui.crop_y.get() else 0
        w = int(ui.crop_w.get()) if ui.crop_w.get() else 100
        h = int(ui.crop_h.get()) if ui.crop_h.get() else 100
        ui._process_phase('_crop_region', {'x': x, 'y': y, 'w': w, 'h': h})
    except ValueError:
        ui.status_label.configure(text="Valores inv\u00e1lidos para recorte", text_color="orange")