"""
Bordes Tab - Detección de bordes.

Funciones:
- setup_tab: configura la UI del tab
- on_canny, on_bounding_boxes
"""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.image_tool.ui.main_ui import ImageToolUI


def setup_tab(ui: 'ImageToolUI') -> None:
    """Configura el tab de Bordes."""
    tab = ui.tab_view.tab("Bordes")

    ctk.CTkButton(tab, text="\u2194\ufe0f Sobel",
                   command=lambda: ui._process_phase('_edge_sobel', {})).pack(pady=5, padx=10, fill="x")
    ctk.CTkButton(tab, text="\u2194\ufe0f Prewitt",
                   command=lambda: ui._process_phase('_edge_prewitt', {})).pack(pady=5, padx=10, fill="x")
    ctk.CTkButton(tab, text="\U0001F53A Laplaciano",
                   command=lambda: ui._process_phase('_edge_laplacian', {})).pack(pady=5, padx=10, fill="x")

    canny_frame = ctk.CTkFrame(tab, fg_color="transparent")
    canny_frame.pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(canny_frame, text="Threshold 1 (bajo):").pack()
    ui.canny_t1 = ctk.CTkSlider(canny_frame, from_=0, to=255, number_of_steps=25)
    ui.canny_t1.set(50)
    ui.canny_t1.pack(fill="x", padx=10)

    ctk.CTkLabel(canny_frame, text="Threshold 2 (alto):").pack()
    ui.canny_t2 = ctk.CTkSlider(canny_frame, from_=0, to=255, number_of_steps=25)
    ui.canny_t2.set(150)
    ui.canny_t2.pack(fill="x", padx=10)

    ctk.CTkButton(canny_frame, text="\u2B55 Canny", command=lambda: ui._on_canny()).pack(pady=5)

    ctk.CTkLabel(tab, text="--- An\u00e1lisis de contornos ---").pack(pady=5)

    ctk.CTkButton(tab, text="\U0001F50D Encontrar contornos",
                   command=lambda: ui._process_phase('_find_contours', {})).pack(pady=5, padx=10, fill="x")

    bbox_frame = ctk.CTkFrame(tab, fg_color="transparent")
    bbox_frame.pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(bbox_frame, text="\u00c1rea m\u00ednima:").pack()
    ui.min_area_entry = ctk.CTkEntry(bbox_frame, width=100)
    ui.min_area_entry.insert(0, "100")
    ui.min_area_entry.pack(pady=2)

    ctk.CTkButton(bbox_frame, text="\U0001F4E6 Bounding boxes", command=lambda: ui._on_bounding_boxes()).pack(pady=5)

    preview_label = ctk.CTkLabel(tab, text="", fg_color="transparent")
    ui._preview_labels["Bordes"] = preview_label


# Handlers

def on_canny(ui: 'ImageToolUI') -> None:
    """Aplica detector de bordes Canny."""
    ui._process_phase('_edge_canny', {
        'threshold1': int(ui.canny_t1.get()),
        'threshold2': int(ui.canny_t2.get()),
    })


def on_bounding_boxes(ui: 'ImageToolUI') -> None:
    """Muestra bounding boxes."""
    try:
        min_area = int(ui.min_area_entry.get()) if ui.min_area_entry.get() else 100
        ui._process_phase('_bounding_boxes', {'min_area': min_area})
    except ValueError:
        ui.status_label.configure(text="\u00c1rea m\u00ednima inv\u00e1lida", text_color="orange")