"""Visualization Panel - dropdown selector for all visualizations."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

import customtkinter as ctk

from tools.text_tool.ui.constants import VIZ_OPTIONS

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks
    from tools.text_tool.ui.tabs.base_tab import BaseTab

logger = logging.getLogger(__name__)


class VisualizationPanel(ctk.CTkFrame):
    """Panel with dropdown to select and display different visualizations."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        state: "TextAnalyzerState",
        callbacks: "AppCallbacks",
        tab_registry: Dict[str, type],
    ) -> None:
        """Initialize the visualization panel.

        Args:
            parent: Parent CTkFrame.
            state: Shared state object.
            callbacks: App callbacks.
            tab_registry: Registry of all available tab classes.
        """
        super().__init__(parent, fg_color="transparent")
        self._state = state
        self._callbacks = callbacks
        self._tab_registry = tab_registry
        self._current_viz: Optional[str] = None
        self._active_tab: Optional["BaseTab"] = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Create the UI components."""
        # Dropdown selector
        selector_frame = ctk.CTkFrame(self, fg_color="transparent")
        selector_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            selector_frame,
            text="Visualización:",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left", padx=5)

        # Build dropdown values from VIZ_OPTIONS
        viz_values = [f"{v['icon']} {v['name']}" for v in VIZ_OPTIONS.values()]
        self._viz_dropdown = ctk.CTkComboBox(
            selector_frame,
            values=viz_values,
            command=self._on_viz_changed,
            state="readonly",
        )
        self._viz_dropdown.set(viz_values[0] if viz_values else "")
        self._viz_dropdown.pack(side="left", fill="x", expand=True, padx=5)

        # Container for the active visualization
        self._viz_container = ctk.CTkFrame(self, fg_color="transparent")
        self._viz_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Initialize with first visualization
        if VIZ_OPTIONS:
            first_key = list(VIZ_OPTIONS.keys())[0]
            self._load_viz(first_key)

    def _on_viz_changed(self, selection: str) -> None:
        """Handle visualization dropdown change."""
        # Extract key from "icon name" format
        for key, viz in VIZ_OPTIONS.items():
            if f"{viz['icon']} {viz['name']}" == selection:
                self._load_viz(key)
                return

    def _load_viz(self, viz_key: str) -> None:
        """Load and display the selected visualization tab.

        Args:
            viz_key: Key of the visualization to load (e.g., "wc", "trends").
        """
        # Clear previous tab
        for widget in self._viz_container.winfo_children():
            widget.destroy()
        self._active_tab = None

        # Get the tab class from registry
        tab_class = self._tab_registry.get(viz_key)
        if not tab_class:
            logger.error(f"Visualization tab not found: {viz_key}")
            return

        try:
            # Create the tab instance in our container
            self._active_tab = tab_class(self._viz_container, self._state, self._callbacks)
            self._current_viz = viz_key
            logger.debug(f"Loaded visualization: {viz_key}")
        except Exception as e:
            logger.error(f"Error loading visualization {viz_key}: {e}")

    def refresh(self) -> None:
        """Refresh the current visualization."""
        if self._active_tab and hasattr(self._active_tab, "refresh"):
            self._active_tab.refresh()

    def get_current_viz(self) -> Optional[str]:
        """Get the currently selected visualization key."""
        return self._current_viz