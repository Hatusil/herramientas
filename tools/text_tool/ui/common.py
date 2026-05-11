"""Common UI components for Text Analyzer."""
import logging
from typing import Callable, Optional

import customtkinter as ctk

logger = logging.getLogger(__name__)


# =============================================================================
# HELPER FUNCTIONS (shared between tabs)
# =============================================================================

def format_top_words(top_words: list, max_display: int = 20) -> str:
    """Format top words for display with alignment.

    Args:
        top_words: List of (word, count) tuples
        max_display: Maximum words to display

    Returns:
        Formatted string with bars and alignment
    """
    if not top_words:
        return "Sin datos"

    max_count = top_words[0][1] if top_words else 1
    max_word_len = max(len(word) for word, _ in top_words) if top_words else 10
    text_width = max(12, max_word_len + 2)

    lines = [f"Top {len(top_words)} palabras:", "=" * (text_width + 8)]

    for i, (word, count) in enumerate(top_words[:max_display], 1):
        bar = "█" * min(int(count / max_count * 20), 20)
        lines.append(f"{i:2}. {word:<{text_width}} {count:>4} {bar}")

    return "\n".join(lines)


def show_error_in_frame(frame: ctk.CTkFrame, message: str) -> None:
    """Show error message in a frame.

    Args:
        frame: CTkFrame to place the error label
        message: Error message to display
    """
    label = ctk.CTkLabel(
        frame,
        text=message,
        text_color="red",
        font=ctk.CTkFont(size=12)
    )
    label.pack(padx=10, pady=10)