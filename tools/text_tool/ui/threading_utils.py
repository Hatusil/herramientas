"""
Threading utilities para TextAnalyzerUI.
Separado de main_ui.py por SRP (máxima R0: clases <300 líneas).
"""
import logging
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

logger = logging.getLogger(__name__)

import customtkinter as ctk


def create_executor() -> ThreadPoolExecutor:
    """Crea executor para operaciones en background."""
    return ThreadPoolExecutor(max_workers=1)


def run_in_thread(
    ui: Any,
    target: Callable,
    callback: Callable[[Any], None],
    *args: Any, **kwargs: Any
) -> None:
    """Execute function in background thread."""
    if ui._is_processing:
        ui._on_status("Análisis en progreso...", "orange")
        return

    ui._is_processing = True
    ui._progress_start_time = _get_time()
    _schedule_progress(ui)

    def worker() -> None:
        try:
            result = target(*args, **kwargs)
            ui.after(0, lambda: _handle_result(ui, result, callback))
        except Exception as e:
            ui.after(0, lambda: _handle_error(ui, str(e)))

    ui.executor.submit(worker)


def _schedule_progress(ui: Any) -> None:
    """Show progress bar after threshold if still running."""
    ui.after(int(ui._progress_threshold * 1000), lambda: _check_show_progress(ui))


def _check_show_progress(ui: Any) -> None:
    """Display progress bar if operation is slow."""
    if ui._is_processing:
        ui._on_status("Procesando...", "blue")
        if ui.progress_bar:
            ui.progress_bar.pack(pady=(0, 5))
            ui.progress_bar.start()


def _handle_result(ui: Any, result: Any, callback: Callable) -> None:
    """Process successful result."""
    _stop_progress(ui)
    ui._is_processing = False
    callback(result)


def _handle_error(ui: Any, msg: str) -> None:
    """Process error from background thread."""
    _stop_progress(ui)
    ui._is_processing = False
    ui._on_status(f"Error: {msg}", "red")


def _stop_progress(ui: Any) -> None:
    """Hide progress bar."""
    if ui.progress_bar:
        ui.progress_bar.stop()
        ui.progress_bar.pack_forget()


def _progress_callback(ui: Any, current: int, total: int, msg: str = "") -> None:
    """Update progress during long operations."""
    if total > 0 and ui.progress_bar:
        ui.progress_bar.set(current / total)
    ui._on_status(f"{msg} {current}/{total}", "blue")


def _get_time() -> float:
    """Get current time for threshold check."""
    import time
    return time.time()