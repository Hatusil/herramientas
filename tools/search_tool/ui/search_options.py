"""Search options panel for Search Tool UI."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional, Dict, Any

import customtkinter as ctk

if TYPE_CHECKING:
    from tools.search_tool.ui.state import SearchState
    from tools.search_tool.ui.callbacks import SearchCallbacks

logger = logging.getLogger(__name__)

EXTENSION_PRESETS = ["", "txt", "py", "md", "json", "xml", "csv", "log"]


class SearchOptions:
    """Panel for search query and filters."""

    def __init__(
        self,
        ui: "SearchToolUIBase",
        parent_frame: ctk.CTkFrame,
    ) -> None:
        """Initialize search options panel.

        Args:
            ui: Parent UI instance.
            parent_frame: Parent frame to contain this panel.
        """
        self._ui = ui
        self._parent = parent_frame
        self._frame: Optional[ctk.CTkFrame] = None
        self._query_entry: Optional[ctk.CTkEntry] = None
        self._name_only_var: Optional[ctk.StringVar] = None
        self._extension_combo: Optional[ctk.CTkComboBox] = None
        self._search_btn: Optional[ctk.CTkButton] = None
        self._search_callback: Optional[callable] = None
        self.setup_ui()

    def setup_ui(self) -> None:
        """Create the search options UI."""
        self._frame = ctk.CTkFrame(self._parent)
        self._frame.pack(fill="x", padx=10, pady=5)

        title = ctk.CTkLabel(
            self._frame,
            text="🔍 Opciones de búsqueda",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        title.pack(anchor="w", padx=10, pady=(10, 5))

        query_frame = ctk.CTkFrame(self._frame, fg_color="transparent")
        query_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(query_frame, text="Buscar:").pack(side="left", padx=(0, 10))

        self._query_entry = ctk.CTkEntry(
            query_frame,
            placeholder_text="Término de búsqueda...",
        )
        self._query_entry.pack(side="left", fill="x", expand=True)

        filters_frame = ctk.CTkFrame(self._frame, fg_color="transparent")
        filters_frame.pack(fill="x", padx=10, pady=5)

        self._name_only_var = ctk.StringVar(value="")
        name_only_check = ctk.CTkCheckBox(
            filters_frame,
            text="Solo nombre",
            variable=self._name_only_var,
            onvalue="true",
            offvalue="",
        )
        name_only_check.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(filters_frame, text="Extensión:").pack(side="left", padx=(0, 5))

        self._extension_combo = ctk.CTkComboBox(
            filters_frame,
            values=EXTENSION_PRESETS,
            width=100,
            state="readonly",
        )
        self._extension_combo.pack(side="left")
        self._extension_combo.set("")

        self._search_btn = ctk.CTkButton(
            self._frame,
            text="Iniciar búsqueda",
            command=self._on_search,
            height=36,
        )
        self._search_btn.pack(fill="x", padx=10, pady=(10, 10))

    def _on_search(self) -> None:
        """Handle search button click."""
        filters = self.get_filters()
        logger.info(f"Search triggered with filters: {filters}")

    def get_filters(self) -> Dict[str, Any]:
        """Get current filter values.

        Returns:
            Dictionary with filter values.
        """
        return {
            "query": self._query_entry.get() if self._query_entry else "",
            "name_only": self._name_only_var.get() if self._name_only_var else "",
            "extension": self._extension_combo.get() if self._extension_combo else "",
        }

    def set_filters(self, filters: Dict[str, Any]) -> None:
        """Set filter values.

        Args:
            filters: Dictionary with filter values.
        """
        if self._query_entry and "query" in filters:
            self._query_entry.delete(0, "end")
            self._query_entry.insert(0, filters.get("query", ""))

        if self._name_only_var and "name_only" in filters:
            self._name_only_var.set(filters.get("name_only", ""))

        if self._extension_combo and "extension" in filters:
            self._extension_combo.set(filters.get("extension", ""))

    def get_frame(self) -> ctk.CTkFrame:
        """Get the main frame.

        Returns:
            The panel frame.
        """
        return self._frame

    def set_search_callback(self, callback: callable) -> None:
        """Set the callback for search button.

        Args:
            callback: Function to call when search is triggered.
        """
        self._search_callback = callback

    def get_search_params(self) -> Dict[str, Any]:
        """Get complete search parameters for the processor.

        Returns:
            Dictionary with all search parameters.
        """
        return {
            "query": self._query_entry.get().strip() if self._query_entry else "",
            "name_only": self._name_only_var.get() if self._name_only_var else "",
            "extension": self._extension_combo.get() if self._extension_combo else "",
        }

    def set_searching(self, is_searching: bool) -> None:
        """Enable/disable search button during search.

        Args:
            is_searching: Whether search is in progress.
        """
        if self._search_btn:
            if is_searching:
                self._search_btn.configure(state="disabled", text="Buscando...")
            else:
                self._search_btn.configure(state="normal", text="Iniciar búsqueda")