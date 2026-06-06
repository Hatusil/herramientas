"""Input tab - URL input section."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Tuple

import customtkinter as ctk
import logging

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks

logger = logging.getLogger(__name__)


def setup_url_input(parent_frame, state: TextAnalyzerState, callbacks: AppCallbacks) -> Tuple[ctk.CTkFrame, List, ctk.CTkLabel]:
    """Build the URL input frame. Returns frame, entries list, and count label."""
    url_frame = ctk.CTkFrame(parent_frame)
    url_frame.pack(fill="x", padx=10, pady=10)
    url_frame.pack_forget()  # Hidden by default, shown when "url" selected

    # Header with count
    header = ctk.CTkFrame(url_frame, fg_color="transparent")
    header.pack(fill="x", pady=5)
    ctk.CTkLabel(header, text="🌐 URLs a cargar:").pack(side="left")
    url_count_label = ctk.CTkLabel(header, text="0 url(s)", text_color="gray")
    url_count_label.pack(side="left", padx=5)

    # Container for URL entries
    url_container = ctk.CTkFrame(url_frame)
    url_container.pack(fill="both", expand=True, pady=5)

    url_entries: List[Tuple[ctk.CTkFrame, ctk.CTkEntry]] = []

    def add_url_entry():
        """Agrega un nuevo campo de URL."""
        url_entry_frame = ctk.CTkFrame(url_container)
        url_entry_frame.pack(fill="x", pady=2)
        
        url_entry = ctk.CTkEntry(url_entry_frame, placeholder_text="https://...")
        url_entry.pack(fill="x", padx=5, pady=5, side="left", expand=True)
        
        def _remove():
            url_entry_frame.destroy()
            url_entries.remove((url_entry_frame, url_entry))
            update_count()
        
        ctk.CTkButton(url_entry_frame, text="✕", width=30, command=_remove).pack(side="right", padx=2)
        
        url_entries.append((url_entry_frame, url_entry))
        update_count()

    def update_count():
        """Actualiza el contador de URLs."""
        count = sum(1 for _, e in url_entries if e.get().strip())
        url_count_label.configure(text=f"{count} url(s)")

    # Buttons
    btn_frame = ctk.CTkFrame(url_frame, fg_color="transparent")
    btn_frame.pack(fill="x", pady=5)
    ctk.CTkButton(url_frame, text="➕ Agregar URL", command=add_url_entry).pack(in_=btn_frame, side="left", padx=5)
    ctk.CTkLabel(btn_frame, text="Escribí las URLs → luego clickea '🌐 Cargar URLs'", text_color="gray").pack(side="left", padx=10)

    # Crear primer campo de URL
    add_url_entry()

    return url_frame, url_entries, url_count_label