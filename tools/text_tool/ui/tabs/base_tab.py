"""Base tab interface for Text Analyzer UI."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

import customtkinter as ctk

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks


class BaseTab(ABC):
    """Abstract base class for all tabs in Text Analyzer UI."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        state: TextAnalyzerState,
        callbacks: AppCallbacks,
    ) -> None:
        """Initialize the tab with shared state and callbacks.

        Args:
            parent: The parent CTkFrame for this tab.
            state: Shared state object with text content and sources.
            callbacks: Callback handlers for app events.
        """
        self._parent = parent
        self._state = state
        self._callbacks = callbacks
        self._frame: Optional[ctk.CTkFrame] = None
        self._setup_frame()

    def _setup_frame(self) -> None:
        """Create the main frame for this tab. Override in subclasses."""
        self._frame = ctk.CTkFrame(self._parent, fg_color="transparent")

    @abstractmethod
    def get_frame(self) -> ctk.CTkFrame:
        """Return the main frame for this tab.

        Returns:
            The CTkFrame containing this tab's UI.
        """

    def on_tab_selected(self) -> None:
        """Called when this tab is selected. Override for custom behavior."""
        pass

    def refresh(self) -> None:
        """Refresh the tab's UI based on current state. Override as needed."""
        pass

    def update_status(self, message: str, color: str = "gray") -> None:
        """Helper to update status via callbacks."""
        self._callbacks.update_status(message, color)

    @property
    def state(self) -> TextAnalyzerState:
        """Access the shared state."""
        return self._state

    @property
    def callbacks(self) -> AppCallbacks:
        """Access the callbacks."""
        return self._callbacks