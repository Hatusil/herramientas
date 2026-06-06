"""UI state dataclasses for the PDF Tool.

This module holds the typed, single-source-of-truth state objects shared
between tabs, handlers, and the orchestrator. The pattern (per the
``ui-state-shape`` architecture pattern) is:

* ``PDFState`` — every widget reference a tab publishes; each field is
  typed with the exact CustomTkinter / Tk widget class (no ``Any``,
  no widening). Tabs publish each widget once at the end of
  ``_setup_frame()``; handlers read it back via direct attribute access.
* ``PDFContext`` — three orchestration handles (file list, status
  label, async process entry point) that don't belong on the widget
  state but that handlers still need. Held under ``PDFState.ctx``.

Both classes live in this single module (not ``context.py``) because
they are tightly coupled — ``PDFState.ctx`` references ``PDFContext``
directly — and a single import point keeps the call sites readable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional

import customtkinter as ctk


@dataclass
class PDFContext:
    """Orchestration handles shared across PDF tool handlers.

    Three concerns stay on the ``PDFToolUI`` orchestrator rather than on
    the typed widget state because their lifecycle is bound to the
    chrome (file selector button, status label, async dispatcher),
    not to any single tab.

    Attributes:
        files: Selected PDF file paths. Mutated by the file selector
            and consumed by handlers.
        status_label: Chrome-level status widget. Optional because the
            test harness and early-init paths may instantiate a state
            before the chrome is built.
        process_async: Orchestrator's async dispatch callable. The
            handler invokes this with ``(operation, files, options)``.
    """

    files: List[str] = field(default_factory=list)
    status_label: Optional[ctk.CTkLabel] = None
    process_async: Callable[..., Any] = None


@dataclass
class PDFState:
    """Typed widget state for the PDF Tool.

    Each field corresponds to a widget (or ``StringVar``) that a tab
    owns and that a handler reads. The exact CTk widget type is
    declared so that an IDE / type checker can flag mismatches at the
    call site, and so a handler that tries to ``.get()`` an
    ``CTkOptionMenu`` vs a ``StringVar`` produces different hints.

    A tab publishes its widgets to this dataclass once, at the end of
    ``_setup_frame()``:

        self._state.annot_text = self._annot_text
        self._state.annot_page = self._annot_page
        ...

    No click handler should ever reassign a field here — that is the
    anti-pattern R14 guards against.
    """

    # --- edit (annotation, redaction, range extraction) ---
    annot_text: Optional[ctk.CTkEntry] = None
    annot_page: Optional[ctk.CTkEntry] = None
    annot_x: Optional[ctk.CTkEntry] = None
    annot_y: Optional[ctk.CTkEntry] = None
    redact_page: Optional[ctk.CTkEntry] = None
    redact_x: Optional[ctk.CTkEntry] = None
    redact_y: Optional[ctk.CTkEntry] = None
    redact_w: Optional[ctk.CTkEntry] = None
    redact_h: Optional[ctk.CTkEntry] = None
    extract_start: Optional[ctk.CTkEntry] = None
    extract_end: Optional[ctk.CTkEntry] = None

    # --- watermark (text + image paths, sliders, position) ---
    # `watermark_text` and `watermark_image_path` are the persistent
    # StringVars bound to the entries; the entries themselves are
    # recreated-free views that toggle via pack()/pack_forget().
    watermark_text: Optional[ctk.StringVar] = None
    watermark_size: Optional[ctk.CTkEntry] = None
    watermark_color: Optional[ctk.CTkEntry] = None
    watermark_opacity_slider: Optional[ctk.CTkSlider] = None
    watermark_rotation_slider: Optional[ctk.CTkSlider] = None
    watermark_position: Optional[ctk.CTkOptionMenu] = None
    watermark_pos_x: Optional[ctk.CTkEntry] = None
    watermark_pos_y: Optional[ctk.CTkEntry] = None
    watermark_image_path: Optional[ctk.StringVar] = None
    watermark_type: Optional[ctk.StringVar] = None

    # --- transform (rotate, reorder) ---
    rotate_var: Optional[ctk.StringVar] = None
    rotate_pages: Optional[ctk.CTkEntry] = None
    reorder_input: Optional[ctk.CTkEntry] = None

    # --- numbers ---
    num_position: Optional[ctk.CTkOptionMenu] = None
    num_start: Optional[ctk.CTkEntry] = None
    num_format: Optional[ctk.CTkEntry] = None

    # --- security ---
    lock_password: Optional[ctk.CTkEntry] = None
    unlock_password: Optional[ctk.CTkEntry] = None

    # --- combine ---
    extract_pages: Optional[ctk.CTkEntry] = None

    # --- info ---
    info_text: Optional[ctk.CTkTextbox] = None

    # --- optimize ---
    compress_level: Optional[ctk.CTkOptionMenu] = None

    # --- pipeline ---
    pipeline_operations: List[dict] = field(default_factory=list)

    # --- shared orchestration handles ---
    ctx: PDFContext = field(default_factory=PDFContext)
