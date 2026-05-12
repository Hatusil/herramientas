"""Topics (LDA) tab for Text Analyzer UI."""
from __future__ import annotations

from typing import TYPE_CHECKING

import customtkinter as ctk
import tkinter as tk

from tools.text_tool.ui.tabs.base_tab import BaseTab

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks


class TopicsTab(BaseTab):
    """Tab for LDA topic modeling analysis."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        state: TextAnalyzerState,
        callbacks: AppCallbacks,
    ) -> None:
        """Initialize TopicsTab."""
        self._count_slider: ctk.CTkSlider | None = None
        self._count_label: ctk.CTkLabel | None = None
        self._results_text: ctk.CTkTextbox | None = None
        super().__init__(parent, state, callbacks)

    def _setup_frame(self) -> None:
        """Create the main frame for this tab."""
        self._frame = ctk.CTkFrame(self._parent, fg_color="transparent")

        container = ctk.CTkFrame(self._frame, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Controls frame
        self._add_controls(container)
        # Results label
        ctk.CTkLabel(
            container, text="Resultados:", font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=1, column=0, sticky="w", padx=10, pady=(10, 5))
        # Results text
        self._results_text = ctk.CTkTextbox(container, font=("Courier New", 12), height=230)
        self._results_text.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))

    def _add_controls(self, container: ctk.CTkFrame) -> None:
        """Add analysis control widgets."""
        controls_frame = ctk.CTkFrame(container, fg_color="transparent")
        controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(
            controls_frame,
            text="Extracción de tópicos usando LDA (Latent Dirichlet Allocation):",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w", padx=5, pady=(5, 10))

        # Topic count slider
        topic_count_row = ctk.CTkFrame(controls_frame)
        topic_count_row.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(topic_count_row, text="Número de temas:", width=120, anchor="w").pack(
            side="left", padx=5
        )

        self._count_slider = ctk.CTkSlider(
            topic_count_row,
            from_=3,
            to=15,
            number_of_steps=12,
            command=self._on_count_change,
        )
        self._count_slider.set(5)
        self._count_slider.pack(side="left", fill="x", expand=True, padx=5)

        self._count_label = ctk.CTkLabel(topic_count_row, text="5", width=30)
        self._count_label.pack(side="left", padx=5)

        # Run button
        analyze_btn = ctk.CTkButton(
            controls_frame,
            text="📚 Analizar Temas",
            command=self._run_analysis,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        analyze_btn.pack(pady=10)

    def get_frame(self) -> ctk.CTkFrame:
        """Return the main frame for this tab."""
        return self._frame

    def _on_count_change(self, value: float) -> None:
        """Handle topic count slider change."""
        n = int(value)
        self._count_label.configure(text=str(n))

    def _run_analysis(self) -> None:
        """Run LDA topic analysis."""
        if not self.state.text_content:
            self.update_status("No hay texto cargado", "orange")
            return

        n_topics = int(self._count_slider.get()) if self._count_slider else 5

        try:
            from tools.text_tool.processor import analyze_topics
            from core.utils import clean_text

            self.update_status("🔄 Analizando temas con LDA...", "blue")
            self._parent.update()

            exclude_text = self.state.exclude_words
            cleaned = clean_text(
                self.state.text_content,
                remove_stopwords=self.state.remove_stopwords,
                exclude_words=exclude_text if exclude_text else None,
            )

            result = analyze_topics(cleaned, n_topics=n_topics, already_cleaned=True)

            if result.get("success"):
                self._show_results(result.get("data", []))
                count = len(result.get("data", []))
                self.update_status(
                    f"Análisis completado: {count} tópicos", "green"
                )
            else:
                self.update_status(result.get("error", "Error"), "red")
        except Exception as e:
            self.update_status(f"Error: {e}", "red")

    def _show_results(self, topics: list) -> None:
        """Display LDA topics results."""
        self._results_text.delete("1.0", tk.END)

        if not topics:
            self._results_text.insert("1.0", "No se pudieron extraer temas del texto.")
            return

        texto = "📚 Temas extraídos con LDA\n"
        texto += "=" * 60 + "\n\n"

        for topic in topics:
            topic_id = topic.get("topic_id", 0)
            words = topic.get("words", [])

            texto += f"--- Tema {topic_id + 1} ---\n"

            if not words:
                texto += "  (Sin palabras)\n"
            else:
                max_weight = max(w.get("weight", 0) for w in words) if words else 1
                max_word_len = (
                    max(len(wd.get("word", "")) for wd in words) if words else 10
                )
                text_width = max(15, max_word_len + 2)

                for word_data in words:
                    word = word_data.get("word", "")
                    weight = word_data.get("weight", 0)
                    normalized = int((weight / max_weight) * 20) if max_weight > 0 else 0
                    bar = "▓" * normalized + "░" * (20 - normalized)
                    texto += f"  {word:<{text_width}} {bar} {weight:.3f}\n"

            texto += "\n"

        self._results_text.insert("1.0", texto)
