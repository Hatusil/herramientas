"""Input tab - URL input section."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Tuple

import customtkinter as ctk
import logging

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks

logger = logging.getLogger(__name__)


def setup_url_input(parent_frame, state: TextAnalyzerState, callbacks: AppCallbacks) -> Tuple[ctk.CTkFrame, List]:
    """Build the URL input frame."""
    url_frame = ctk.CTkFrame(parent_frame)
    url_frame.pack(fill="x", padx=10, pady=10)
    url_frame.pack_forget()  # Hidden by default, shown when "url" selected

    ctk.CTkLabel(url_frame, text="URLs:").pack(anchor="w")

    url_container = ctk.CTkFrame(url_frame)
    url_container.pack(fill="both", expand=True, pady=5)

    url_btns = ctk.CTkFrame(url_frame, fg_color="transparent")
    url_btns.pack(fill="x", pady=5)

    # Lista de entries para URLs
    url_entries: List[Tuple[ctk.CTkFrame, ctk.CTkEntry]] = []
    
    def add_url_entry():
        """Agrega un nuevo campo de URL."""
        url_entry_frame = ctk.CTkFrame(url_container)
        url_entry_frame.pack(fill="x", pady=2)
        url_entry = ctk.CTkEntry(url_entry_frame, placeholder_text="https://...")
        url_entry.pack(fill="x", padx=5, pady=5)
        url_entries.append((url_entry_frame, url_entry))
        update_count()
        logger.info(f"➕ Nueva URL añadida ({len(url_entries)} total)")

    def update_count():
        """Actualiza el contador de URLs."""
        url_count_label.configure(text=f"{len(url_entries)} URL(s)")

    # Botón para agregar más URLs
    ctk.CTkButton(
        url_btns, text="➕ Agregar URL", command=add_url_entry
    ).pack(side="left", padx=5)

    url_count_label = ctk.CTkLabel(url_btns, text="1 URL", text_color="gray")
    url_count_label.pack(side="left", padx=10)

    # Crear primer campo de URL
    url_entry_frame = ctk.CTkFrame(url_container)
    url_entry_frame.pack(fill="x", pady=2)
    url_entry = ctk.CTkEntry(url_entry_frame, placeholder_text="https://...")
    url_entry.pack(fill="x", padx=5, pady=5)
    url_entries.append((url_entry_frame, url_entry))

    return url_frame, url_entries