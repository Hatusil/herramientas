"""Clean tab - Sources display section."""
from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING, Callable

import customtkinter as ctk

from core.constants import COLORS
from tools.text_tool.ui.phases.clean_phase import CleanPhase

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks


def build_sources_section(parent: ctk.CTkFrame) -> ctk.CTkFrame:
    """Build the sources display section. Returns the sources frame."""
    header = ctk.CTkLabel(
        parent,
        text="\U0001f4e5 FUENTES DE CONTENIDO",
        font=ctk.CTkFont(size=14, weight="bold"),
    )
    header.pack(anchor="w", padx=10, pady=(10, 5))

    sources_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_medium"])
    sources_frame.pack(fill="x", padx=10, pady=5)
    return sources_frame


def update_sources_display(
    sources_frame: ctk.CTkFrame | None,
    state: TextAnalyzerState,
    callbacks: AppCallbacks,
    remove_fn: Callable[[str, str], None] | None = None,
) -> None:
    """Update sources display.

    Handles Clear + rebuild + transition to CREATE_RAW if sources exist.
    """
    if not sources_frame:
        return

    for widget in sources_frame.winfo_children():
        widget.destroy()

    sources = state.sources

    for src_type, src_list in sources.items():
        if not src_list:
            continue

        for src in src_list:
            src_frame = ctk.CTkFrame(sources_frame, fg_color=COLORS["bg_input"])
            src_frame.pack(fill="x", pady=2, padx=5)

            icon = {"text": "\U0001f4dd", "files": "\U0001f4c4", "urls": "\U0001f310"}.get(
                src_type, "\U0001f4c1"
            )
            if len(src.source_id) > 40:
                label_text = (
                    f"{icon} {src.source_id[:40]}... "
                    f"({src.char_count} chars, {src.word_count} palabras)"
                )
            else:
                label_text = (
                    f"{icon} {src.source_id} "
                    f"({src.char_count} chars, {src.word_count} palabras)"
                )

            if src_type == "files":
                import os

                label_text = (
                    f"{icon} {os.path.basename(src.source_id)} ({src.char_count} chars)"
                )
            elif src_type == "urls":
                if len(src.source_id) > 50:
                    label_text = f"{icon} {src.source_id[:50]}... ({src.char_count} chars)"
                else:
                    label_text = f"{icon} {src.source_id} ({src.char_count} chars)"

            ctk.CTkLabel(src_frame, text=label_text).pack(side="left", padx=5)

            btn = ctk.CTkButton(
                src_frame,
                text="\u2715",
                width=30,
                fg_color=COLORS["error"],
            )
            if remove_fn:
                btn.configure(
                    command=lambda s=src: remove_fn(s.source_type, s.source_id)
                )
            btn.pack(side="right", padx=2)

    if sources and state.phase_manager.is_phase(CleanPhase.SELECT):
        state.transition_to_phase(CleanPhase.CREATE_RAW)


def remove_source(
    source_type: str,
    source_id: str,
    state: TextAnalyzerState,
    callbacks: AppCallbacks,
    clean_text: ctk.CTkTextbox | None,
    clean_freq_text: ctk.CTkTextbox | None,
    stats_label: ctk.CTkLabel | None,
    filter_info: ctk.CTkLabel | None,
    update_fn: Callable[[], None] | None = None,
) -> None:
    """Remove a specific source and update display."""
    state.remove_source(source_type, source_id)
    if state.has_text:
        if update_fn:
            update_fn()
        callbacks.on_status(
            f"Fuente removida \u2014 {len(state.filter_pipeline.filtered_words)}"
            f" palabras restantes",
            "green",
        )
    else:
        if clean_text:
            clean_text.delete("1.0", tk.END)
        if clean_freq_text:
            clean_freq_text.delete("1.0", tk.END)
        if stats_label:
            stats_label.configure(text="Sin contenido")
        if filter_info:
            filter_info.configure(text="")
        callbacks.on_status("Todo el contenido fue removido", "orange")
