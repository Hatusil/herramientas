"""Frequency tab for Text Analyzer UI."""
from __future__ import annotations

from typing import TYPE_CHECKING

import customtkinter as ctk
import tkinter as tk

from tools.text_tool.ui.tabs.base_tab import BaseTab

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks


class FreqTab(BaseTab):
    """Tab displaying word frequency analysis."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        state: TextAnalyzerState,
        callbacks: AppCallbacks,
    ) -> None:
        """Initialize FreqTab."""
        self._freq_text: ctk.CTkTextbox | None = None
        self._slider: ctk.CTkSlider | None = None
        self._slider_label: ctk.CTkLabel | None = None
        super().__init__(parent, state, callbacks)

    def _setup_frame(self) -> None:
        """Create the main frame for this tab."""
        self._frame = ctk.CTkFrame(self._parent, fg_color="transparent")

        # Container for full tab
        container = ctk.CTkFrame(self._frame, fg_color="transparent")
        container.pack(fill="both", expand=True)

        # Slider frame at top
        slider_frame = ctk.CTkFrame(container, fg_color="transparent")
        slider_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            slider_frame, text="Palabras a mostrar:", font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=10)

        # Slider for word count (20-100, default 20)
        self._slider = ctk.CTkSlider(
            slider_frame,
            from_=20,
            to=100,
            number_of_steps=80,
            command=self._on_slider_change,
        )
        self._slider.set(20)
        self._slider.pack(side="left", fill="x", expand=True, padx=10)

        # Label showing current value
        self._slider_label = ctk.CTkLabel(slider_frame, text="20 palabras", font=ctk.CTkFont(size=12))
        self._slider_label.pack(side="left", padx=10)

        # Text view for results
        self._freq_text = ctk.CTkTextbox(
            container,
            font=("Courier New", 14),
            wrap="word",
            height=397,
        )
        self._freq_text.pack(fill="both", expand=True, padx=10, pady=(5, 10))

    def get_frame(self) -> ctk.CTkFrame:
        """Return the main frame for this tab."""
        return self._frame

    def _on_slider_change(self, value: float) -> None:
        """Handle slider value change."""
        n = int(value)
        self._slider_label.configure(text=f"{n} palabras")
        self._refresh_display(n)

    def refresh(self) -> None:
        """Update frequency display when text changes."""
        if not self.state.cleaned_content:
            self._freq_text.delete("1.0", tk.END)
            self._freq_text.insert("1.0", "📈 Frecuencia aparecerá aquí\nEjecute análisis primero")
            return
        self._refresh_display()

    def _refresh_display(self, n: int | None = None) -> None:
        """Update frequency display with specified n value."""
        if n is None:
            n = int(self._slider.get())

        if not self.state.cleaned_content:
            return

        try:
            from tools.text_tool.processor import analyze_frequency

            result = analyze_frequency(self.state.cleaned_content, n=n, already_cleaned=True)
            if result.get("success"):
                self._display_frequencies(result["frequencies"], n)
        except Exception as e:
            self.update_status(f"Error: {e}", "red")

    def _display_frequencies(self, frequencies: dict, n: int | None = None) -> None:
        """Display frequency results."""
        self._freq_text.delete("1.0", tk.END)

        actual_count = len(frequencies)
        slider_n = n if n is not None else int(self._slider.get())

        # Update label to show actual count
        if actual_count < slider_n:
            self._slider_label.configure(text=f"{actual_count} palabras (máx disponible)")
        else:
            self._slider_label.configure(text=f"{slider_n} palabras")

        # Calculate max word length for alignment
        max_word_len = max(len(word) for word in frequencies) if frequencies else 10
        text_width = max(20, max_word_len + 2)

        # Header with aligned columns
        texto = "📈 Palabras más frecuentes\n"
        texto += "=" * (text_width + 10) + "\n"
        texto += f"{'#':>3} {'Palabra':<{text_width}} {'Count':>5}\n"
        texto += "-" * (text_width + 10) + "\n"

        for i, (word, count) in enumerate(frequencies.items(), 1):
            texto += f"{i:>3}. {word:<{text_width}} {count:>5}\n"

        self._freq_text.insert("1.0", texto)