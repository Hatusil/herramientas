"""Watermark handler. R0: <80 lines."""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any

from core.constants import COLORS

if TYPE_CHECKING:
    from tools.pdf_tool.ui.main_ui import PDFToolUI


def apply_text_watermark(ui: PDFToolUI) -> None:
    """Apply text watermark to PDF."""
    if not ui._check_files():
        return
    text = getattr(ui, "watermark_text", None)
    text_val = text.get() if text and hasattr(text, "get") else "WATERMARK"
    position = getattr(ui, "watermark_position", None)
    pos_val = position.get() if position and hasattr(position, "get") else "center"
    size = getattr(ui, "watermark_size", None)
    size_val = int(size.get() or 48) if size and hasattr(size, "get") else 48
    color = getattr(ui, "watermark_color", None)
    color_val = color.get() if color and hasattr(color, "get") else COLORS.get("text_secondary", "#888888")
    opacity_slider = getattr(ui, "watermark_opacity_slider", None)
    opacity = opacity_slider.get() / 100.0 if opacity_slider else 0.3
    rotation_slider = getattr(ui, "watermark_rotation_slider", None)
    rotation = int(rotation_slider.get()) if rotation_slider else 45
    pos_x = getattr(ui, "watermark_pos_x", None)
    pos_y = getattr(ui, "watermark_pos_y", None)
    position_x = float(pos_x.get()) if pos_x and pos_x.get() else None
    position_y = float(pos_y.get()) if pos_y and pos_y.get() else None

    ui.status_label.configure(text="Procesando...", text_color="blue")
    ui.process_async("text_watermark", ui.files, {
        "text": text_val,
        "font_size": size_val,
        "color": color_val,
        "opacity": opacity,
        "rotation": rotation,
        "position": pos_val,
        "position_x": position_x,
        "position_y": position_y,
    })


def apply_image_watermark(ui: PDFToolUI) -> None:
    """Apply image watermark to PDF."""
    if not ui._check_files():
        return
    image_path = getattr(ui, "watermark_image_path", None)
    path_val = image_path.get() if image_path and hasattr(image_path, "get") else ""
    if not path_val:
        ui.status_label.configure(text="Seleccione una imagen", text_color=COLORS.get("warning", "orange"))
        return
    opacity_slider = getattr(ui, "watermark_opacity_slider", None)
    opacity = opacity_slider.get() / 100.0 if opacity_slider else 0.3
    position = getattr(ui, "watermark_position", None)
    pos_val = position.get() if position and hasattr(position, "get") else "center"

    ui.status_label.configure(text="Procesando...", text_color="blue")
    ui.process_async("image_watermark", ui.files, {
        "image_path": path_val,
        "scale": 0.5,
        "opacity": opacity,
        "position": pos_val,
    })


def remove_watermark(ui: PDFToolUI) -> None:
    """Remove watermarks from PDF."""
    if not ui._check_files():
        return
    ui.status_label.configure(text="Procesando...", text_color="blue")
    ui.process_async("remove_watermark", ui.files, {})
