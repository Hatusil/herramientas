"""Main UI orchestrator for Search Tool - integrates all panels."""
from __future__ import annotations

import logging
import threading
from typing import Optional, Dict, Any

import customtkinter as ctk

# Import BaseToolUI - refactorizada para seguir arquitectura
from core.base_tool_ui import BaseToolUI

# Imports for panels
from tools.search_tool.ui.folder_selector import FolderSelector
from tools.search_tool.ui.search_options import SearchOptions
from tools.search_tool.ui.results_view import ResultsView

# Imports for state management
from tools.search_tool.ui.state import SearchState
from tools.search_tool.ui.callbacks import SearchCallbacks

# Observability (A12)
from core.metrics import Counter, Timer

logger = logging.getLogger(__name__)

# Type alias for backward compatibility
SearchToolUIBase = BaseToolUI


class SearchToolUI(SearchToolUIBase):
    """Main UI orchestrator that integrates all Search Tool panels."""

    def __init__(
        self,
        master: Any,
        on_process: Optional[callable] = None,
        **kwargs,
    ) -> None:
        """Initialize SearchToolUI - extends BaseToolUI."""
        # BaseToolUI espera on_process como segundo argumento
        super().__init__(master, on_process or self._dummy_process, **kwargs)
        self._on_process = on_process
        self._init_state()
        self._init_metrics()
    
    def _setup_ui(self) -> None:
        """Override: SearchToolUI builds its own UI - no file selector needed."""
        # Don't call super() - we build our own UI in build_ui()
        pass
    
    def _dummy_process(self, files, options):
        """Dummy process callback - search doesn't use file selector."""
        return {'success': True, 'message': 'Search uses folder selector'}

    def _init_state(self) -> None:
        """Initialize internal state."""
        self._search_thread: Optional[threading.Thread] = None
        self._cancel_event: Optional[threading.Event] = None
        self.state = SearchState()
        self.callbacks = SearchCallbacks()
        self.folder_selector: Optional[FolderSelector] = None
        self.search_options: Optional[SearchOptions] = None
        self.results_view: Optional[ResultsView] = None

    def _init_metrics(self) -> None:
        """Initialize observability metrics."""
        self._search_counter = Counter("search_tool.searches")
        self._search_timer = Timer("search_tool.search_duration")
        # Auto-build UI on init (self is the parent frame)
        self.build_ui(self)

    def build_ui(self, parent_frame: ctk.CTkFrame) -> None:
        """Build the complete UI by instantiating all panels.

        Args:
            parent_frame: The frame to contain this UI.
        """
        # Add title and help button
        from core.help_panel import add_help
        from core.constants import font

        title_label = ctk.CTkLabel(
            parent_frame,
            text="🔍 Búsqueda Avanzada",
            font=font("header", "bold")
        )
        title_label.pack(pady=(0, 10))

        add_help(
            parent_frame,
            title="Ayuda - Búsqueda Avanzada",
            description="🔍 Buscar archivos por nombre, fecha y contenido",
            usage=[
                "1. Seleccionar carpeta a buscar",
                "2. Elegir tipo de búsqueda (nombre, contenido, fecha)",
                "3. Ingresar texto de búsqueda",
                "4. Click en 'Buscar'",
            ],
            tips=[
                "💡 Usar * para buscar todos los archivos",
                "💡 La búsqueda por contenido es más lenta",
            ],
        ).pack(fill="x", padx=10, pady=5)

        # Create folder selector panel
        self.folder_selector = FolderSelector(ui=self, parent_frame=parent_frame)

        # Create search options panel
        self.search_options = SearchOptions(ui=self, parent_frame=parent_frame)

        # Create results view panel
        self.results_view = ResultsView(ui=self, parent_frame=parent_frame)

        # Connect search button from search_options to our _start_search
        if self.search_options:
            self.search_options.set_search_callback(self._start_search)

    def _start_search(self) -> None:
        """Start a new search with current folder and options."""
        folder = self._get_search_folder()
        if not folder:
            return

        search_params = self._get_search_params()
        if not search_params:
            return

        self._prepare_search_state(folder, search_params)
        self._launch_search_thread(folder, search_params)

    def _get_search_folder(self) -> Optional[str]:
        """Validate and return selected folder."""
        folder = self.folder_selector.get_selected_folder() if self.folder_selector else None
        if not folder:
            logger.warning("No folder selected")
        return folder

    def _get_search_params(self) -> Optional[Dict[str, Any]]:
        """Get search parameters from options panel."""
        if not self.search_options:
            logger.warning("No search options available")
            return None
        return self.search_options.get_search_params()

    def _prepare_search_state(self, folder: str, params: Dict[str, Any]) -> None:
        """Prepare state and UI for search."""
        self.state.set_folder(folder)
        self.state.set_searching(True)
        self.state.update_query(params.get("query", ""))
        self._cancel_event = threading.Event()
        self._cancel_event.clear()

        if self.search_options:
            self.search_options.set_searching(True)
        if self.results_view:
            self.results_view.clear()
        self.callbacks.trigger_search_start()

    def _launch_search_thread(self, folder: str, params: Dict[str, Any]) -> None:
        """Launch search in background thread."""
        self._search_thread = threading.Thread(
            target=self._search_worker,
            args=(folder, params),
        )
        self._search_thread.daemon = True
        self._search_thread.start()
        logger.info(f"Started search in folder: {folder}")

    def _stop_search(self) -> None:
        """Stop the current search."""
        if self._cancel_event:
            self._cancel_event.set()
        logger.info("Search stop requested")

        # Update state
        self.state.set_searching(False)

        # Update UI
        if self.search_options:
            self.search_options.set_searching(False)

    def _search_worker(self, folder: str, params: Dict[str, Any]) -> None:
        """Worker thread that executes the search."""
        self._search_timer.start()
        self._search_counter.increment()
        try:
            result = self._execute_search(folder, params)
            self._schedule_result_update(result)
        except Exception as e:
            logger.exception(f"Search error: {e}")
            self.after(0, lambda: self._on_search_error(str(e)))
        finally:
            self._search_timer.stop()
            self._cancel_event = None

    def _execute_search(self, folder: str, params: Dict[str, Any]) -> Dict:
        """Execute search via processor."""
        from tools.search_tool.processor import search_all
        return search_all(folder, params, cancel_flag=self._cancel_event)

    def _schedule_result_update(self, result: Dict) -> None:
        """Schedule UI update based on search result."""
        if result.get("cancelled"):
            self.after(0, lambda: self._on_search_cancelled())
        elif result.get("success"):
            results = result.get("results", [])
            self.after(0, lambda: self._on_search_complete(results))
        else:
            error = result.get("error", "Unknown error")
            self.after(0, lambda: self._on_search_error(error))

    def _on_search_cancelled(self) -> None:
        """Handle search cancellation."""
        self.state.set_searching(False)

        if self.search_options:
            self.search_options.set_searching(False)

        logger.info("Search cancelled UI update")

    def _on_search_complete(self, results: list) -> None:
        """Handle successful search completion.

        Args:
            results: Search results list.
        """
        self.state.set_searching(False)
        self.state.set_results(results)

        if self.search_options:
            self.search_options.set_searching(False)

        if self.results_view:
            self.results_view.display_results(results)

        self.callbacks.trigger_search_complete(results)
        logger.info(f"Search complete: {len(results)} results")

    def _on_search_error(self, error: str) -> None:
        """Handle search error.

        Args:
            error: Error message.
        """
        self.state.set_searching(False)

        if self.search_options:
            self.search_options.set_searching(False)

        logger.error(f"Search error: {error}")


__all__ = ["SearchToolUI"]