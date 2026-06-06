"""Optimize tab for PDF Tool."""
from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from tools.pdf_tool.ui.tabs.base_tab import PDFBaseTab
from ui.theme_factory import create_frame, create_label, create_button, create_option_menu

if TYPE_CHECKING:
    from tools.pdf_tool.ui.callbacks import PDFCallbacks


class OptimizeTab(PDFBaseTab):
    def __init__(self, parent: ctk.CTkFrame, callbacks: PDFCallbacks, main_ui=None):
        super().__init__(parent, callbacks, main_ui)

    def _setup_frame(self) -> None:
        self._frame = create_frame(self._parent, fg_color="transparent")
        compress_frame = create_frame(self._frame)
        compress_frame.pack(fill="x", padx=10, pady=5)
        create_label(
            compress_frame, text="Comprimir PDF:", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=5)
        comp_opts = create_frame(compress_frame, fg_color="transparent")
        comp_opts.pack(fill="x", padx=5)
        create_label(comp_opts, text="Nivel:").pack(side="left", padx=5)
        self._compress_level = create_option_menu(
            comp_opts, values=["low", "medium", "high"], width=100
        )
        self._compress_level.set("medium")
        self._compress_level.pack(side="left", padx=5)
        create_button(
            compress_frame, text="Comprimir", command=self._compress, height=40,
        ).pack(pady=5)

        clean_frame = create_frame(self._frame)
        clean_frame.pack(fill="x", padx=10, pady=5)
        create_label(
            clean_frame, text="Limpiar metadatos:", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=5)
        create_button(
            clean_frame, text="Limpiar Metadatos", command=self._clean, height=40,
        ).pack(pady=5)

    def get_frame(self) -> ctk.CTkFrame:
        return self._frame

    def _compress(self) -> None:
        from tools.pdf_tool.ui.handlers.optimize_handler import compress_pdf
        self._main_ui.compress_level = self._compress_level
        compress_pdf(self._main_ui)

    def _clean(self) -> None:
        from tools.pdf_tool.ui.handlers.optimize_handler import clean_metadata
        clean_metadata(self._main_ui)
