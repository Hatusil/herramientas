"""Info tab for PDF Tool."""
from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from tools.pdf_tool.ui.tabs.base_tab import PDFBaseTab
from ui.theme_factory import create_frame, create_label, create_button, create_textbox

if TYPE_CHECKING:
    from tools.pdf_tool.ui.callbacks import PDFCallbacks


class InfoTab(PDFBaseTab):
    def __init__(self, parent: ctk.CTkFrame, callbacks: PDFCallbacks, main_ui=None):
        super().__init__(parent, callbacks, main_ui)

    def _setup_frame(self) -> None:
        self._frame = create_frame(self._parent, fg_color="transparent")
        info_frame = create_frame(self._frame)
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        create_label(
            info_frame, text="Informacion del PDF:", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="n", pady=5)
        self._info_text = create_textbox(
            info_frame, width=400, height=200,
        )
        self._info_text.pack(padx=10, pady=10, fill="both", expand=True)
        create_button(
            info_frame, text="Ver Informacion",
            command=self._run_analysis,
        ).pack(pady=5)

    def get_frame(self) -> ctk.CTkFrame:
        return self._frame

    def on_tab_selected(self) -> None:
        self._run_analysis()

    def _run_analysis(self) -> None:
        from tools.pdf_tool.ui.handlers.info_handler import get_pdf_info
        self._main_ui.info_text = self._info_text
        get_pdf_info(self._main_ui)
