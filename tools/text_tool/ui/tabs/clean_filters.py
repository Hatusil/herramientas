"""Clean tab - Filter options section."""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import customtkinter as ctk

from core.constants import COLORS
from tools.text_tool.ui.phases.clean_phase import CleanPhase

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState


def build_stats_section(parent: ctk.CTkFrame) -> tuple[ctk.CTkLabel, ctk.CTkLabel]:
    """Build filter statistics section. Returns (stats_label, filter_info_label)."""
    stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
    stats_frame.pack(fill="x", padx=10, pady=5)

    stats_label = ctk.CTkLabel(
        stats_frame,
        text="",
        font=ctk.CTkFont(size=12),
        text_color=COLORS["text_secondary"],
    )
    stats_label.pack(anchor="w")

    filter_info = ctk.CTkLabel(
        stats_frame,
        text="",
        font=ctk.CTkFont(size=11),
        text_color=COLORS["text_muted"],
    )
    filter_info.pack(anchor="w", pady=(2, 0))

    return stats_label, filter_info


def build_clean_options(
    parent: ctk.CTkFrame,
    state: TextAnalyzerState,
    on_filter_change: Callable[[], None],
    apply_filters_fn: Callable[[], None],
) -> tuple[ctk.BooleanVar, ctk.CTkEntry, ctk.CTkButton]:
    """Build the cleaning options section.

    Includes filter controls only (stats + execute button are separate).
    Returns (remove_stopwords_var, exclude_entry, apply_btn).
    """
    opts_section = ctk.CTkLabel(
        parent,
        text="\u2699\ufe0f FILTROS",
        font=ctk.CTkFont(size=14, weight="bold"),
    )
    opts_section.pack(anchor="w", padx=10, pady=(10, 5))

    opts_frame = ctk.CTkFrame(parent)
    opts_frame.pack(fill="x", padx=10, pady=5)

    remove_stopwords_var = ctk.BooleanVar(value=True)
    ctk.CTkCheckBox(
        opts_frame,
        text="Quitar conectores (stopwords)",
        variable=remove_stopwords_var,
        command=on_filter_change,
    ).pack(anchor="w", padx=5, pady=3)

    ctk.CTkLabel(
        opts_frame, text="Excluir palabras (separadas por coma):"
    ).pack(anchor="w", padx=5, pady=(5, 0))

    exclude_entry = ctk.CTkEntry(
        opts_frame, placeholder_text="ej: palabra1, palabra2, palabra3"
    )
    exclude_entry.pack(fill="x", padx=5, pady=5)
    exclude_entry.bind("<KeyRelease>", lambda e: on_filter_change())

    apply_btn = ctk.CTkButton(
        opts_frame,
        text="\U0001f504 Aplicar Filtros",
        command=apply_filters_fn,
        fg_color=COLORS["primary"],
    )
    apply_btn.pack(fill="x", padx=5, pady=5)

    return remove_stopwords_var, exclude_entry, apply_btn


def update_filter_stats(
    stats_label: ctk.CTkLabel | None,
    filter_info: ctk.CTkLabel | None,
    state: TextAnalyzerState,
) -> None:
    """Update filter statistics display."""
    if not stats_label:
        return

    pipeline = state.filter_pipeline
    raw_count = len(pipeline.raw_words)
    filtered_count = len(pipeline.filtered_words)

    stats_label.configure(
        text=f"Palabras: {filtered_count}/{raw_count} (filtro activo) | "
        f"Caracteres: {len(pipeline.raw_text)}"
    )

    filters_text = (
        ", ".join(pipeline.applied_filters) if pipeline.applied_filters else "ninguno"
    )
    if filter_info:
        filter_info.configure(text=f"Filtros aplicados: {filters_text}")


def update_execute_button_state(
    execute_btn: ctk.CTkButton | None,
    state: TextAnalyzerState,
) -> None:
    """Update execute button enabled/disabled based on phase."""
    if not execute_btn:
        return

    current_phase = state.current_phase
    if current_phase in (CleanPhase.PREVIEW, CleanPhase.EXECUTE):
        execute_btn.configure(state="normal")
    else:
        execute_btn.configure(state="disabled")
