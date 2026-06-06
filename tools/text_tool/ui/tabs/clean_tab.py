"""Clean tab for Text Analyzer UI."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import customtkinter as ctk

from tools.text_tool.ui.tabs.base_tab import BaseTab
from tools.text_tool.ui.phases.clean_phase import CleanPhase
from core.constants import COLORS

from .clean_sources import (
    build_sources_section,
    update_sources_display,
    remove_source,
)
from .clean_filters import (
    build_stats_section,
    build_clean_options,
    update_filter_stats,
    update_execute_button_state,
)
from .clean_results import (
    build_action_buttons,
    build_results_section,
    build_execute_button,
    show_raw_text,
    show_filtered_text,
    update_freq_display,
)

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks

logger = logging.getLogger(__name__)


class CleanTab(BaseTab):
    """Tab for text cleaning options and preview with progressive filters."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        state: TextAnalyzerState,
        callbacks: AppCallbacks,
    ) -> None:
        """Initialize CleanTab."""
        self._exclude_entry: ctk.CTkEntry | None = None
        self._remove_stopwords: ctk.BooleanVar | None = None
        self._preview_raw_btn: ctk.CTkButton | None = None
        self._apply_clean_btn: ctk.CTkButton | None = None
        self._execute_btn: ctk.CTkButton | None = None
        self._clean_text: ctk.CTkTextbox | None = None
        self._clean_freq_text: ctk.CTkTextbox | None = None
        self._sources_frame: ctk.CTkFrame | None = None
        self._stats_label: ctk.CTkLabel | None = None
        self._filter_info: ctk.CTkLabel | None = None
        self._update_fn: callable | None = None
        super().__init__(parent, state, callbacks)

    def _setup_frame(self) -> None:
        """Create the main frame for this tab."""
        self._frame = ctk.CTkFrame(self._parent, fg_color="transparent")
        self._build_ui()

    def _build_ui(self) -> None:
        """Build the tab UI using imported submodule builders."""

        def _refresh_all() -> None:
            """Coordinator: updates sources, stats, filters, and execute button."""
            update_sources_display(
                self._sources_frame,
                self.state,
                self.callbacks,
                remove_fn=self._remove_source,
            )
            update_filter_stats(self._stats_label, self._filter_info, self.state)
            self._apply_filters()
            update_execute_button_state(self._execute_btn, self.state)

        self._update_fn = _refresh_all

        self._sources_frame = build_sources_section(self._frame)

        self._stats_label, self._filter_info = build_stats_section(self._frame)

        self._remove_stopwords, self._exclude_entry, _apply_btn = build_clean_options(
            self._frame,
            self.state,
            on_filter_change=self._on_filter_change,
            apply_filters_fn=self._apply_filters,
        )

        self._preview_raw_btn, self._apply_clean_btn = build_action_buttons(
            self._frame,
            show_raw_fn=self._show_raw_text,
            show_filtered_fn=self._show_filtered_text,
        )

        self._clean_text, self._clean_freq_text = build_results_section(self._frame)

        self._execute_btn = build_execute_button(self._frame, self._run_all_analysis)

    def get_frame(self) -> ctk.CTkFrame:
        """Return the main frame for this tab."""
        return self._frame

    def refresh(self) -> None:
        """Refresh the clean tab state via coordinator."""
        if self._update_fn:
            self._update_fn()

    def _remove_source(self, source_type: str, source_id: str) -> None:
        """Remove a specific source."""
        remove_source(
            source_type,
            source_id,
            self.state,
            self.callbacks,
            self._clean_text,
            self._clean_freq_text,
            self._stats_label,
            self._filter_info,
            self._update_fn,
        )

    def _on_filter_change(self) -> None:
        """Handle filter checkbox change."""
        if self._remove_stopwords is not None:
            self.state.remove_stopwords = self._remove_stopwords.get()
        exclusions = self._exclude_entry.get().strip() if self._exclude_entry else ""
        self.state.set_exclusions(exclusions)
        self._apply_filters()

    def _apply_filters(self) -> None:
        """Apply current filters and update display."""
        if not self.state.has_text:
            self.update_status("Primero carg\u00e1 contenido", "orange")
            return

        self.state.apply_stopwords_filter(
            self._remove_stopwords.get() if self._remove_stopwords else True,
        )
        if self._exclude_entry:
            self.state.set_exclusions(self._exclude_entry.get().strip())

        update_filter_stats(self._stats_label, self._filter_info, self.state)

        self._show_filtered_text()

        self.state.transition_to_phase(CleanPhase.EXECUTE)
        update_execute_button_state(self._execute_btn, self.state)

        self.update_status(
            f"Filtros aplicados: {len(self.state.filter_pipeline.filtered_words)}"
            f" palabras - Listo para ejecutar",
            "green",
        )

    def _show_raw_text(self) -> None:
        """Show raw (unfiltered) text."""
        if not self.state.has_text:
            self.update_status("Primero carg\u00e1 contenido", "orange")
            return

        show_raw_text(
            self._clean_text,
            self._clean_freq_text,
            self.state,
            self.callbacks,
            self._preview_raw_btn,
            self._apply_clean_btn,
            lambda: update_execute_button_state(self._execute_btn, self.state),
        )
        self.state.transition_to_phase(CleanPhase.PREVIEW)
        self.update_status(
            f"Texto bruto: {len(self.state.filter_pipeline.raw_words)} palabras",
            "blue",
        )

    def _show_filtered_text(self) -> None:
        """Show filtered text."""
        if not self.state.has_text:
            self.update_status("Primero carg\u00e1 contenido", "orange")
            return

        show_filtered_text(
            self._clean_text,
            self._clean_freq_text,
            self.state,
            self.callbacks,
            self._preview_raw_btn,
            self._apply_clean_btn,
            lambda: update_execute_button_state(self._execute_btn, self.state),
        )
        self.state.transition_to_phase(CleanPhase.PREVIEW)
        self.update_status(
            f"Texto filtrado: {len(self.state.filter_pipeline.filtered_words)}"
            f" palabras",
            "green",
        )

    def _run_all_analysis(self) -> None:
        """Request full analysis of cleaned text."""
        if not self.state.has_text:
            self.update_status("Primero carg\u00e1 texto", "orange")
            return

        self.state.clear_analysis()

        self.state.transition_to_phase(CleanPhase.EXECUTE)

        self.callbacks.request_analysis("full_analysis", None)
