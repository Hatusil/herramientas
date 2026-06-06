"""Transform tab for PDF Tool."""
from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from tools.pdf_tool.ui.tabs.base_tab import PDFBaseTab
from ui.theme_factory import create_frame, create_label, create_button, create_entry, create_radiobutton

if TYPE_CHECKING:
    from tools.pdf_tool.ui.callbacks import PDFCallbacks


class TransformTab(PDFBaseTab):
    def __init__(self, parent: ctk.CTkFrame, callbacks: PDFCallbacks, main_ui=None):
        super().__init__(parent, callbacks, main_ui)

    def _setup_frame(self) -> None:
        self._frame = create_frame(self._parent, fg_color="transparent")
        rotate_frame = create_frame(self._frame)
        rotate_frame.pack(fill="x", padx=10, pady=5)
        create_label(
            rotate_frame, text="Rotar paginas:", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=5)
        rot_opts = create_frame(rotate_frame, fg_color="transparent")
        rot_opts.pack(fill="x", padx=5)
        self._rotate_var = ctk.StringVar(value="90")
        for deg in ["90", "180", "270"]:
            create_radiobutton(
                rot_opts, text=f"{deg}deg", variable=self._rotate_var, value=deg,
            ).pack(side="left", padx=10)
        create_label(
            rot_opts, text="Paginas (vacio=todas):"
        ).pack(side="left", padx=(20, 5))
        self._rotate_pages = create_entry(rot_opts, width=100)
        self._rotate_pages.pack(side="left", padx=5)
        create_button(
            rotate_frame, text="Rotar", command=self._rotate_pages
        ).pack(pady=5)

        reorder_frame = create_frame(self._frame)
        reorder_frame.pack(fill="x", padx=10, pady=5)
        create_label(
            reorder_frame, text="Reordenar paginas:", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=5)
        create_label(
            reorder_frame, text="Nuevo orden (ej: 3,1,2):"
        ).pack(anchor="w", padx=10)
        self._reorder_input = create_entry(reorder_frame, width=200)
        self._reorder_input.pack(padx=10, pady=5)
        create_button(
            reorder_frame, text="Reordenar", command=self._reorder_pages
        ).pack(pady=5)

    def get_frame(self) -> ctk.CTkFrame:
        return self._frame

    def _rotate_pages(self) -> None:
        from tools.pdf_tool.ui.handlers.transform_handler import rotate_pages
        self._main_ui.rotate_var = self._rotate_var
        self._main_ui.rotate_pages = self._rotate_pages
        rotate_pages(self._main_ui)

    def _reorder_pages(self) -> None:
        from tools.pdf_tool.ui.handlers.transform_handler import reorder_pages
        self._main_ui.reorder_input = self._reorder_input
        reorder_pages(self._main_ui)
