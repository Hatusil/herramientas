"""Input tab - File input section."""
from __future__ import annotations
from typing import TYPE_CHECKING, Tuple

import customtkinter as ctk

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks


def setup_file_input(parent_frame, state: TextAnalyzerState, callbacks: AppCallbacks) -> Tuple[ctk.CTkFrame, ctk.CTkLabel]:
    """Build the file selection frame. Returns frame and label."""
    file_frame = ctk.CTkFrame(parent_frame)
    file_frame.pack(fill="x", padx=10, pady=10)
    file_frame.pack_forget()  # Hidden by default, shown when "files" selected

    ctk.CTkLabel(
        file_frame,
        text="📄 Archivos Seleccionados:",
        font=ctk.CTkFont(size=14, weight="bold"),
    ).pack(anchor="w", pady=5)

    files_label = ctk.CTkLabel(
        file_frame,
        text="No hay archivos seleccionados",
        font=ctk.CTkFont(size=12),
        text_color="gray",
        anchor="w",
        justify="left",
    )
    files_label.pack(fill="x", padx=5, pady=5)

    return file_frame, files_label