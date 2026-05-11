"""N-grams tab for Text Analyzer UI."""
from __future__ import annotations

from typing import TYPE_CHECKING

import customtkinter as ctk
import tkinter as tk

from tools.text_tool.ui.tabs.base_tab import BaseTab

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks


class NgramsTab(BaseTab):
    """Tab displaying n-gram analysis."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        state: TextAnalyzerState,
        callbacks: AppCallbacks,
    ) -> None:
        """Initialize NgramsTab."""
        self._ngram_text: ctk.CTkTextbox | None = None
        self._ngram_size: ctk.IntVar = ctk.IntVar(value=2)
        self._slider: ctk.CTkSlider | None = None
        self._slider_label: ctk.CTkLabel | None = None
        super().__init__(parent, state, callbacks)

    def _setup_frame(self) -> None:
        """Create the main frame for this tab."""
        self._frame = ctk.CTkFrame(self._parent, fg_color="transparent")
        self._build_ui()

    def _build_ui(self) -> None:
        """Build the tab UI."""
        container = ctk.CTkFrame(self._frame, fg_color="transparent")
        container.pack(fill="both", expand=True)

        container.grid_rowconfigure(2, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self._build_size_selector(container)
        self._build_slider(container)
        self._build_results_area(container)

    def _build_size_selector(self, container: ctk.CTkFrame) -> None:
        """Build the n-gram size selector."""
        opts = ctk.CTkFrame(container)
        opts.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        ctk.CTkLabel(opts, text="N-gram size:").pack(side="left", padx=10)

        self._ngram_size = ctk.IntVar(value=2)
        self._ngram_size.trace_add("write", self._on_ngram_size_change)

        for n in [2, 3]:
            ctk.CTkRadioButton(
                opts,
                text=f"{n}-grams",
                variable=self._ngram_size,
                value=n,
            ).pack(side="left", padx=10)

    def _build_slider(self, container: ctk.CTkFrame) -> None:
        """Build the top_k slider."""
        slider_frame = ctk.CTkFrame(container, fg_color="transparent")
        slider_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 0))

        ctk.CTkLabel(
            slider_frame,
            text="Top resultados:",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(side="left", padx=10)

        self._slider = ctk.CTkSlider(
            slider_frame,
            from_=20,
            to=100,
            number_of_steps=80,
            command=self._on_slider_change,
        )
        self._slider.set(15)
        self._slider.pack(side="left", fill="x", expand=True, padx=10)

        self._slider_label = ctk.CTkLabel(
            slider_frame, text="15 resultados", font=ctk.CTkFont(size=12)
        )
        self._slider_label.pack(side="left", padx=10)

    def _build_results_area(self, container: ctk.CTkFrame) -> None:
        """Build the results text area."""
        self._ngram_text = ctk.CTkTextbox(
            container,
            font=("Courier New", 14),
            height=345,
        )
        self._ngram_text.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))

    def get_frame(self) -> ctk.CTkFrame:
        """Return the main frame for this tab."""
        return self._frame

    def refresh(self) -> None:
        """Update n-grams display when text changes."""
        if not self.state.cleaned_content:
            self._ngram_text.delete("1.0", tk.END)
            self._ngram_text.insert("1.0", "🔗 N-grams aparecerá aquí\nEjecute análisis primero")
            return
        self._refresh_display()

    def _on_slider_change(self, value: float) -> None:
        """Handle slider value change."""
        top_k = int(value)
        self._slider_label.configure(text=f"{top_k} resultados")
        self._refresh_display(top_k)

    def _on_ngram_size_change(self, *args) -> None:
        """Handle n-gram size change."""
        self._refresh_display()

    def _refresh_display(self, top_k: int | None = None) -> None:
        """Update n-grams display."""
        if top_k is None:
            top_k = int(self._slider.get())

        if not self.state.cleaned_content:
            return

        try:
            from tools.text_tool.processor import analyze_ngrams

            n = self._ngram_size.get()
            result = analyze_ngrams(self.state.cleaned_content, n=n, top_k=top_k)
            if result.get("success"):
                self._display_ngrams(result["ngrams"], top_k, n)
            else:
                self.update_status(result.get("error", "Error"), "orange")
        except Exception as e:
            self.update_status(f"Error: {e}", "red")

    def _display_ngrams(self, ngrams: dict, top_k: int, n: int) -> None:
        """Display n-gram results."""
        self._ngram_text.delete("1.0", tk.END)

        actual_count = len(ngrams)
        if actual_count < top_k:
            self._slider_label.configure(text=f"{actual_count} resultados (máx disponible)")
        else:
            self._slider_label.configure(text=f"{top_k} resultados")

        max_ng_len = max(len(ng) for ng in ngrams) if ngrams else 10
        text_width = max(25, max_ng_len + 2)

        texto = f"🔗 N-grams ({n})\n"
        texto += "=" * (text_width + 8) + "\n"
        texto += f"{'#':>3} {'N-gram':<{text_width}} {'Count':>4}\n"
        texto += "-" * (text_width + 8) + "\n"

        for i, (ng, count) in enumerate(ngrams.items(), 1):
            texto += f"{i:>3}. {ng:<{text_width}} {count:>4}\n"

        self._ngram_text.insert("1.0", texto)