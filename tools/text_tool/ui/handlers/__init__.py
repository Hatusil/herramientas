"""Handlers module for text_tool UI."""
from __future__ import annotations

# Analysis handlers
from tools.text_tool.ui.handlers.analysis_handler import (
    run_all_analysis,
    run_stats,
    run_frequency,
)

# File handlers
from tools.text_tool.ui.handlers.file_handler import (
    on_open_file,
    on_save_file,
    load_files,
    on_file_drop,
)

# Keyboard handlers
from tools.text_tool.ui.handlers.keyboard_handler import (
    setup_shortcuts,
    on_paste,
    on_run,
    on_cancel,
    on_open_file as kbd_on_open_file,
    on_save_file as kbd_on_save_file,
)

# Progress handlers
from tools.text_tool.ui.handlers.progress_handler import (
    on_progress,
    stop_progress,
    stop_all_progress,
)

__all__ = [
    # Analysis
    "run_all_analysis",
    "run_stats",
    "run_frequency",
    # File
    "on_open_file",
    "on_save_file",
    "load_files",
    "on_file_drop",
    # Keyboard
    "setup_shortcuts",
    "on_paste",
    "on_run",
    "on_cancel",
    # Progress
    "on_progress",
    "stop_progress",
    "stop_all_progress",
]