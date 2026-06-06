"""Clean tab - Results display section."""
from __future__ import annotations

import tkinter as tk
from collections import Counter
from typing import TYPE_CHECKING, Callable

import customtkinter as ctk

from core.constants import COLORS

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks


def build_action_buttons(
    parent: ctk.CTkFrame,
    show_raw_fn: Callable[[], None],
    show_filtered_fn: Callable[[], None],
) -> tuple[ctk.CTkButton, ctk.CTkButton]:
    """Build action buttons (raw text + filtered text).

    Returns (preview_raw_btn, apply_clean_btn).
    """
    action_frame = ctk.CTkFrame(parent, fg_color="transparent")
    action_frame.pack(fill="x", padx=10, pady=10)

    preview_raw_btn = ctk.CTkButton(
        action_frame,
        text="\U0001f4dc Texto Bruto",
        command=show_raw_fn,
        width=120,
        fg_color=COLORS["bg_medium"],
    )
    preview_raw_btn.pack(side="left", padx=2)

    apply_clean_btn = ctk.CTkButton(
        action_frame,
        text="\U0001f50d Texto Filtrado",
        command=show_filtered_fn,
        width=120,
        fg_color=COLORS["primary"],
    )
    apply_clean_btn.pack(side="left", padx=2)

    return preview_raw_btn, apply_clean_btn


def build_results_section(
    parent: ctk.CTkFrame,
) -> tuple[ctk.CTkTextbox, ctk.CTkTextbox]:
    """Build results display section. Returns (clean_text, clean_freq_text)."""
    results_section = ctk.CTkLabel(
        parent,
        text="\U0001f4ca RESULTADO",
        font=ctk.CTkFont(size=14, weight="bold"),
    )
    results_section.pack(anchor="w", padx=10, pady=(15, 5))

    clean_text = ctk.CTkTextbox(
        parent,
        wrap="word",
        height=100,
        fg_color=COLORS["bg_input"],
        text_color=COLORS["text_primary"],
    )
    clean_text.pack(fill="both", expand=False, padx=10, pady=5)

    top_words_label = ctk.CTkLabel(
        parent,
        text="Top 20 palabras:",
        font=ctk.CTkFont(size=12),
    )
    top_words_label.pack(anchor="w", padx=10, pady=(10, 0))

    clean_freq_text = ctk.CTkTextbox(
        parent,
        wrap="word",
        font=("Courier New", 11),
        fg_color=COLORS["bg_input"],
        text_color=COLORS["text_primary"],
    )
    clean_freq_text.pack(fill="both", expand=True, padx=10, pady=5)

    return clean_text, clean_freq_text


def build_execute_button(
    parent: ctk.CTkFrame,
    execute_fn: Callable[[], None],
) -> ctk.CTkButton:
    """Build the main execute analysis button. Returns execute_btn."""
    execute_btn = ctk.CTkButton(
        parent,
        text="\u25b6 EJECUTAR AN\u00c1LISIS",
        command=execute_fn,
        height=45,
        font=ctk.CTkFont(size=16, weight="bold"),
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_hover"],
        state="disabled",
    )
    execute_btn.pack(fill="x", padx=10, pady=(20, 10))
    return execute_btn


def show_raw_text(
    clean_text: ctk.CTkTextbox | None,
    clean_freq_text: ctk.CTkTextbox | None,
    state: TextAnalyzerState,
    callbacks: AppCallbacks,
    preview_raw_btn: ctk.CTkButton | None,
    apply_clean_btn: ctk.CTkButton | None,
    update_exe_fn: Callable[[], None] | None = None,
) -> None:
    """Show raw (unfiltered) text in display."""
    if not clean_text or not clean_freq_text:
        return

    pipeline = state.filter_pipeline
    clean_text.delete("1.0", tk.END)
    clean_text.insert("1.0", pipeline.raw_text[:3000])

    word_freq = Counter(pipeline.raw_words)
    top_20 = word_freq.most_common(20)
    update_freq_display(clean_freq_text, top_20, "TEXTO BRUTO")

    if preview_raw_btn:
        preview_raw_btn.configure(fg_color=COLORS["primary"])
    if apply_clean_btn:
        apply_clean_btn.configure(fg_color=COLORS["bg_medium"])

    if update_exe_fn:
        update_exe_fn()


def show_filtered_text(
    clean_text: ctk.CTkTextbox | None,
    clean_freq_text: ctk.CTkTextbox | None,
    state: TextAnalyzerState,
    callbacks: AppCallbacks,
    preview_raw_btn: ctk.CTkButton | None,
    apply_clean_btn: ctk.CTkButton | None,
    update_exe_fn: Callable[[], None] | None = None,
) -> None:
    """Show filtered text in display."""
    if not clean_text or not clean_freq_text:
        return

    pipeline = state.filter_pipeline
    filtered = pipeline.filtered_words
    clean_text.delete("1.0", tk.END)
    clean_text.insert("1.0", " ".join(filtered)[:3000])

    word_freq = Counter(filtered)
    top_20 = word_freq.most_common(20)
    update_freq_display(clean_freq_text, top_20, "TEXTO FILTRADO")

    if preview_raw_btn:
        preview_raw_btn.configure(fg_color=COLORS["bg_medium"])
    if apply_clean_btn:
        apply_clean_btn.configure(fg_color=COLORS["primary"])

    if update_exe_fn:
        update_exe_fn()


def update_freq_display(
    clean_freq_text: ctk.CTkTextbox | None,
    top_20: list,
    label: str,
) -> None:
    """Update the frequency display with top words (bar chart)."""
    if not clean_freq_text:
        return

    if not top_20:
        clean_freq_text.delete("1.0", tk.END)
        clean_freq_text.insert("1.0", "Sin palabras")
        return

    max_count = top_20[0][1] if top_20 else 1
    max_word_len = max(len(word) for word, _ in top_20) if top_20 else 10
    text_width = max(15, max_word_len + 2)

    texto = f"\U0001f4ca Top 20 palabras ({label}):\n"
    texto += "=" * (text_width + 10) + "\n\n"

    for i, (word, count) in enumerate(top_20, 1):
        bar = "\u2588" * min(int(count / max_count * 20), 20)
        texto += f"{i:2}. {word:<{text_width}} {count:>4} {bar}\n"

    clean_freq_text.delete("1.0", tk.END)
    clean_freq_text.insert("1.0", texto)
