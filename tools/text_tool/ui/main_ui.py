"""Main UI orchestrator for Text Analyzer."""
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any, Callable, Dict

import customtkinter as ctk
import tkinter as tk

from core.base_tool_ui import BaseToolUI
from core.constants import font, COLORS
from tools.text_tool.ui.constants import TAB_ORDER, TAB_ICONS, HELP_CONTENT

# Handler imports
from tools.text_tool.ui.handlers import analysis_handler
from tools.text_tool.ui.handlers import file_handler
from tools.text_tool.ui.handlers import keyboard_handler
from tools.text_tool.ui.handlers import progress_handler

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks
    from tools.text_tool.ui.tabs import BaseTab
else:
    from tools.text_tool.ui.state import record_analysis_start, record_analysis_error

logger = logging.getLogger(__name__)


class TextAnalyzerUI(BaseToolUI):
    """Main UI orchestrator - creates state, callbacks, tabs, handles threading."""

    _add_folder_custom = True  # Skip global file selector
    _skip_file_selector = True  # Skip the file selector entirely

    def _setup_ui(self) -> None:
        """Override: text_tool construye UI desde cero."""
        # Don't call parent _setup_ui - we build our own in _build_ui()
        logger.debug("TextAnalyzerUI._setup_ui called - skipping file selector")

    def __init__(self, master: Any, on_process: Callable, **kwargs) -> None:
        from tools.text_tool.ui.state import TextAnalyzerState
        from tools.text_tool.ui.callbacks import AppCallbacks
        from tools.text_tool.ui.tabs import TAB_REGISTRY
        from tools.text_tool.ui.analysis import run_all_analysis, run_stats, run_frequency

        super().__init__(master, on_process, **kwargs)

        # Shared state and callbacks
        self.state: TextAnalyzerState = TextAnalyzerState()
        self.callbacks: AppCallbacks = AppCallbacks(
            on_status=self._on_status,
            on_text_changed=self._on_text_changed,
            on_analysis_request=self._on_analysis_request,
            on_progress=self._on_progress,  # A12: spinner con mensaje
            on_progress_stop=self._stop_all_progress,  # A12: detiene spinner
        )

        # Tab management
        self._tab_registry = TAB_REGISTRY
        self.tabs: Dict[str, "BaseTab"] = {}
        self._tab_frames: Dict[str, ctk.CTkFrame] = {}

        # Threading
        self.executor = ThreadPoolExecutor(max_workers=1)
        self._is_processing = False
        self._is_batch_analysis = False
        self._progress_start_time = 0.0
        self._progress_threshold = 2.0
        self._progress_active = False

        self._build_ui()

    def _on_status(self, message: str, color: str = "gray") -> None:
        """Update status label. Thread-safe via after()."""
        print(f"[STATUS] {message} ({color})")
        # Resolver color: si es HEX directo (comienza con #) usar tal cual
        from core.constants import COLORS
        if color.startswith('#'):
            resolved = color
        else:
            resolved = COLORS.get(color, color)
        if self.status_label:
            self.status_label.configure(text=message, text_color=resolved)

    def _on_text_changed(self) -> None:
        """Refresh all tabs when text changes."""
        for tab in self.tabs.values():
            if hasattr(tab, 'refresh'):
                tab.refresh()
        # Also refresh viz panel if it exists
        if hasattr(self, 'viz_panel'):
            self.viz_panel.refresh()

    def _on_analysis_request(self, method: str, args: Any = None) -> None:
        """Handle requests from tabs (e.g., open modal, full analysis)."""
        handlers = {
            "open_modal": self._open_chart_modal,
            "run_specific": self._run_specific_analysis,
            "full_analysis": lambda _: self._run_all_analysis(),
        }
        handler = handlers.get(method)
        if handler:
            handler(args)

    def _on_progress(self, message: str) -> None:
        """Show progress message with spinner animation."""
        progress_handler.on_progress(self, message)

    def _stop_progress(self) -> None:
        """Stop the progress spinner. (legacy - use _stop_all_progress)"""
        progress_handler.stop_progress(self)

    def _stop_all_progress(self) -> None:
        """Stop spinner and progress bar. A12: feedback cleanup."""
        progress_handler.stop_all_progress(self)

    def _build_ui(self) -> None:
        """Build complete UI layout."""
        self._setup_progress_bar()  # A12: progress bar for UX feedback
        self._setup_title()
        self._setup_help()
        self._setup_status()
        self._setup_tabs()
        self._setup_shortcuts()

    def _setup_status(self) -> None:
        """Create status label with emoji support."""
        self.status_label = ctk.CTkLabel(
            self, text="", text_color="gray",
            font=("Segoe UI Emoji", 12)
        )
        self.status_label.pack(pady=5)

    def _setup_title(self) -> None:
        """Create title label."""
        ctk.CTkLabel(
            self, text="📊 Text Analyzer",
            font=font("title", "bold")
        ).pack(pady=(10, 5))

    def _setup_help(self) -> None:
        """Setup help panel."""
        try:
            from core.help_panel import add_help
            add_help(self, **HELP_CONTENT).pack(fill="x", padx=10, pady=5)
        except ImportError:
            logger.warning("help_panel not available")

    def _setup_tabs(self) -> None:
        """Create tab view and all tab instances."""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=5)

        # Create tab frames (icon-only, tooltip on hover via status bar)
        for key in TAB_ORDER:
            # Always create frame for "viz" even if not in registry
            if key in self._tab_registry or key == "viz":
                icon = TAB_ICONS.get(key, "")
                self._tab_frames[key] = self.tabview.add(icon)

        self._create_tabs()
        self._create_viz_panel()
        self.tabview.configure(command=self._on_tab_changed)

    def _create_viz_panel(self) -> None:
        """Create the visualization panel for the 'viz' tab."""
        from tools.text_tool.ui.viz_panel import VisualizationPanel
        viz_frame = self._tab_frames.get("viz")
        if viz_frame:
            self.viz_panel = VisualizationPanel(
                viz_frame,
                self.state,
                self.callbacks,
                self._tab_registry,
            )
            self.viz_panel.pack(fill="both", expand=True)

    def _create_tabs(self) -> None:
        """Instantiate all tabs from registry."""
        from tools.text_tool.ui.tabs import get_tab
        for key, frame in self._tab_frames.items():
            # Skip "viz" - it's handled by VisualizationPanel
            if key == "viz":
                continue
            cls = get_tab(key)
            if cls:
                self.tabs[key] = cls(frame, self.state, self.callbacks)

    def _on_tab_changed(self, tab_name: str = None) -> None:
        """Handle tab selection change."""
        try:
            if tab_name is None:
                tab_name = self.tabview.get()
            # Map icon back to key (tab_name is now just the icon)
            rev = {v: k for k, v in TAB_ICONS.items()}
            key = rev.get(tab_name, "input")
            self.state.current_tab = key

            # Handle viz tab specially
            if key == "viz" and hasattr(self, "viz_panel"):
                self.viz_panel.refresh()
                return

            tab = self.tabs.get(key)
            if tab and hasattr(tab, 'on_tab_selected'):
                tab.on_tab_selected()
        except Exception as e:
            logger.error(f"Tab change error: {e}")

    def _run_all_analysis(self) -> None:
        """Run all text analysis methods. Delegate to analysis_handler."""
        analysis_handler.run_all_analysis(self)

    def _open_chart_modal(self, args: Dict[str, Any]) -> None:
        """Open modal for expanded chart."""
        try:
            from tools.text_tool.ui.modal import ChartModal
            if args.get("image_data"):
                ChartModal(self, args["image_data"], args.get("title", "Chart"), self._on_status)
        except ImportError:
            logger.error("ChartModal not available")

    def _run_specific_analysis(self, args: Dict[str, Any]) -> None:
        """Run specific analysis requested by tab via dispatch."""
        t = args.get("type")
        if t in ("stats", "frequency"):
            from tools.text_tool.ui.handlers import analysis_handler
            analysis_handler.run_specific_analysis(self, [t])

    def _run_stats(self) -> None:
        """Run statistics analysis. Delegate to analysis_handler."""
        analysis_handler.run_stats(self)

    def _run_frequency(self, params: Dict[str, Any]) -> None:
        """Run frequency analysis. Delegate to analysis_handler."""
        analysis_handler.run_frequency(self, params)

    def _setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts. Delegate to keyboard_handler."""
        keyboard_handler.setup_shortcuts(self)

    def _on_paste(self, event: Any = None) -> str:
        """Handle paste shortcut. Delegate to keyboard_handler."""
        return keyboard_handler.on_paste(self, event)

    def _on_open_file(self, event: Any = None) -> str:
        """Handle open file shortcut. Delegate to file_handler."""
        return file_handler.on_open_file(self, event)

    def _on_save_file(self, event: Any = None) -> str:
        """Handle save file shortcut. Delegate to file_handler."""
        return file_handler.on_save_file(self, event)

    def _on_run(self, event: Any = None) -> str:
        """Handle run shortcut. Delegate to keyboard_handler."""
        return keyboard_handler.on_run(self, event)

    def _on_cancel(self, event: Any = None) -> str:
        """Handle cancel shortcut. Delegate to keyboard_handler."""
        return keyboard_handler.on_cancel(self, event)

    def _load_files(self, files: tuple) -> None:
        """Load files. Delegate to file_handler."""
        file_handler.load_files(self, files)

    def _on_file_drop(self, event: Any) -> str:
        """Handle file drop event. Delegate to file_handler."""
        return file_handler.on_file_drop(self, event)


