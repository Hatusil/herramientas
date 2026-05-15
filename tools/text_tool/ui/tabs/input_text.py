"""Input tab - Text input section."""
from __future__ import annotations
from typing import TYPE_CHECKING

import customtkinter as ctk
from core.constants import COLORS

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks


def setup_text_input(parent_frame, state: TextAnalyzerState, callbacks: AppCallbacks) -> ctk.CTkTextbox:
    """Build the direct text input area."""
    text_area = ctk.CTkTextbox(
        parent_frame, 
        wrap="word", 
        fg_color=COLORS.get("bg_input"), 
        text_color=COLORS.get("text_primary")
    )
    text_area.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Keyboard shortcuts (placeholder - to be connected to state)
    def on_paste(event):
        # Placeholder for paste handling
        pass
    
    text_area.bind("<Control-v>", on_paste)
    
    return text_area