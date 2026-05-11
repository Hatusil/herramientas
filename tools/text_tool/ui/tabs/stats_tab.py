"""Stats tab for Text Analyzer UI."""
from __future__ import annotations

from typing import TYPE_CHECKING

import customtkinter as ctk
import tkinter as tk

from tools.text_tool.ui.tabs.base_tab import BaseTab

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks


class StatsTab(BaseTab):
    """Tab displaying statistical metrics about the text."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        state: TextAnalyzerState,
        callbacks: AppCallbacks,
    ) -> None:
        """Initialize StatsTab."""
        self._stats_text: ctk.CTkTextbox | None = None
        super().__init__(parent, state, callbacks)

    def _setup_frame(self) -> None:
        """Create the main frame for this tab."""
        self._frame = ctk.CTkFrame(self._parent, fg_color="transparent")

        # Container for grid layout
        container = ctk.CTkFrame(self._frame, fg_color="transparent")
        container.pack(fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Stats text display
        self._stats_text = ctk.CTkTextbox(
            container, font=("Courier New", 15), height=270
        )
        self._stats_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def get_frame(self) -> ctk.CTkFrame:
        """Return the main frame for this tab."""
        return self._frame

    def refresh(self) -> None:
        """Update statistics when text changes."""
        if not self.state.cleaned_content:
            self._stats_text.delete("1.0", tk.END)
            self._stats_text.insert("1.0", "📉 Estadísticas aparecerán aquí\nEjecute análisis primero")
            return

        try:
            from tools.text_tool.processor import analyze_stats
            result = analyze_stats(self.state.cleaned_content)
            if result.get("success"):
                self._display_stats(result)
        except Exception as e:
            self.update_status(f"Error: {e}", "red")

    def _display_stats(self, stats: dict) -> None:
        """Display statistics in the text box."""
        self._stats_text.delete("1.0", tk.END)

        label_width = 25

        texto = "📉 Estadísticas del Texto\n"
        texto += "=" * (label_width + 12) + "\n"
        texto += f"{'Métrica':<{label_width}} {'Valor':>10}\n"
        texto += "-" * (label_width + 12) + "\n"

        texto += f"{'Caracteres totales':<{label_width}} {stats.get('total_chars', 0):>10,}\n"
        texto += f"{'Palabras totales':<{label_width}} {stats.get('total_words', 0):>10,}\n"
        texto += f"{'Palabras únicas':<{label_width}} {stats.get('unique_words', 0):>10,}\n"
        texto += f"{'Oraciones':<{label_width}} {stats.get('total_sentences', 0):>10,}\n"
        texto += "\n"
        texto += f"{'Promedio palabra':<{label_width}} {stats.get('avg_word_length', 0):>10.2f}\n"
        texto += f"{'Promedio oración':<{label_width}} {stats.get('avg_sentence_length', 0):>10.2f}\n"
        texto += f"{'Type-Token Ratio':<{label_width}} {stats.get('type_token_ratio', 0):>10.4f}\n"

        self._stats_text.insert("1.0", texto)