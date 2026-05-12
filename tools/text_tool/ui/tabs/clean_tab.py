"""Clean tab for Text Analyzer UI."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import customtkinter as ctk
import tkinter as tk
from collections import Counter

from tools.text_tool.ui.tabs.base_tab import BaseTab

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks

logger = logging.getLogger(__name__)


class CleanTab(BaseTab):
    """Tab for text cleaning options and preview."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        state: TextAnalyzerState,
        callbacks: AppCallbacks,
    ) -> None:
        """Initialize CleanTab."""
        self._sources_summary: ctk.CTkLabel | None = None
        self._remove_stopwords: ctk.BooleanVar = ctk.BooleanVar(value=True)
        self._exclude_entry: ctk.CTkEntry | None = None
        self._preview_raw_btn: ctk.CTkButton | None = None
        self._apply_clean_btn: ctk.CTkButton | None = None
        self._clean_text: ctk.CTkTextbox | None = None
        self._clean_freq_text: ctk.CTkTextbox | None = None
        super().__init__(parent, state, callbacks)

    def _setup_frame(self) -> None:
        """Create the main frame for this tab."""
        self._frame = ctk.CTkFrame(self._parent, fg_color="transparent")
        self._build_ui()

    def _build_ui(self) -> None:
        """Build the tab UI."""
        self._build_sources_section()
        self._build_clean_options()
        self._build_action_buttons()
        self._build_generate_button()
        self._build_results_section()

    def _build_sources_section(self) -> None:
        """Build the sources summary section."""
        self._sources_summary = ctk.CTkLabel(
            self._frame,
            text="📁 Sin contenido cargado",
            font=ctk.CTkFont(size=14),
        )
        self._sources_summary.pack(anchor="w", padx=10, pady=(10, 5))

        remove_frame = ctk.CTkFrame(self._frame)
        remove_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            remove_frame,
            text="❌ Quitar Textos",
            command=lambda: self._remove_source("text"),
            fg_color="#c44",
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            remove_frame,
            text="❌ Quitar Archivos",
            command=lambda: self._remove_source("files"),
            fg_color="#c44",
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            remove_frame,
            text="❌ Quitar URLs",
            command=lambda: self._remove_source("urls"),
            fg_color="#c44",
        ).pack(side="left", padx=2)

    def _build_clean_options(self) -> None:
        """Build the cleaning options section."""
        opts_section = ctk.CTkLabel(
            self._frame,
            text="⚙️ OPCIONES DE LIMPIEZA",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        opts_section.pack(anchor="w", padx=10, pady=(15, 5))

        opts_frame = ctk.CTkFrame(self._frame)
        opts_frame.pack(fill="x", padx=10, pady=5)

        self._remove_stopwords = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            opts_frame,
            text="Quitar conectores (stopwords)",
            variable=self._remove_stopwords,
        ).pack(anchor="w", padx=5, pady=3)

        ctk.CTkLabel(
            opts_frame, text="Excluir palabras (separadas por coma):"
        ).pack(anchor="w", padx=5, pady=(5, 0))

        self._exclude_entry = ctk.CTkEntry(
            opts_frame, placeholder_text="ej: palabra1, palabra2, palabra3"
        )
        self._exclude_entry.pack(fill="x", padx=5, pady=5)

    def _build_action_buttons(self) -> None:
        """Build the action buttons."""
        action_frame = ctk.CTkFrame(self._frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=10)

        self._preview_raw_btn = ctk.CTkButton(
            action_frame,
            text="👁 Preview Texto Bruto",
            command=self._preview_raw_text,
            width=180,
            fg_color="#888",
            hover_color="#666",
        )
        self._preview_raw_btn.pack(side="left", padx=5)

        self._apply_clean_btn = ctk.CTkButton(
            action_frame,
            text="🔄 Aplicar Limpieza",
            command=self._apply_clean,
            width=180,
            fg_color="#48a",
            hover_color="#386",
        )
        self._apply_clean_btn.pack(side="left", padx=5)

    def _build_results_section(self) -> None:
        """Build the results display section."""
        results_section = ctk.CTkLabel(
            self._frame,
            text="✅ RESULTADOS",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        results_section.pack(anchor="w", padx=10, pady=(15, 5))

        clean_label = ctk.CTkLabel(
            self._frame, text="Texto limpio (preview):", font=ctk.CTkFont(size=12)
        )
        clean_label.pack(anchor="w", padx=10, pady=(5, 0))

        self._clean_text = ctk.CTkTextbox(self._frame, wrap="word", height=150)
        self._clean_text.pack(fill="both", expand=False, padx=10, pady=5)

        top_words_label = ctk.CTkLabel(
            self._frame, text="Top 20 palabras:", font=ctk.CTkFont(size=12)
        )
        top_words_label.pack(anchor="w", padx=10, pady=(10, 0))

        self._clean_freq_text = ctk.CTkTextbox(
            self._frame, wrap="word", font=("Courier New", 11)
        )
        self._clean_freq_text.pack(fill="both", expand=True, padx=10, pady=5)

    def _build_generate_button(self) -> None:
        """Build the main generate button."""
        ctk.CTkButton(
            self._frame,
            text="📊 GENERAR VISUALIZACIONES Y ANÁLISIS",
            command=self._run_all_analysis,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#e62",
            hover_color="#c50",
        ).pack(fill="x", padx=10, pady=(20, 10))

    def get_frame(self) -> ctk.CTkFrame:
        """Return the main frame for this tab."""
        return self._frame

    def refresh(self) -> None:
        """Refresh the clean tab state."""
        self._update_sources_summary()

    def _update_sources_summary(self) -> None:
        """Update the sources summary label."""
        if self._sources_summary:
            self._sources_summary.configure(text=self.state.sources_summary)

    def _remove_source(self, source_type: str) -> None:
        """Remove a source type and reset content."""
        if not self.state.text_content and not self.state.sources[source_type]:
            return

        self.state.text_content = ""
        self.state.update_cleaned(None)
        self._clean_text.delete("1.0", tk.END)
        self._clean_freq_text.delete("1.0", tk.END)
        self.state.sources = {"text": [], "files": [], "urls": []}
        self._update_sources_summary()
        self.update_status("Contenido reseteado", "gray")

    def _preview_raw_text(self) -> None:
        """Show preview of raw text (no filters)."""
        if not self.state.text_content:
            self.update_status("Primero cargá texto", "orange")
            return

        self._clean_text.delete("1.0", tk.END)
        self._clean_text.insert("1.0", self.state.text_content[:2000])

        words = self.state.text_content.lower().split()
        word_freq = Counter(words)
        top_20 = word_freq.most_common(20)

        self._update_freq_display(top_20, "texto bruto (sin filtros)")
        self._preview_raw_btn.configure(fg_color="#4a4", hover_color="#383")
        self._apply_clean_btn.configure(fg_color="#48a", hover_color="#386")
        self.update_status("Preview: texto en bruto (sin filtros)", "green")

    def _apply_clean(self) -> None:
        """Apply cleaning and show preview."""
        if not self.state.text_content:
            self.update_status("Primero cargá texto", "orange")
            return

        try:
            from core.utils import clean_text

            exclude_text = self._exclude_entry.get().strip()
            exclude_words = (
                [w.strip().lower() for w in exclude_text.split(",")]
                if exclude_text
                else []
            )

            cleaned = clean_text(
                self.state.text_content,
                remove_stopwords=self._remove_stopwords.get(),
                exclude_words=exclude_words,
            )

            self._clean_text.delete("1.0", tk.END)
            self._clean_text.insert("1.0", cleaned[:2000])

            words = cleaned.lower().split()
            word_freq = Counter(words)
            top_20 = word_freq.most_common(20)

            self._update_freq_display(top_20, "limpio")
            self.state.update_cleaned(cleaned)

            self._preview_raw_btn.configure(fg_color="#888", hover_color="#666")
            self._apply_clean_btn.configure(fg_color="#4a4", hover_color="#383")
            self.update_status(
                f"Limpieza aplicada: {len(cleaned.split())} palabras", "green"
            )
            self.state.last_analysis = "limpieza"
        except Exception as e:
            self.update_status(f"Error: {e}", "red")

    def _update_freq_display(self, top_20: list, label: str) -> None:
        """Update the frequency display with top words."""
        if not top_20:
            self._clean_freq_text.delete("1.0", tk.END)
            self._clean_freq_text.insert("1.0", "Sin palabras")
            return

        max_count = top_20[0][1] if top_20 else 1
        max_word_len = max(len(word) for word, _ in top_20) if top_20 else 10
        text_width = max(15, max_word_len + 2)

        texto = f"📊 Top 20 palabras ({label}):\n"
        texto += "=" * (text_width + 10) + "\n\n"

        for i, (word, count) in enumerate(top_20, 1):
            bar = "█" * min(int(count / max_count * 20), 20)
            texto += f"{i:2}. {word:<{text_width}} {count:>4} {bar}\n"

        self._clean_freq_text.delete("1.0", tk.END)
        self._clean_freq_text.insert("1.0", texto)

    def _run_all_analysis(self) -> None:
        """Request full analysis of cleaned text."""
        if not self.state.has_text:
            self.update_status("Primero cargá texto", "orange")
            return

        self.callbacks.request_analysis("full_analysis", None)