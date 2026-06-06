"""Progress handlers for text_tool UI."""
from __future__ import annotations

import time
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.text_tool.ui.main_ui import TextAnalyzerUI


def on_progress(ui: "TextAnalyzerUI", message: str) -> None:
    """Show progress message with spinner animation."""
    # A12: progress feedback para operaciones largas
    spinner = ["|", "/", "-", "\\"]

    # Stop any existing spinner first
    ui._progress_active = False
    time.sleep(0.05)  # Give previous thread time to stop

    ui._progress_active = True
    ui._progress_message = message

    def _spin():
        i = 0
        while ui._progress_active:
            ui._on_status(f"{spinner[i % 4]} {message}...", "blue")
            time.sleep(0.3)
            i += 1

    ui._spin_thread = threading.Thread(target=_spin, daemon=True)
    ui._spin_thread.start()


def stop_progress(ui: "TextAnalyzerUI") -> None:
    """Stop the progress spinner. (legacy - use stop_all_progress)"""
    ui._progress_active = False


def stop_all_progress(ui: "TextAnalyzerUI") -> None:
    """Stop spinner and progress bar. A12: feedback cleanup."""
    ui._progress_active = False
    # Also stop progress bar if active
    if hasattr(ui, '_processing') and ui._processing:
        ui.stop_progress()