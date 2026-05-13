"""Centralized state for Search Tool UI."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class SearchState:
    """Centralized state for the Search Tool."""

    query: str = ""
    filters: Dict[str, Any] = field(
        default_factory=lambda: {
            "name_only": "",
            "extension": "",
            "date_from": "",
            "date_to": "",
            "content": "",
        }
    )
    results: List[Dict[str, Any]] = field(default_factory=list)
    is_searching: bool = False
    selected_folder: str = ""
    progress: int = 0

    def update_query(self, query: str) -> None:
        """Update the search query."""
        self.query = query

    def update_filter(self, key: str, value: Any) -> None:
        """Update a specific filter."""
        if key in self.filters:
            self.filters[key] = value

    def set_results(self, results: List[Dict[str, Any]]) -> None:
        """Set search results."""
        self.results = results

    def set_searching(self, is_searching: bool) -> None:
        """Set searching state."""
        self.is_searching = is_searching

    def set_progress(self, progress: int) -> None:
        """Set progress value (0-100)."""
        self.progress = max(0, min(100, progress))

    def set_folder(self, folder: str) -> None:
        """Set selected folder."""
        self.selected_folder = folder

    def reset(self) -> None:
        """Reset state to initial values."""
        self.query = ""
        self.filters = {
            "name_only": "",
            "extension": "",
            "date_from": "",
            "date_to": "",
            "content": "",
        }
        self.results = []
        self.is_searching = False
        self.selected_folder = ""
        self.progress = 0

    @property
    def has_results(self) -> bool:
        """Check if there are results."""
        return len(self.results) > 0

    @property
    def result_count(self) -> int:
        """Get the number of results."""
        return len(self.results)