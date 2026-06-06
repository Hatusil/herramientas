"""Edit tab for PDF Tool."""
from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from tools.pdf_tool.ui.tabs.base_tab import PDFBaseTab
from ui.theme_factory import create_frame, create_label, create_button, create_entry

if TYPE_CHECKING:
    from tools.pdf_tool.ui.callbacks import PDFCallbacks


class EditTab(PDFBaseTab):
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
        ann_frame = create_frame(self._frame)
        ann_frame.pack(fill="x", padx=10, pady=5)
        create_label(
            ann_frame, text="Agregar Anotacion:", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=5)
        pos_frame = create_frame(ann_frame, fg_color="transparent")
        pos_frame.pack(fill="x", padx=5)
        create_label(pos_frame, text="Texto:").pack(side="left", padx=5)
        self._annot_text = create_entry(pos_frame, width=150)
        self._annot_text.pack(side="left", padx=5)
        create_label(pos_frame, text="Pagina:").pack(side="left", padx=5)
        self._annot_page = create_entry(pos_frame, width=50)
        self._annot_page.insert(0, "0")
        self._annot_page.pack(side="left", padx=5)
        create_label(pos_frame, text="X:").pack(side="left", padx=5)
        self._annot_x = create_entry(pos_frame, width=50)
        self._annot_x.insert(0, "100")
        self._annot_x.pack(side="left", padx=5)
        create_label(pos_frame, text="Y:").pack(side="left", padx=5)
        self._annot_y = create_entry(pos_frame, width=50)
        self._annot_y.insert(0, "100")
        self._annot_y.pack(side="left", padx=5)
        create_button(
            ann_frame, text="Agregar Anotacion", command=self._add_annotation
        ).pack(pady=5)

        redact_frame = create_frame(self._frame)
        redact_frame.pack(fill="x", padx=10, pady=5)
        create_label(
            redact_frame, text="Censurar Area:", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=5)
        redact_pos = create_frame(redact_frame, fg_color="transparent")
        redact_pos.pack(fill="x", padx=5)
        create_label(redact_pos, text="Pagina:").pack(side="left", padx=5)
        self._redact_page = create_entry(redact_pos, width=50)
        self._redact_page.insert(0, "0")
        self._redact_page.pack(side="left", padx=5)
        create_label(redact_pos, text="X:").pack(side="left", padx=5)
        self._redact_x = create_entry(redact_pos, width=50)
        self._redact_x.insert(0, "100")
        self._redact_x.pack(side="left", padx=5)
        create_label(redact_pos, text="Y:").pack(side="left", padx=5)
        self._redact_y = create_entry(redact_pos, width=50)
        self._redact_y.insert(0, "100")
        self._redact_y.pack(side="left", padx=5)
        create_label(redact_pos, text="Ancho:").pack(side="left", padx=5)
        self._redact_w = create_entry(redact_pos, width=50)
        self._redact_w.insert(0, "100")
        self._redact_w.pack(side="left", padx=5)
        create_label(redact_pos, text="Alto:").pack(side="left", padx=5)
        self._redact_h = create_entry(redact_pos, width=50)
        self._redact_h.insert(0, "30")
        self._redact_h.pack(side="left", padx=5)
        create_button(
            redact_frame, text="Censurar", command=self._redact_area
        ).pack(pady=5)

        extract_frame = create_frame(self._frame)
        extract_frame.pack(fill="x", padx=10, pady=5)
        create_label(
            extract_frame, text="Extraer paginas:", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=5)
        range_frame = create_frame(extract_frame, fg_color="transparent")
        range_frame.pack(fill="x", padx=5)
        create_label(range_frame, text="Desde:").pack(side="left", padx=5)
        self._extract_start = create_entry(range_frame, width=50)
        self._extract_start.insert(0, "1")
        self._extract_start.pack(side="left", padx=5)
        create_label(range_frame, text="Hasta:").pack(side="left", padx=5)
        self._extract_end = create_entry(range_frame, width=50)
        self._extract_end.insert(0, "1")
        self._extract_end.pack(side="left", padx=5)
        create_button(
            extract_frame, text="Extraer Rango", command=self._extract_range
        ).pack(pady=5)

        self._state.annot_text = self._annot_text
        self._state.annot_page = self._annot_page
        self._state.annot_x = self._annot_x
        self._state.annot_y = self._annot_y
        self._state.redact_page = self._redact_page
        self._state.redact_x = self._redact_x
        self._state.redact_y = self._redact_y
        self._state.redact_w = self._redact_w
        self._state.redact_h = self._redact_h
        self._state.extract_start = self._extract_start
        self._state.extract_end = self._extract_end

    def get_frame(self) -> ctk.CTkFrame:
        return self._frame

    def _add_annotation(self) -> None:
        from tools.pdf_tool.ui.handlers.edit_handler import add_annotation
        add_annotation(self._state)

    def _redact_area(self) -> None:
        from tools.pdf_tool.ui.handlers.edit_handler import redact_area
        redact_area(self._state)

    def _extract_range(self) -> None:
        from tools.pdf_tool.ui.handlers.combine_handler import extract_range
        extract_range(self._state)
