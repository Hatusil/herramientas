"""Watermark tab for PDF Tool."""
from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from tools.pdf_tool.ui.tabs.base_tab import PDFBaseTab
from core.constants import COLORS
from ui.theme_factory import create_frame, create_label, create_button, create_entry, create_option_menu, create_slider, create_radiobutton

if TYPE_CHECKING:
    from tools.pdf_tool.ui.callbacks import PDFCallbacks
    from tools.pdf_tool.ui.state import PDFState


class WatermarkTab(PDFBaseTab):
    def __init__(
        self,
        parent: ctk.CTkFrame,
        callbacks: PDFCallbacks,
        main_ui=None,
        state: "PDFState" = None,
    ):
        super().__init__(parent, callbacks, main_ui, state)

    def _setup_frame(self) -> None:
        self._frame = create_frame(self._parent, fg_color="transparent")
        self._watermark_type = ctk.StringVar(value="text")

        type_frame = create_frame(self._frame)
        type_frame.pack(fill="x", padx=10, pady=5)
        create_label(type_frame, text="Tipo:").pack(side="left", padx=5)
        create_radiobutton(
            type_frame, text="Texto", variable=self._watermark_type, value="text",
            command=self._update_inputs,
        ).pack(side="left", padx=5)
        create_radiobutton(
            type_frame, text="Imagen", variable=self._watermark_type, value="image",
            command=self._update_inputs,
        ).pack(side="left", padx=5)

        self._inputs_frame = create_frame(self._frame)
        self._inputs_frame.pack(fill="x", padx=10, pady=5)

        self._watermark_text_var = ctk.StringVar(value="WATERMARK")
        self._watermark_image_path_var = ctk.StringVar()

        self._text_frame = create_frame(self._inputs_frame)
        create_label(self._text_frame, text="Texto:").pack(side="left", padx=5)
        self._watermark_text_entry = create_entry(
            self._text_frame, width=200, textvariable=self._watermark_text_var,
        )
        self._watermark_text_entry.pack(side="left", padx=5)
        self._text_frame.pack(fill="x", padx=5, pady=5)

        self._image_frame = create_frame(self._inputs_frame)
        create_label(self._image_frame, text="Imagen:").pack(side="left", padx=5)
        self._watermark_image_entry = create_entry(
            self._image_frame, width=200, textvariable=self._watermark_image_path_var,
        )
        self._watermark_image_entry.pack(side="left", padx=5)
        create_button(
            self._image_frame, text="Examinar...",
            command=self._select_image, width=80,
        ).pack(side="left", padx=5)

        self._update_inputs()

        opts_frame = create_frame(self._frame)
        opts_frame.pack(fill="x", padx=10, pady=5)
        create_label(opts_frame, text="Tamano:").pack(side="left", padx=5)
        self._watermark_size = create_entry(opts_frame, width=60)
        self._watermark_size.insert(0, "48")
        self._watermark_size.pack(side="left", padx=5)
        create_label(opts_frame, text="Color:").pack(side="left", padx=5)
        self._watermark_color = create_entry(opts_frame, width=80)
        self._watermark_color.insert(0, COLORS.get("text_secondary", "#888888"))
        self._watermark_color.pack(side="left", padx=5)

        opacity_frame = create_frame(self._frame)
        opacity_frame.pack(fill="x", padx=10, pady=5)
        create_label(opacity_frame, text="Opacidad:").pack(side="left", padx=5)
        self._opacity_slider = create_slider(
            opacity_frame, from_=0, to=100, number_of_steps=100,
            command=self._on_opacity_change,
        )
        self._opacity_slider.set(30)
        self._opacity_slider.pack(side="left", padx=5, fill="x", expand=True)
        self._opacity_label = create_label(opacity_frame, text="30%", width=50)
        self._opacity_label.pack(side="left", padx=5)

        rotation_frame = create_frame(self._frame)
        rotation_frame.pack(fill="x", padx=10, pady=5)
        create_label(rotation_frame, text="Rotacion:").pack(side="left", padx=5)
        self._rotation_slider = create_slider(
            rotation_frame, from_=0, to=360, number_of_steps=36,
            command=self._on_rotation_change,
        )
        self._rotation_slider.set(45)
        self._rotation_slider.pack(side="left", padx=5, fill="x", expand=True)
        self._rotation_label = create_label(rotation_frame, text="45deg", width=50)
        self._rotation_label.pack(side="left", padx=5)

        pos_frame = create_frame(self._frame)
        pos_frame.pack(fill="x", padx=10, pady=5)
        create_label(pos_frame, text="Posicion:").pack(side="left", padx=5)
        self._watermark_position = create_option_menu(
            pos_frame,
            values=["center", "top-left", "top-right", "bottom-left", "bottom-right", "diagonal", "custom"],
            width=120,
        )
        self._watermark_position.set("center")
        self._watermark_position.pack(side="left", padx=5)
        create_label(pos_frame, text="X:").pack(side="left", padx=5)
        self._watermark_pos_x = create_entry(pos_frame, width=60)
        self._watermark_pos_x.pack(side="left", padx=5)
        create_label(pos_frame, text="Y:").pack(side="left", padx=5)
        self._watermark_pos_y = create_entry(pos_frame, width=60)
        self._watermark_pos_y.pack(side="left", padx=5)

        btn_frame = create_frame(self._frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)
        create_button(
            btn_frame, text="Aplicar Watermark",
            command=self._apply_watermark, height=40,
        ).pack(side="left", padx=5, fill="x", expand=True)
        create_button(
            btn_frame, text="Quitar Watermarks",
            command=self._remove_watermark, height=40,
        ).pack(side="left", padx=5, fill="x", expand=True)

        self._state.watermark_text = self._watermark_text_var
        self._state.watermark_size = self._watermark_size
        self._state.watermark_color = self._watermark_color
        self._state.watermark_opacity_slider = self._opacity_slider
        self._state.watermark_rotation_slider = self._rotation_slider
        self._state.watermark_position = self._watermark_position
        self._state.watermark_pos_x = self._watermark_pos_x
        self._state.watermark_pos_y = self._watermark_pos_y
        self._state.watermark_image_path = self._watermark_image_path_var
        self._state.watermark_type = self._watermark_type

    def get_frame(self) -> ctk.CTkFrame:
        return self._frame

    def _on_opacity_change(self, value: float) -> None:
        self._opacity_label.configure(text=f"{int(value)}%")

    def _on_rotation_change(self, value: float) -> None:
        self._rotation_label.configure(text=f"{int(value)}deg")

    def _update_inputs(self) -> None:
        if self._watermark_type.get() == "text":
            self._image_frame.pack_forget()
            self._text_frame.pack(fill="x", padx=5, pady=5)
        else:
            self._text_frame.pack_forget()
            self._image_frame.pack(fill="x", padx=5, pady=5)

    def _select_image(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imagenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos", "*.*")],
        )
        if file_path:
            self._watermark_image_path_var.set(file_path)

    def _apply_watermark(self) -> None:
        from tools.pdf_tool.ui.handlers.watermark_handler import apply_text_watermark, apply_image_watermark
        self._main_ui.watermark_text = self._watermark_text_var
        self._main_ui.watermark_size = self._watermark_size
        self._main_ui.watermark_color = self._watermark_color
        self._main_ui.watermark_opacity_slider = self._opacity_slider
        self._main_ui.watermark_rotation_slider = self._rotation_slider
        self._main_ui.watermark_position = self._watermark_position
        self._main_ui.watermark_pos_x = self._watermark_pos_x
        self._main_ui.watermark_pos_y = self._watermark_pos_y
        self._main_ui.watermark_image_path = self._watermark_image_path_var
        self._main_ui.watermark_type = self._watermark_type
        if self._watermark_type.get() == "image":
            apply_image_watermark(self._main_ui)
        else:
            apply_text_watermark(self._main_ui)

    def _remove_watermark(self) -> None:
        from tools.pdf_tool.ui.handlers.watermark_handler import remove_watermark
        remove_watermark(self._main_ui)
