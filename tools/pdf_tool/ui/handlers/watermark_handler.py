"""Watermark handler. R0: <80 lines."""
from __future__ import annotations
from typing import TYPE_CHECKING

from core.constants import COLORS

if TYPE_CHECKING:
    from tools.pdf_tool.ui.state import PDFState, PDFContext


def apply_text_watermark(state: "PDFState") -> None:
    """Apply text watermark to PDF."""
    if not state.ctx.files:
        state.ctx.status_label and state.ctx.status_label.configure(
            text="Seleccione un PDF primero", text_color="orange",
        )
        return
    text_var = state.watermark_text
    text_val = text_var.get() if text_var is not None else "WATERMARK"
    position = state.watermark_position
    pos_val = position.get() if position is not None else "center"
    size = state.watermark_size
    size_val = int(size.get() or 48) if size is not None else 48
    color = state.watermark_color
    color_val = color.get() if color is not None else COLORS.get("text_secondary", "#888888")
    opacity_slider = state.watermark_opacity_slider
    opacity = opacity_slider.get() / 100.0 if opacity_slider is not None else 0.3
    rotation_slider = state.watermark_rotation_slider
    rotation = int(rotation_slider.get()) if rotation_slider is not None else 45
    pos_x = state.watermark_pos_x
    pos_y = state.watermark_pos_y
    position_x = float(pos_x.get()) if pos_x is not None and pos_x.get() else None
    position_y = float(pos_y.get()) if pos_y is not None and pos_y.get() else None
    state.ctx.status_label and state.ctx.status_label.configure(
        text="Procesando...", text_color="blue",
    )
    if state.ctx.process_async is not None:
        state.ctx.process_async("text_watermark", state.ctx.files, {
            "text": text_val, "font_size": size_val, "color": color_val,
            "opacity": opacity, "rotation": rotation, "position": pos_val,
            "position_x": position_x, "position_y": position_y,
        })


def apply_image_watermark(state: "PDFState") -> None:
    """Apply image watermark to PDF."""
    if not state.ctx.files:
        state.ctx.status_label and state.ctx.status_label.configure(
            text="Seleccione un PDF primero", text_color="orange",
        )
        return
    image_path_var = state.watermark_image_path
    path_val = image_path_var.get() if image_path_var is not None else ""
    if not path_val:
        state.ctx.status_label and state.ctx.status_label.configure(
            text="Seleccione una imagen",
            text_color=COLORS.get("warning", "orange"),
        )
        return
    opacity_slider = state.watermark_opacity_slider
    opacity = opacity_slider.get() / 100.0 if opacity_slider is not None else 0.3
    position = state.watermark_position
    pos_val = position.get() if position is not None else "center"
    state.ctx.status_label and state.ctx.status_label.configure(
        text="Procesando...", text_color="blue",
    )
    if state.ctx.process_async is not None:
        state.ctx.process_async("image_watermark", state.ctx.files, {
            "image_path": path_val, "scale": 0.5, "opacity": opacity, "position": pos_val,
        })


def remove_watermark(state: "PDFState", ctx: "PDFContext") -> None:
    """Remove watermarks from PDF (widget-less)."""
    if not ctx.files:
        ctx.status_label and ctx.status_label.configure(
            text="Seleccione un PDF primero", text_color="orange",
        )
        return
    ctx.status_label and ctx.status_label.configure(
        text="Procesando...", text_color="blue",
    )
    if ctx.process_async is not None:
        ctx.process_async("remove_watermark", ctx.files, {})
