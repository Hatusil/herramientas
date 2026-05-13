"""Callback handlers for Search Tool UI."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Dict, Any


@dataclass
class SearchCallbacks:
    """Callback handlers for search events."""

    on_search_start: Callable[[], None] = field(
        default=lambda: None
    )
    on_search_progress: Callable[[int, int], None] = field(
        default=lambda *_: None
    )
    on_search_complete: Callable[[List[Dict[str, Any]]], None] = field(
        default=lambda *_: None
    )
    on_result_select: Callable[[Dict[str, Any]], None] = field(
        default=lambda *_: None
    )

    def trigger_search_start(self) -> None:
        """Trigger on_search_start callback."""
        self.on_search_start()

    def trigger_search_progress(self, current: int, total: int) -> None:
        """Trigger on_search_progress callback."""
        self.on_search_progress(current, total)

    def trigger_search_complete(self, results: List[Dict[str, Any]]) -> None:
        """Trigger on_search_complete callback."""
        self.on_search_complete(results)

    def trigger_result_select(self, result: Dict[str, Any]) -> None:
        """Trigger on_result_select callback."""
        self.on_result_select(result)