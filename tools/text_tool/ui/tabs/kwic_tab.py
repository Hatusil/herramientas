"""KWIC (Keyword In Context) tab for Text Analyzer UI."""
from __future__ import annotations

from typing import TYPE_CHECKING

import customtkinter as ctk
import tkinter as tk

from tools.text_tool.ui.tabs.base_tab import BaseTab

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks


class KwicTab(BaseTab):
    """Tab for keyword-in-context concordance search."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        state: TextAnalyzerState,
        callbacks: AppCallbacks,
    ) -> None:
        """Initialize KwicTab."""
        self._keyword_entry: ctk.CTkEntry | None = None
        self._context_slider: ctk.CTkSlider | None = None
        self._context_label: ctk.CTkLabel | None = None
        self._results_slider: ctk.CTkSlider | None = None
        self._results_label: ctk.CTkLabel | None = None
        self._results_text: ctk.CTkTextbox | None = None
        super().__init__(parent, state, callbacks)

    def _setup_frame(self) -> None:
        """Create the main frame for this tab."""
        self._frame = ctk.CTkFrame(self._parent, fg_color="transparent")

        container = ctk.CTkFrame(self._frame, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(2, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Search controls
        self._add_search_controls(container)
        # Results label
        ctk.CTkLabel(
            container, text="Resultados:", font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=1, column=0, sticky="w", padx=10, pady=(10, 5))
        # Results text
        self._results_text = ctk.CTkTextbox(
            container, font=("Courier New", 12), height=180
        )
        self._results_text.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))

    def _add_search_controls(self, container: ctk.CTkFrame) -> None:
        """Add search control widgets."""
        search_frame = ctk.CTkFrame(container, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(
            search_frame,
            text="Buscar palabra clave en contexto:",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w", padx=5, pady=(5, 10))

        # Keyword input
        keyword_row = ctk.CTkFrame(search_frame)
        keyword_row.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(keyword_row, text="Palabra:", width=80, anchor="w").pack(side="left", padx=5)

        self._keyword_entry = ctk.CTkEntry(keyword_row, placeholder_text="palabra a buscar...")
        self._keyword_entry.pack(side="left", fill="x", expand=True, padx=5)
        self._keyword_entry.bind("<Return>", lambda e: self._run_search())

        # Context window slider
        self._add_context_slider(search_frame)
        # Max results slider
        self._add_results_slider(search_frame)
        # Search button
        search_btn = ctk.CTkButton(
            search_frame,
            text="🔍 Buscar",
            command=self._run_search,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        search_btn.pack(pady=10)

    def _add_context_slider(self, parent: ctk.CTkFrame) -> None:
        """Add context window slider."""
        row = ctk.CTkFrame(parent)
        row.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(row, text="Contexto (±palabras):", width=120, anchor="w").pack(side="left", padx=5)

        self._context_slider = ctk.CTkSlider(
            row, from_=1, to=15, number_of_steps=14, command=self._on_context_change
        )
        self._context_slider.set(5)
        self._context_slider.pack(side="left", fill="x", expand=True, padx=5)

        self._context_label = ctk.CTkLabel(row, text="5", width=30)
        self._context_label.pack(side="left", padx=5)

    def _add_results_slider(self, parent: ctk.CTkFrame) -> None:
        """Add max results slider."""
        row = ctk.CTkFrame(parent)
        row.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(row, text="Máx resultados:", width=120, anchor="w").pack(side="left", padx=5)

        self._results_slider = ctk.CTkSlider(
            row, from_=5, to=50, number_of_steps=45, command=self._on_results_change
        )
        self._results_slider.set(20)
        self._results_slider.pack(side="left", fill="x", expand=True, padx=5)

        self._results_label = ctk.CTkLabel(row, text="20", width=30)
        self._results_label.pack(side="left", padx=5)

    def get_frame(self) -> ctk.CTkFrame:
        """Return the main frame for this tab."""
        return self._frame

    def _on_context_change(self, value: float) -> None:
        """Handle context slider change."""
        n = int(value)
        self._context_label.configure(text=str(n))

    def _on_results_change(self, value: float) -> None:
        """Handle results slider change."""
        n = int(value)
        self._results_label.configure(text=str(n))

    def _run_search(self) -> None:
        """Run KWIC concordance search."""
        if not self.state.text_content:
            self.update_status("No hay texto cargado", "orange")
            return

        keyword = self._keyword_entry.get().strip() if self._keyword_entry else ""
        if not keyword:
            self.update_status("Ingrese una palabra clave", "orange")
            return

        context = int(self._context_slider.get()) if self._context_slider else 5
        max_results = int(self._results_slider.get()) if self._results_slider else 20

        try:
            from tools.text_tool.processor import analyze_kwic

            result = analyze_kwic(
                self.state.text_content, keyword, context=context, max_results=max_results
            )

            if result.get("success"):
                self._show_results(result.get("data", []), keyword)
                count = len(result.get("data", []))
                if count > 0:
                    self.update_status(f"{count} ocurrencias encontradas", "green")
                else:
                    self.update_status("No se encontraron ocurrencias", "orange")
            else:
                self.update_status(result.get("error", "Error"), "red")
        except Exception as e:
            self.update_status(f"Error: {e}", "red")

    def _show_results(self, concordances: list, keyword: str) -> None:
        """Display concordance results."""
        self._results_text.delete("1.0", tk.END)

        if not concordances:
            self._results_text.insert("1.0", "No se encontraron ocurrencias")
            return

        texto = f"🔍 Contextos para '{keyword}'\n"
        texto += "=" * 70 + "\n\n"

        max_before = max(len(c.get("before", "")) for c in concordances) if concordances else 20
        max_after = max(len(c.get("after", "")) for c in concordances) if concordances else 20

        before_width = min(max_before, 40)
        after_width = min(max_after, 40)

        for i, conc in enumerate(concordances, 1):
            before = conc.get("before", "")[:before_width]
            keyword_disp = conc.get("keyword", "")
            after = conc.get("after", "")[:after_width]
            texto += f"{i:>3}. {before:<{before_width}} | {keyword_disp} | {after}\n"

        self._results_text.insert("1.0", texto)
