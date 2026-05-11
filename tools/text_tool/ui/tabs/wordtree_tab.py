"""WordTree (Árbol de Palabras) tab for Text Analyzer UI."""
from __future__ import annotations

from typing import TYPE_CHECKING

import customtkinter as ctk
import tkinter as tk

from tools.text_tool.ui.tabs.base_tab import BaseTab

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks


class WordTreeTab(BaseTab):
    """Tab for hierarchical word tree visualization."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        state: TextAnalyzerState,
        callbacks: AppCallbacks,
    ) -> None:
        """Initialize WordTreeTab."""
        self._phrase_entry: ctk.CTkEntry | None = None
        self._depth_slider: ctk.CTkSlider | None = None
        self._depth_label: ctk.CTkLabel | None = None
        self._display_label: ctk.CTkLabel | None = None
        self._simple_text: ctk.CTkTextbox | None = None
        self._collapsed: dict = {}
        self._last_result: dict | None = None
        super().__init__(parent, state, callbacks)

    def _setup_frame(self) -> None:
        """Create the main frame for this tab."""
        self._frame = ctk.CTkFrame(self._parent, fg_color="transparent")

        # Controls frame
        controls_frame = ctk.CTkFrame(self._frame)
        controls_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            controls_frame,
            text="Lista de continuaciones simple:",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w", padx=5, pady=(5, 10))

        # Phrase input
        phrase_row = ctk.CTkFrame(controls_frame)
        phrase_row.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(phrase_row, text="Frase raíz:", width=80, anchor="w").pack(
            side="left", padx=5
        )

        self._phrase_entry = ctk.CTkEntry(
            phrase_row, placeholder_text="palabra o frase a buscar..."
        )
        self._phrase_entry.pack(side="left", fill="x", expand=True, padx=5)
        self._phrase_entry.bind("<Return>", lambda e: self._run_analysis())

        # Max results slider
        self._add_depth_slider(controls_frame)

        # Generate button
        generate_btn = ctk.CTkButton(
            controls_frame,
            text="📋 Generar Lista",
            command=self._run_analysis,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        generate_btn.pack(pady=10)

        # Display area
        self._display_label = ctk.CTkLabel(
            self._frame, text="Lista de continuaciones aparecerá aquí", text_color="gray"
        )
        self._display_label.pack(expand=True)

    def _add_depth_slider(self, parent: ctk.CTkFrame) -> None:
        """Add max results slider."""
        depth_row = ctk.CTkFrame(parent)
        depth_row.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(depth_row, text="Máx resultados:", width=120, anchor="w").pack(
            side="left", padx=5
        )

        self._depth_slider = ctk.CTkSlider(
            depth_row,
            from_=2,
            to=5,
            number_of_steps=3,
            command=self._on_depth_change,
        )
        self._depth_slider.set(3)
        self._depth_slider.pack(side="left", fill="x", expand=True, padx=5)

        self._depth_label = ctk.CTkLabel(depth_row, text="3", width=30)
        self._depth_label.pack(side="left", padx=5)

    def get_frame(self) -> ctk.CTkFrame:
        """Return the main frame for this tab."""
        return self._frame

    def _on_depth_change(self, value: float) -> None:
        """Handle depth slider change."""
        n = int(value)
        self._depth_label.configure(text=str(n))

    def _run_analysis(self) -> None:
        """Run WordTree analysis."""
        if not self.state.text_content:
            self.update_status("No hay texto cargado", "orange")
            return

        phrase = self._phrase_entry.get().strip() if self._phrase_entry else ""
        if not phrase:
            self.update_status("Ingrese una frase raíz", "orange")
            return

        max_results = (int(self._depth_slider.get()) if self._depth_slider else 3) * 5

        try:
            from tools.text_tool.processor import analyze_wordtree_simple

            result = analyze_wordtree_simple(self.state.text_content, phrase, max_results=max_results)

            if result.get("success") and result.get("continuations"):
                self._show_simple_list(result)
                total = result.get("total_found", len(result["continuations"]))
                self.update_status(
                    f"Continuaciones para '{phrase}': {total} encontradas", "green"
                )
            elif result.get("success"):
                self.update_status(
                    result.get("error", "No se encontraron continuaciones"), "orange"
                )
            else:
                self.update_status(result.get("error", "Error"), "red")
        except Exception as e:
            self.update_status(f"Error: {e}", "red")

    def _show_simple_list(self, result: dict) -> None:
        """Display results as simple text list."""
        continuations = result.get("continuations", [])
        phrase = result.get("phrase", "")

        if not continuations:
            self._display_label.configure(text="No se encontraron continuaciones")
            return

        if hasattr(self, "_canvas_frame"):
            self._canvas_frame.pack_forget()

        if self._simple_text is None:
            self._simple_text = ctk.CTkTextbox(
                self._frame, wrap="word", font=("Courier New", 12)
            )

        lines = [f"Continuaciones para '{phrase}':\n", "=" * 40 + "\n\n"]
        for item in continuations:
            word = item.get("word", "")
            count = item.get("count", 0)
            lines.append(f"- {word}: {count} ocurrencias\n")

        self._simple_text.delete("1.0", tk.END)
        self._simple_text.insert("1.0", "".join(lines))
        self._simple_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._display_label.pack_forget()

    def refresh(self) -> None:
        """Reset display on tab refresh."""
        pass
