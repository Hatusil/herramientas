"""Callback handlers for PDF Tool UI."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class PDFCallbacks:
    """Callback handlers for PDF tool events."""

    on_status: Optional[Callable[[str, str], None]] = field(default=None)

    def status(self, message: str, color: str = "blue") -> None:
        if self.on_status:
            self.on_status(message, color)
