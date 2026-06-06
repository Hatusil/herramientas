"""Callback handlers for Text Analyzer UI."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, Any


@dataclass
class AppCallbacks:
    """Callback handlers for app events."""

    on_status: Callable[[str, str], None] = field(
        default=lambda *_: None
    )
    on_text_changed: Callable[[], None] = field(
        default=lambda *_: None
    )
    on_analysis_request: Callable[[str, Any], None] = field(
        default=lambda *_: None
    )
    on_progress: Callable[[str], None] = field(  # A12: progress feedback
        default=lambda *_: None
    )
    on_progress_stop: Callable[[], None] = field(  # A12: stop progress
        default=lambda *_: None
    )

    def update_status(self, message: str, color: str = "gray") -> None:
        """Convenience method to update status via callback."""
        self.on_status(message, color)

    def emit_text_changed(self) -> None:
        """Convenience method to emit text change event."""
        self.on_text_changed()

    def request_analysis(self, method: str, args: Any = None) -> None:
        """Convenience method to request analysis."""
        self.on_analysis_request(method, args)

    def show_progress(self, message: str) -> None:
        """Show progress indicator. A12: observability."""
        self.on_progress(message)

    def stop_progress(self) -> None:
        """Stop progress indicator. A12: observability."""
        self.on_progress_stop()