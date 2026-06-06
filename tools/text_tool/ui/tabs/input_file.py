"""Input tab - File input section."""
from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List

import customtkinter as ctk
import os

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks


def setup_file_input(parent_frame, state: TextAnalyzerState, callbacks: AppCallbacks) -> Tuple[ctk.CTkFrame, ctk.CTkLabel, List[str]]:
    """Build the file selection frame. Returns frame, label, and pending files list."""
    file_frame = ctk.CTkFrame(parent_frame)
    file_frame.pack(fill="x", padx=10, pady=10)
    file_frame.pack_forget()  # Hidden by default, shown when "files" selected

    # Pending files list
    pending_files: List[str] = []

    # Header with count
    header = ctk.CTkFrame(file_frame, fg_color="transparent")
    header.pack(fill="x", pady=5)
    ctk.CTkLabel(
        header,
        text="📄 Archivos seleccionados:",
        font=ctk.CTkFont(size=14, weight="bold"),
    ).pack(side="left")
    
    count_label = ctk.CTkLabel(header, text="0", text_color="gray")
    count_label.pack(side="left", padx=5)

    # File list container
    list_frame = ctk.CTkScrollableFrame(file_frame, height=120)
    list_frame.pack(fill="x", pady=5)
    
    list_label = ctk.CTkLabel(
        list_frame,
        text="Ninguno — click en 'Agregar' para seleccionar",
        text_color="gray",
        anchor="w",
    )
    list_label.pack(fill="x", padx=5, pady=10)

    def _add_files():
        """Add files to pending list."""
        from tkinter import filedialog
        files = filedialog.askopenfilenames(
            title="Seleccionar archivos",
            filetypes=[
                ("Todos", "*.*"),
                ("PDF", "*.pdf"),
                ("Word", "*.docx"),
                ("Excel", "*.xlsx"),
                ("CSV", "*.csv"),
                ("Texto", "*.txt *.md"),
            ]
        )
        if files:
            for f in files:
                if f not in pending_files:
                    pending_files.append(f)
            _update_list()

    def _clear_files():
        """Clear pending files."""
        pending_files.clear()
        _update_list()

    def _update_list():
        """Refresh the file list display."""
        count_label.configure(text=str(len(pending_files)))
        if pending_files:
            list_label.configure(text="\n".join(os.path.basename(f) for f in pending_files), text_color="white")
        else:
            list_label.configure(text="Ninguno — click en 'Agregar' para seleccionar", text_color="gray")

    # Buttons
    btn_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
    btn_frame.pack(fill="x", pady=5)
    
    ctk.CTkButton(btn_frame, text="➕ Agregar", command=_add_files, width=80).pack(side="left", padx=2)
    ctk.CTkButton(btn_frame, text="🗑️ Limpiar", command=_clear_files, width=80).pack(side="left", padx=2)

    return file_frame, count_label, pending_files