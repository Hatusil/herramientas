"""
Morfologia Tab - Operaciones morfológicas.

Funciones:
- setup_tab: configura la UI del tab
- on_erode, on_dilate, on_open, on_close
"""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.image_tool.ui.main_ui import ImageToolUI


def setup_tab(ui: 'ImageToolUI') -> None:
    """Configura el tab de Morfología."""
    tab = ui.tab_view.tab("Morfolog\u00eda")

    morph_ksize_frame = ctk.CTkFrame(tab, fg_color="transparent")
    morph_ksize_frame.pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(morph_ksize_frame, text="Kernel size (3-15):").pack()
    ui.morph_ksize_slider = ctk.CTkSlider(morph_ksize_frame, from_=3, to=15, number_of_steps=6)
    ui.morph_ksize_slider.set(3)
    ui.morph_ksize_slider.pack(fill="x", padx=10)

    ui.morph_ksize_label = ctk.CTkLabel(morph_ksize_frame, text="ksize: 3")
    ui.morph_ksize_label.pack()

    morph_ksize_slider = ui.morph_ksize_slider
    morph_ksize_label = ui.morph_ksize_label

    def update_morph_ksize(value):
        odd_val = int(value)
        if odd_val % 2 == 0:
            odd_val += 1
        morph_ksize_label.configure(text=f"ksize: {odd_val}")

    ui.morph_ksize_slider.configure(command=update_morph_ksize)

    ctk.CTkButton(tab, text="\u2796 Erosi\u00f3n", command=lambda: ui._on_erode()).pack(pady=5, padx=10, fill="x")
    ctk.CTkButton(tab, text="\u2795 Dilataci\u00f3n", command=lambda: ui._on_dilate()).pack(pady=5, padx=10, fill="x")
    ctk.CTkButton(tab, text="\U0001F331 Apertura (erosi\u00f3n+dilataci\u00f3n)", command=lambda: ui._on_open()).pack(pady=5, padx=10, fill="x")
    ctk.CTkButton(tab, text="\U0001F512 Cierre (dilataci\u00f3n+erosi\u00f3n)", command=lambda: ui._on_close()).pack(pady=5, padx=10, fill="x")

    preview_label = ctk.CTkLabel(tab, text="", fg_color="transparent")
    ui._preview_labels["Morfolog\u00eda"] = preview_label


# Handlers

def on_erode(ui: 'ImageToolUI') -> None:
    """Aplica erosión."""
    ksize = int(ui.morph_ksize_slider.get())
    if ksize % 2 == 0:
        ksize += 1
    ui._process_phase('_erode', {'kernel_size': ksize})


def on_dilate(ui: 'ImageToolUI') -> None:
    """Aplica dilatación."""
    ksize = int(ui.morph_ksize_slider.get())
    if ksize % 2 == 0:
        ksize += 1
    ui._process_phase('_dilate', {'kernel_size': ksize})


def on_open(ui: 'ImageToolUI') -> None:
    """Aplica apertura."""
    ksize = int(ui.morph_ksize_slider.get())
    if ksize % 2 == 0:
        ksize += 1
    ui._process_phase('_open', {'kernel_size': ksize})


def on_close(ui: 'ImageToolUI') -> None:
    """Aplica cierre."""
    ksize = int(ui.morph_ksize_slider.get())
    if ksize % 2 == 0:
        ksize += 1
    ui._process_phase('_close', {'kernel_size': ksize})