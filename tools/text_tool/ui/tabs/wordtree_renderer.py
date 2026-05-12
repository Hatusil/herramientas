"""WordTree interactive renderer for Text Analyzer UI.

This module handles the interactive tree rendering with:
- Clickable nodes
- Collapse/expand functionality
- Canvas with scroll support
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import customtkinter as ctk

from core.constants import COLORS

if TYPE_CHECKING:
    from tools.text_tool.ui.callbacks import AppCallbacks


# Default colors for the dark theme tree (fallback for standalone use)
TREE_BG = COLORS.get("bg_dark", "#1a1a1a")
CARD_BG = COLORS.get("bg_light", "#2d2d2d")
HEADER_BG = COLORS.get("bg_hover", "#3A3A3A")
BTN_NORMAL = COLORS.get("bg_hover", "#3A3A3A")
BTN_HOVER = COLORS.get("bg_medium", "#505050")
BTN_ROOT = COLORS.get("primary", "#4A90D9")
BTN_ROOT_HOVER = COLORS.get("primary_hover", "#6BA8E0")
BTN_COLLAPSE = COLORS.get("bg_medium", "#4A4A4A")
TEXT_PRIMARY = COLORS.get("text_primary", "white")
TEXT_SECONDARY = COLORS.get("text_secondary", "#AAAAAA")
TEXT_MUTED = COLORS.get("text_muted", "#666666")
TEXT_DARK_MUTED = COLORS.get("text_secondary", "#888888")


def build_interactive_tree(
    parent: ctk.CTkFrame,
    tree_data: dict,
    callbacks: AppCallbacks,
    collapsed: dict,
) -> None:
    """Build interactive tree with clickable nodes and collapse/expand.

    Args:
        parent: Parent frame to build tree in
        tree_data: Dictionary with 'root' and 'children' keys
        callbacks: App callback handlers
        collapsed: Dictionary tracking collapsed nodes {word: bool}
    """
    _clear_parent(parent)

    root_phrase = tree_data.get("root", "")
    children = tree_data.get("children", [])

    # Root label
    root_frame = ctk.CTkFrame(parent, fg_color=TREE_BG)
    root_frame.pack(pady=(15, 10), fill="x")

    root_btn = ctk.CTkButton(
        root_frame,
        text=f"🌳 {root_phrase}",
        font=ctk.CTkFont(size=18, weight="bold"),
        fg_color=BTN_ROOT,
        hover_color=BTN_ROOT_HOVER,
        text_color=TEXT_PRIMARY,
        command=lambda: callbacks.expand_wordtree_node(root_phrase),
        width=350,
        height=45,
        corner_radius=8,
    )
    root_btn.pack()

    ctk.CTkLabel(
        root_frame,
        text="(click para re-centrar)",
        font=ctk.CTkFont(size=11),
        text_color=TEXT_DARK_MUTED,
    ).pack(pady=(5, 15))

    if not children:
        ctk.CTkLabel(
            parent, text="No se encontraron palabras relacionadas", text_color=TEXT_DARK_MUTED
        ).pack()
        return

    # Container for children
    children_frame = ctk.CTkFrame(parent, fg_color=TREE_BG)
    children_frame.pack(fill="x", padx=15, pady=10)

    for child in children:
        _build_child_card(children_frame, child, callbacks, collapsed)


def _clear_parent(parent: ctk.CTkFrame) -> None:
    """Clear all widgets from parent frame."""
    for widget in parent.winfo_children():
        widget.destroy()


def _build_child_card(
    card_parent: ctk.CTkFrame,
    child: dict,
    callbacks: AppCallbacks,
    collapsed: dict,
) -> None:
    """Build a single child card with collapse/expand functionality."""
    word = child.get("word", "")
    count = child.get("count", 0)
    subchildren = child.get("children", [])
    is_collapsed = collapsed.get(word, False)
    child_count = len(subchildren)

    card = ctk.CTkFrame(card_parent, fg_color=CARD_BG, corner_radius=10)
    card.pack(side="left", padx=8, pady=8, fill="both", expand=True)

    header_frame = ctk.CTkFrame(card, fg_color="transparent")
    header_frame.pack(fill="x", padx=8, pady=(8, 0))

    # Collapse/expand button
    if child_count > 0:
        collapse_btn = ctk.CTkButton(
            header_frame,
            text="−" if not is_collapsed else "+",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=BTN_COLLAPSE,
            hover_color="#5A5A5A",
            text_color=TEXT_PRIMARY,
            width=30,
            height=30,
            command=lambda w=word: _toggle_collapse(callbacks, word, collapsed),
            corner_radius=4,
        )
        collapse_btn.pack(side="left", padx=(0, 5))

    # Word button
    btn_width = 140 if child_count == 0 else 110
    word_btn = ctk.CTkButton(
        card,
        text=word.title(),
        font=ctk.CTkFont(size=15, weight="bold"),
        fg_color=BTN_NORMAL,
        hover_color=BTN_HOVER,
        text_color=TEXT_PRIMARY,
        command=lambda w=word: callbacks.expand_wordtree_node(w),
        width=btn_width,
        height=40,
        corner_radius=6,
    )
    word_btn.pack(padx=8, pady=(8 if child_count == 0 else 0, 4))

    # Count label
    count_text = f"🔢 {count} veces"
    if is_collapsed and child_count > 0:
        count_text += f" ({child_count} hidden)"

    ctk.CTkLabel(
        card, text=count_text, font=ctk.CTkFont(size=12), text_color=TEXT_SECONDARY
    ).pack(pady=(0, 8))

    # Sub-children
    if subchildren and not is_collapsed:
        sub_frame = ctk.CTkFrame(card, fg_color="transparent")
        sub_frame.pack(padx=8, pady=(0, 8))

        ctk.CTkLabel(
            sub_frame,
            text="Continúa:",
            font=ctk.CTkFont(size=10),
            text_color=TEXT_MUTED,
        ).pack(pady=(4, 4))

        for sub in subchildren[:4]:
            sub_btn = ctk.CTkButton(
                sub_frame,
                text=f"→ {sub['word']} ({sub['count']})",
                font=ctk.CTkFont(size=11),
                fg_color="#252525",
                hover_color="#404040",
                text_color="#BBBBBB",
                command=lambda w=sub["word"]: callbacks.expand_wordtree_node(w),
                height=26,
                width=120,
                corner_radius=4,
            )
            sub_btn.pack(pady=2)
    elif is_collapsed:
        ctk.CTkLabel(
            card,
            text="(Click + para expandir)",
            font=ctk.CTkFont(size=10),
            text_color=TEXT_MUTED,
        ).pack(pady=5)


def _toggle_collapse(
    callbacks: AppCallbacks, word: str, collapsed: dict
) -> None:
    """Toggle collapse state for a node."""
    collapsed[word] = not collapsed.get(word, False)
    status = "colapsado" if collapsed[word] else "expandido"
    callbacks.update_status(f"Nodo '{word}' {status}", "green")


def add_export_button(parent: ctk.CTkFrame, callbacks: AppCallbacks) -> None:
    """Add export/detail button at the bottom of the tree."""
    export_frame = ctk.CTkFrame(parent, fg_color=TREE_BG)
    export_frame.pack(fill="x", pady=(15, 10), padx=10)

    ctk.CTkButton(
        export_frame,
        text="🔍 Ver en detalle + Exportar",
        font=ctk.CTkFont(size=13, weight="bold"),
        fg_color=BTN_ROOT,
        hover_color=BTN_ROOT_HOVER,
        text_color=TEXT_PRIMARY,
        command=callbacks.open_wordtree_modal,
        height=35,
        corner_radius=6,
    ).pack(pady=5)
