"""Keyboard handlers for text_tool UI."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from tools.text_tool.ui.main_ui import TextAnalyzerUI


def setup_shortcuts(ui: "TextAnalyzerUI") -> None:
    """Setup keyboard shortcuts."""
    from tools.text_tool.ui.keyboard_shortcuts import setup_shortcuts as setup
    setup(ui, {
        'on_paste': on_paste,
        'on_open': on_open_file,
        'on_save': on_save_file,
        'on_run': on_run,
        'on_cancel': on_cancel,
    })


def on_paste(ui: "TextAnalyzerUI", event: Any = None) -> str:
    """Handle paste shortcut."""
    return "break"


def on_run(ui: "TextAnalyzerUI", event: Any = None) -> str:
    """Handle run shortcut."""
    return "break"


def on_cancel(ui: "TextAnalyzerUI", event: Any = None) -> str:
    """Handle cancel shortcut - stop analysis."""
    if ui._is_processing:
        ui._is_processing = False
        ui.stop_progress()  # A9: thread-safe
        ui._on_status("Análisis cancelado", "orange")
    return "break"


def on_open_file(ui: "TextAnalyzerUI", event: Any = None) -> str:
    """Handle open file shortcut - delegate to file_handler."""
    from tools.text_tool.ui.handlers.file_handler import on_open_file as of
    return of(ui, event)


def on_save_file(ui: "TextAnalyzerUI", event: Any = None) -> str:
    """Handle save file shortcut - delegate to file_handler."""
    from tools.text_tool.ui.handlers.file_handler import on_save_file as sf
    return sf(ui, event)