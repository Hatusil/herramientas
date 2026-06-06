"""Combine tab for PDF Tool."""
from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from tools.pdf_tool.ui.tabs.base_tab import PDFBaseTab
from ui.theme_factory import create_frame, create_label, create_secondary_label, create_button, create_entry

if TYPE_CHECKING:
    from tools.pdf_tool.ui.callbacks import PDFCallbacks


class CombineTab(PDFBaseTab):
    def __init__(
        self,
        parent: ctk.CTkFrame,
        callbacks: PDFCallbacks,
        main_ui=None,
        state=None,
    ):
        super().__init__(parent, callbacks, main_ui, state)

    def _setup_frame(self) -> None:
        self._frame = create_frame(self._parent, fg_color="transparent")
        merge_frame = create_frame(self._frame)
        merge_frame.pack(fill="x", padx=10, pady=5)
        create_label(
            merge_frame, text="Combinar PDFs:", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=5)
        create_secondary_label(
            merge_frame,
            text="Seleccione multiples PDFs en el selector de archivos",
        ).pack(anchor="w", padx=10)
        create_button(
            merge_frame, text="Combinar en un PDF",
            command=self._merge, height=40,
        ).pack(pady=5)

        extract_frame = create_frame(self._frame)
        extract_frame.pack(fill="x", padx=10, pady=5)
        create_label(
            extract_frame, text="Extraer paginas:", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=5)
        create_label(
            extract_frame, text="Paginas (ej: 1,3,5 o 1-5):"
        ).pack(anchor="w", padx=10)
        self._extract_pages = create_entry(extract_frame, width=200)
        self._extract_pages.pack(padx=10, pady=5)
        create_button(
            extract_frame, text="Extraer", command=self._extract
        ).pack(pady=5)

        self._state.extract_pages = self._extract_pages

    def get_frame(self) -> ctk.CTkFrame:
        return self._frame

    def _merge(self) -> None:
        from tools.pdf_tool.ui.handlers.combine_handler import merge_pdfs
        merge_pdfs(self._state, self._state.ctx)

    def _extract(self) -> None:
        from tools.pdf_tool.ui.handlers.combine_handler import extract_pages
        extract_pages(self._state)
