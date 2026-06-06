"""Numbers tab for PDF Tool."""
from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from tools.pdf_tool.ui.tabs.base_tab import PDFBaseTab
from ui.theme_factory import create_frame, create_label, create_button, create_entry, create_option_menu

if TYPE_CHECKING:
    from tools.pdf_tool.ui.callbacks import PDFCallbacks


class NumbersTab(PDFBaseTab):
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
        num_frame = create_frame(self._frame)
        num_frame.pack(fill="x", padx=10, pady=5)
        create_label(
            num_frame, text="Agregar numeros de pagina:", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=5)
        opts = create_frame(num_frame, fg_color="transparent")
        opts.pack(fill="x", padx=5)
        create_label(opts, text="Posicion:").pack(side="left", padx=5)
        self._num_position = create_option_menu(
            opts, values=["footer", "header"], width=100
        )
        self._num_position.set("footer")
        self._num_position.pack(side="left", padx=5)
        create_label(opts, text="Inicio:").pack(side="left", padx=5)
        self._num_start = create_entry(opts, width=50)
        self._num_start.insert(0, "1")
        self._num_start.pack(side="left", padx=5)
        create_label(opts, text="Formato:").pack(side="left", padx=5)
        self._num_format = create_entry(opts, width=120)
        self._num_format.insert(0, "Pagina {n} de {total}")
        self._num_format.pack(side="left", padx=5)
        create_button(
            num_frame, text="Agregar Numeros",
            command=self._add_numbers, height=40,
        ).pack(pady=10)

        self._state.num_position = self._num_position
        self._state.num_start = self._num_start
        self._state.num_format = self._num_format

    def get_frame(self) -> ctk.CTkFrame:
        return self._frame

    def _add_numbers(self) -> None:
        from tools.pdf_tool.ui.handlers.numbers_handler import add_page_numbers
        self._main_ui.num_position = self._num_position
        self._main_ui.num_start = self._num_start
        self._main_ui.num_format = self._num_format
        add_page_numbers(self._main_ui)
