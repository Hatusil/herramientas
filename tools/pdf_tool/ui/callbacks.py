"""Callback handlers for PDF Tool UI.

The ``PDFCallbacks`` dataclass aggregates the four event channels a
handler might emit during its work:

* ``on_status`` — human-readable status updates (e.g. "rotating
  page 3 of 12"). Wired to the chrome status label.
* ``on_files_changed`` — file-list mutation notifications (e.g. after
  a pipeline produces a new file). Wired to the file selector refresh.
* ``on_progress`` — numeric progress updates for the progress bar.
* ``on_error`` — non-fatal error reporting (e.g. validation
  failure). The handler decides whether to surface a hard exception
  or recover.

All four fields are ``Optional[Callable[..., None]]`` so that the
type-checked concrete signatures stay at the call sites; the
dataclass holds only the dispatch shape.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class PDFCallbacks:
    """Callback handlers for PDF tool events.

    All four fields default to ``None`` so that test code and partial
    wiring paths can instantiate the dataclass without populating
    every channel. The orchestrator wires the concrete callables in
    ``PDFToolUI._setup_ui`` after construction.
    """

    on_status: Optional[Callable[..., None]] = None
    on_files_changed: Optional[Callable[..., None]] = None
    on_progress: Optional[Callable[..., None]] = None
    on_error: Optional[Callable[..., None]] = None

    def status(self, message: str, color: str = "blue") -> None:
        """Convenience pass-through to ``on_status`` (legacy shape)."""
        if self.on_status is not None:
            self.on_status(message, color)
