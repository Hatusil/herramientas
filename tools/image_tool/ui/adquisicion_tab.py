"""
Adquisicion Tab - Carga de imágenes (archivo, URL, limpiar).

Funciones:
- setup_tab: configura la UI del tab
- on_select_image: selecciona imagen del sistema
- on_load_url: carga desde URL
- on_clear_image: limpia la imagen actual
- show_preview_adquisicion: muestra preview
"""

from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.image_tool.ui.main_ui import ImageToolUI


def setup_tab(ui: 'ImageToolUI') -> None:
    """Configura el tab de Adquisición."""
    tab = ui.tab_view.tab("Adquisici\u00f3n")

    ctk.CTkButton(tab, text="\U0001F4C2 Seleccionar imagen", command=lambda: ui._on_select_image(), height=40).pack(pady=10)

    ui.path_label = ctk.CTkLabel(tab, text="", text_color="gray", font=ctk.CTkFont(size=10))
    ui.path_label.pack(pady=2)

    url_frame = ctk.CTkFrame(tab, fg_color="transparent")
    url_frame.pack(fill="x", padx=10, pady=10)

    ctk.CTkLabel(url_frame, text="URL:").pack(side="left", padx=5)
    ui.url_entry = ctk.CTkEntry(url_frame, width=250, placeholder_text="https://ejemplo.com/imagen.jpg")
    ui.url_entry.pack(side="left", fill="x", expand=True, padx=5)

    ctk.CTkButton(url_frame, text="Cargar", command=lambda: ui._on_load_url(), width=80).pack(side="left", padx=5)

    ctk.CTkButton(tab, text="\U0001F5D1\ufe0f Limpiar", command=lambda: ui._on_clear_image(), fg_color="#dc2626", height=30).pack(pady=5)

    preview_label = ctk.CTkLabel(tab, text="", fg_color="transparent")
    ui._preview_labels["Adquisici\u00f3n"] = preview_label


# Handlers

def on_select_image(ui: 'ImageToolUI') -> None:
    """Selecciona una imagen del sistema."""
    files = filedialog.askopenfilenames(
        title="Seleccionar imagen",
        filetypes=[
            ("Im\u00e1genes", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.webp"),
            ("Todos los archivos", "*.*"),
        ],
    )
    if files:
        ui.current_image_path = files[0]
        ui.status_label.configure(text=f"\u2705 {Path(ui.current_image_path).name}", text_color="green")
        ui.path_label.configure(text=ui.current_image_path)
        from tools.image_tool.processor import _load_from_file
        result = _load_from_file(ui.current_image_path)
        if result['success']:
            ui.current_image_data = result['image_data']
            ui._show_preview_adquisicion()
        else:
            ui.status_label.configure(text=f"\u274c {result.get('error', 'Error')}", text_color="red")


def on_load_url(ui: 'ImageToolUI') -> None:
    """Carga una imagen desde URL."""
    url = ui.url_entry.get().strip()
    if not url:
        ui.status_label.configure(text="Ingrese una URL", text_color="orange")
        return
    ui.status_label.configure(text="Cargando...", text_color="blue")
    from tools.image_tool.processor import _load_from_url
    result = _load_from_url(url)
    if result['success']:
        ui.current_image_data = result['image_data']
        ui._show_preview_adquisicion()
        ui.status_label.configure(text="\u2705 Cargado desde URL", text_color="green")
        ui.url_entry.delete(0, 'end')
    else:
        ui.status_label.configure(text=f"\u274c {result.get('error', 'Error')}", text_color="red")


def on_clear_image(ui: 'ImageToolUI') -> None:
    """Limpia la imagen actual."""
    ui.current_image_path = None
    ui.current_image_data = None
    ui.status_label.configure(text="Sin imagen cargada", text_color="gray")
    ui.path_label.configure(text="")
    for label in ui._preview_labels.values():
        label.configure(image=None, text="")
    if ui._histogram_label:
        ui._histogram_label.configure(image=None, text="")


def show_preview_adquisicion(ui: 'ImageToolUI') -> None:
    """Muestra el preview en la tab de adquisición."""
    if not ui.current_image_data:
        return
    image_array = ui.current_image_data.get('array')
    if image_array is None:
        return
    pil_img = ui._array_to_pil(image_array)
    ui._show_in_tab("Adquisici\u00f3n", pil_img)