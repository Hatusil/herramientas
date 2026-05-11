"""
Watermark Tab - Agregar y quitar watermarks.

Funciones:
- setup_watermark_tab: configura la UI del tab
- apply_text_watermark: aplica watermark de texto
- remove_watermark: elimina watermarks
- handlers de sliders y selectors
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.pdf_tool.ui.main_ui import PDFToolUI


def setup_watermark_tab(ui: 'PDFToolUI') -> None:
    """Configura el tab de Watermark."""
    frame = ui.tab_watermark

    # Toggle para tipo de watermark (texto vs imagen)
    ui.watermark_type = ctk.StringVar(value="text")

    type_frame = ctk.CTkFrame(frame)
    type_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(type_frame, text="Tipo:").pack(side="left", padx=5)
    ctk.CTkRadioButton(
        type_frame,
        text="Texto",
        variable=ui.watermark_type,
        value="text",
        command=lambda: ui._update_watermark_inputs()
    ).pack(side="left", padx=5)
    ctk.CTkRadioButton(
        type_frame,
        text="Imagen",
        variable=ui.watermark_type,
        value="image",
        command=lambda: ui._update_watermark_inputs()
    ).pack(side="left", padx=5)

    # Contenedor para inputs
    ui.watermark_inputs_frame = ctk.CTkFrame(frame)
    ui.watermark_inputs_frame.pack(fill="x", padx=10, pady=5)

    # Texto inicial
    text_frame = ctk.CTkFrame(ui.watermark_inputs_frame)
    text_frame.pack(fill="x", padx=5, pady=5)

    ctk.CTkLabel(text_frame, text="Texto:").pack(side="left", padx=5)
    ui.watermark_text = ctk.CTkEntry(text_frame, width=200)
    ui.watermark_text.insert(0, "WATERMARK")
    ui.watermark_text.pack(side="left", padx=5)

    # Imagen (inicialmente oculto)
    ui.image_frame = ctk.CTkFrame(ui.watermark_inputs_frame)

    ctk.CTkLabel(ui.image_frame, text="Imagen:").pack(side="left", padx=5)
    ui.watermark_image_path = ctk.CTkEntry(ui.image_frame, width=200)
    ui.watermark_image_path.pack(side="left", padx=5)

    ctk.CTkButton(
        ui.image_frame,
        text="Examinar...",
        command=lambda: ui._select_watermark_image(),
        width=80
    ).pack(side="left", padx=5)

    # Opciones avanzadas
    options_frame = ctk.CTkFrame(frame)
    options_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(options_frame, text="Tamaño:").pack(side="left", padx=5)
    ui.watermark_size = ctk.CTkEntry(options_frame, width=60)
    ui.watermark_size.insert(0, "48")
    ui.watermark_size.pack(side="left", padx=5)

    ctk.CTkLabel(options_frame, text="Color:").pack(side="left", padx=5)
    ui.watermark_color = ctk.CTkEntry(options_frame, width=80)
    ui.watermark_color.insert(0, "#888888")
    ui.watermark_color.pack(side="left", padx=5)

    # Opacity slider
    opacity_frame = ctk.CTkFrame(frame)
    opacity_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(opacity_frame, text="Opacidad:").pack(side="left", padx=5)
    ui.watermark_opacity_slider = ctk.CTkSlider(
        opacity_frame,
        from_=0,
        to=100,
        number_of_steps=100,
        command=lambda v: ui._on_opacity_slider_change(v)
    )
    ui.watermark_opacity_slider.set(30)
    ui.watermark_opacity_slider.pack(side="left", padx=5, fill="x", expand=True)

    ui.watermark_opacity_label = ctk.CTkLabel(opacity_frame, text="30%", width=50)
    ui.watermark_opacity_label.pack(side="left", padx=5)

    # Rotation slider
    rotation_frame = ctk.CTkFrame(frame)
    rotation_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(rotation_frame, text="Rotación:").pack(side="left", padx=5)
    ui.watermark_rotation_slider = ctk.CTkSlider(
        rotation_frame,
        from_=0,
        to=360,
        number_of_steps=36,
        command=lambda v: ui._on_rotation_slider_change(v)
    )
    ui.watermark_rotation_slider.set(45)
    ui.watermark_rotation_slider.pack(side="left", padx=5, fill="x", expand=True)

    ui.watermark_rotation_label = ctk.CTkLabel(rotation_frame, text="45°", width=50)
    ui.watermark_rotation_label.pack(side="left", padx=5)

    # Position
    position_frame = ctk.CTkFrame(frame)
    position_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(position_frame, text="Posición:").pack(side="left", padx=5)
    ui.watermark_position = ctk.CTkOptionMenu(
        position_frame,
        values=["center", "top-left", "top-right", "bottom-left", "bottom-right", "diagonal", "custom"],
        width=120
    )
    ui.watermark_position.set("center")
    ui.watermark_position.pack(side="left", padx=5)

    ctk.CTkLabel(position_frame, text="X:").pack(side="left", padx=5)
    ui.watermark_pos_x = ctk.CTkEntry(position_frame, width=60)
    ui.watermark_pos_x.insert(0, "")
    ui.watermark_pos_x.pack(side="left", padx=5)

    ctk.CTkLabel(position_frame, text="Y:").pack(side="left", padx=5)
    ui.watermark_pos_y = ctk.CTkEntry(position_frame, width=60)
    ui.watermark_pos_y.insert(0, "")
    ui.watermark_pos_y.pack(side="left", padx=5)

    # Botones
    btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
    btn_frame.pack(fill="x", padx=10, pady=10)

    ctk.CTkButton(
        btn_frame,
        text="Aplicar Watermark",
        command=lambda: ui._apply_text_watermark(),
        height=40
    ).pack(side="left", padx=5, fill="x", expand=True)

    ctk.CTkButton(
        btn_frame,
        text="Quitar Watermarks",
        command=lambda: ui._remove_watermark(),
        height=40
    ).pack(side="left", padx=5, fill="x", expand=True)


# Handlers

def on_opacity_slider_change(ui: 'PDFToolUI', value: float) -> None:
    """Actualiza la etiqueta de opacidad."""
    ui.watermark_opacity_label.configure(text=f"{int(value)}%")


def on_rotation_slider_change(ui: 'PDFToolUI', value: float) -> None:
    """Actualiza la etiqueta de rotación."""
    ui.watermark_rotation_label.configure(text=f"{int(value)}°")


def update_watermark_inputs(ui: 'PDFToolUI') -> None:
    """Actualiza los inputs según el tipo de watermark."""
    for widget in ui.watermark_inputs_frame.winfo_children():
        widget.destroy()

    if ui.watermark_type.get() == "text":
        text_frame = ctk.CTkFrame(ui.watermark_inputs_frame)
        text_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(text_frame, text="Texto:").pack(side="left", padx=5)
        ui.watermark_text = ctk.CTkEntry(text_frame, width=200)
        ui.watermark_text.insert(0, "WATERMARK")
        ui.watermark_text.pack(side="left", padx=5)
    else:
        img_frame = ctk.CTkFrame(ui.watermark_inputs_frame)
        img_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(img_frame, text="Imagen:").pack(side="left", padx=5)
        ui.watermark_image_path = ctk.CTkEntry(img_frame, width=200)
        ui.watermark_image_path.pack(side="left", padx=5)

        ctk.CTkButton(
            img_frame,
            text="Examinar...",
            command=lambda: ui._select_watermark_image(),
            width=80
        ).pack(side="left", padx=5)


def select_watermark_image(ui: 'PDFToolUI') -> None:
    """Selecciona una imagen para watermark."""
    file_path = filedialog.askopenfilename(
        title="Seleccionar imagen",
        filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos", "*.*")]
    )
    if file_path:
        ui.watermark_image_path.delete(0, tk.END)
        ui.watermark_image_path.insert(0, file_path)


def apply_text_watermark(ui: 'PDFToolUI') -> None:
    """Aplica watermark de texto o imagen."""
    if not ui._check_files():
        return

    ui.status_label.configure(text="Procesando...", text_color="blue")

    if ui.watermark_type.get() == "image":
        image_path = ui.watermark_image_path.get()
        if not image_path:
            ui.status_label.configure(text="Seleccione una imagen", text_color="#FFA500")
            return

        result = ui.process_async('image_watermark', ui.files, {
            'image_path': image_path,
            'scale': 0.5,
            'opacity': ui.watermark_opacity_slider.get() / 100.0,
            'position': ui.watermark_position.get(),
        })
    else:
        text = ui.watermark_text.get() or "WATERMARK"

        position = ui.watermark_position.get()
        position_x = None
        position_y = None

        if position == 'custom':
            try:
                position_x = float(ui.watermark_pos_x.get()) if ui.watermark_pos_x.get() else None
                position_y = float(ui.watermark_pos_y.get()) if ui.watermark_pos_y.get() else None
            except ValueError:
                ui.status_label.configure(text="Coordenadas inválidas", text_color="red")
                return

        result = ui.process_async('text_watermark', ui.files, {
            'text': text,
            'font_size': int(ui.watermark_size.get() or 48),
            'color': ui.watermark_color.get() or '#888888',
            'opacity': ui.watermark_opacity_slider.get() / 100.0,
            'rotation': int(ui.watermark_rotation_slider.get()),
            'position': position,
            'position_x': position_x,
            'position_y': position_y,
        })

    ui._show_result(result)


def remove_watermark(ui: 'PDFToolUI') -> None:
    """Quita watermarks del PDF."""
    if not ui._check_files():
        return

    ui.status_label.configure(text="Procesando...", text_color="blue")

    result = ui.process_async('remove_watermark', ui.files, {})

    ui._show_result(result)