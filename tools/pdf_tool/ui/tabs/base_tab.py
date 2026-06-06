"""Base tab interface for PDF Tool UI."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

import customtkinter as ctk

if TYPE_CHECKING:
    from tools.pdf_tool.ui.callbacks import PDFCallbacks
    from tools.pdf_tool.ui.state import PDFState


class PDFBaseTab(ABC):
    """Abstract base class for all tabs in PDF Tool UI.

    Tabs receive a ``state`` (``PDFState``) reference at construction
    time and publish each widget they own into ``self._state.<attr>``
    exactly once, at the end of ``_setup_frame()``. Click handlers
    never reassign — they read the typed dataclass field directly. The
    ``main_ui`` back-reference remains for the chrome (e.g. files
    list, status label) but is no longer the widget namespace.
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        callbacks: PDFCallbacks,
        main_ui: Optional[object] = None,
        state: Optional["PDFState"] = None,
    ) -> None:
        self._parent = parent
        self._callbacks = callbacks
        self._main_ui = main_ui
        self._state = state
        self._frame: Optional[ctk.CTkFrame] = None
        self._setup_frame()
        if self._frame is not None:
            self._frame.pack(fill="both", expand=True)

    @abstractmethod
    def _setup_frame(self) -> None:
        """Create the main frame for this tab.

        Subclasses MUST publish every widget they own to
        ``self._state.<attr>`` at the end of this method.
        """
        ...

    @abstractmethod
    def get_frame(self) -> ctk.CTkFrame:
        """Return the main frame for this tab."""

    def on_tab_selected(self) -> None:
        """Called when this tab is selected. Override for custom behavior."""
        pass

    def refresh(self) -> None:
        """Refresh the tab's UI based on current state."""
        pass

    def update_status(self, message: str, color: str = "blue") -> None:
        """Helper to update status via callbacks."""
        self._callbacks.status(message, color)
