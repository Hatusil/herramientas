"""Main UI orchestrator for Text Analyzer."""
from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog

from core.base_tool_ui import BaseToolUI
from core.constants import font
from tools.text_tool.ui.threading_utils import run_in_thread
from tools.text_tool.ui.keyboard_shortcuts import (
    setup_shortcuts, handle_paste, handle_open, handle_save, handle_run, handle_cancel
)
from tools.text_tool.ui.constants import TAB_ORDER, TAB_ICONS, HELP_CONTENT

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks
    from tools.text_tool.ui.tabs import BaseTab

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
            on_analysis_request=self._on_analysis_request
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

        self._build_ui()

    # === Callbacks ===

    def _on_status(self, message: str, color: str = "gray") -> None:
        """Update status label."""
        if self.status_label and not getattr(self, '_is_batch_analysis', False):
            self.status_label.configure(text=message, text_color=color)

    def _on_text_changed(self) -> None:
        """Refresh all tabs when text changes."""
        for tab in self.tabs.values():
            if hasattr(tab, 'refresh'):
                tab.refresh()

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

    # === UI Construction ===

    def _build_ui(self) -> None:
        """Build complete UI layout."""
        self._setup_title()
        self._setup_help()
        self._setup_status()
        self._setup_tabs()
        self._setup_shortcuts()

    def _setup_status(self) -> None:
        """Create status label."""
        self.status_label = ctk.CTkLabel(self, text="", text_color="gray")
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
            if key in self._tab_registry:
                icon = TAB_ICONS.get(key, "")
                self._tab_frames[key] = self.tabview.add(icon)

        self._create_tabs()
        self.tabview.configure(command=self._on_tab_changed)

    def _create_tabs(self) -> None:
        """Instantiate all tabs from registry."""
        from tools.text_tool.ui.tabs import get_tab
        for key, frame in self._tab_frames.items():
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
            tab = self.tabs.get(key)
            if tab and hasattr(tab, 'on_tab_selected'):
                tab.on_tab_selected()
        except Exception as e:
            logger.error(f"Tab change error: {e}")

    # === Threading ===

    def run_in_thread(self, target, callback, *args, **kwargs):
        return run_in_thread(self, target, callback, *args, **kwargs)

    def _stop_progress(self):
        if self.progress_bar:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()

    # === Analysis ===

    def _run_all_analysis(self) -> None:
        """Run all text analysis methods."""
        if not self.state.has_text:
            self._on_status("No hay texto para analizar", "orange")
            return

        text = self.state.cleaned_content or self.state.text_content
        self._is_processing = True
        self._is_batch_analysis = True
        self._on_status("Ejecutando análisis...", "blue")

        def worker() -> None:
            try:
                results = run_all_analysis(text)
                self.after(0, lambda: self._on_analysis_complete(results))
            except Exception as e:
                self._is_batch_analysis = False
                self.after(0, lambda err=e: self._handle_error(str(err)))

        self.executor.submit(worker)

    def _on_analysis_complete(self, results: Dict[str, Any]) -> None:
        """Handle analysis completion."""
        self._is_processing = False
        self._is_batch_analysis = False  # Habilitar status antes de mostrar mensaje
        errors = [k for k, v in results.items() if isinstance(v, dict) and v.get("error")]
        ok = len(results) - len(errors)
        if errors:
            self._on_status(f"Visualizaciones: {ok} ok, {len(errors)} fallaron", "orange")
        else:
            self._on_status(f"Visualizaciones y análisis: {ok} generados", "green")
        self._on_text_changed()

    def _open_chart_modal(self, args: Dict[str, Any]) -> None:
        """Open modal for expanded chart."""
        try:
            from tools.text_tool.ui.modal import ChartModal
            if args.get("image_data"):
                ChartModal(self, args["image_data"], args.get("title", "Chart"), self._on_status)
        except ImportError:
            logger.error("ChartModal not available")

    def _run_specific_analysis(self, args: Dict[str, Any]) -> None:
        """Run specific analysis requested by tab."""
        t = args.get("type")
        params = args.get("params", {})
        if t == "stats":
            self._run_stats()
        elif t == "frequency":
            self._run_frequency(params)

    def _run_stats(self) -> None:
        """Run statistics analysis."""
        text = self.state.cleaned_content or self.state.text_content
        if text:
            self.executor.submit(lambda: self._on_stats_complete(run_stats(text)))

    def _on_stats_complete(self, result: Dict[str, Any]) -> None:
        """Handle stats completion."""
        if result.get("success"):
            self._on_status("Estadísticas actualizadas", "green")
        self._on_text_changed()

    def _run_frequency(self, params: Dict[str, Any]) -> None:
        """Run frequency analysis."""
        text = self.state.cleaned_content or self.state.text_content
        if text:
            self.executor.submit(
                lambda: self._on_freq_complete(run_frequency(text, params.get("top_n", 50)))
            )

    def _on_freq_complete(self, result: Dict[str, Any]) -> None:
        """Handle frequency completion."""
        self._on_text_changed()
        self._on_status("Frecuencias actualizadas", "green")

    # === Keyboard ===

    def _setup_shortcuts(self) -> None:
        """Bind global keyboard shortcuts."""
        handlers = {
            'on_paste': self._on_paste,
            'on_open': self._on_open_file,
            'on_save': self._on_save_file,
            'on_run': self._on_run,
            'on_cancel': self._on_cancel,
        }
        setup_shortcuts(self, handlers)

    def _on_paste(self, event: Any = None) -> str:
        """Handle Ctrl+V."""
        try:
            text = self.clipboard_get()
            if text and text.strip():
                self.state.update_text(text)
                self._on_status(f"Pegado: {len(text)} caracteres", "green")
        except tk.TclError:
            self._on_status("Clipboard vacío", "orange")
        return "break"

    def _on_open_file(self, event: Any = None) -> str:
        """Handle Ctrl+O."""
        files = filedialog.askopenfilenames(
            title="Seleccionar archivos",
            filetypes=[("Texto", "*.txt *.md"), ("Documentos", "*.pdf *.docx"), ("Todos", "*.*")]
        )
        if files:
            self._load_files(files)
        return "break"

    def _on_save_file(self, event: Any = None) -> str:
        """Handle Ctrl+S."""
        text = self.state.cleaned_content or self.state.text_content
        if not text:
            self._on_status("No hay texto para guardar", "orange")
            return "break"

        path = filedialog.asksaveasfilename(
            title="Guardar archivo", defaultextension=".txt",
            filetypes=[("Texto", "*.txt"), ("Markdown", "*.md"), ("Todos", "*.*")]
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(text)
                self._on_status(f"Guardado: {os.path.basename(path)}", "green")
            except Exception as e:
                self._on_status(f"Error al guardar: {e}", "red")
        return "break"

    def _on_run(self, event: Any = None) -> str:
        """Handle Ctrl+Enter."""
        self._run_all_analysis()
        return "break"

    def _on_cancel(self, event: Any = None) -> str:
        """Handle Escape."""
        if self._is_processing:
            self._is_processing = False
            self._stop_progress()
            self._on_status("Análisis cancelado", "orange")
        return "break"

    # === File Operations ===

    def _load_files(self, files: tuple) -> None:
        """Load files and update state."""
        try:
            from tools.text_tool.processor import extract_text_from_file
            texts = []
            for f in files:
                result = extract_text_from_file(f)
                if result.get('success'):
                    texts.append(result['text'])

            if texts:
                new_text = '\n\n'.join(texts)
                if self.state.text_content:
                    self.state.text_content += '\n\n' + new_text
                else:
                    self.state.text_content = new_text
                self.state.sources["files"].extend(list(files))
                self.state.file_path = files[0] if files else None
                self._on_text_changed()
                self._on_status(f"{len(files)} archivos: {len(self.state.text_content)} chars", "green")
        except ImportError:
            self._on_status("Instala dependencias: pip install wordcloud nltk pdfplumber", "red")

    def _on_file_drop(self, event: Any) -> str:
        """Handle file drop on widget."""
        files = self.tk.splitlist(event.data) if hasattr(event, 'data') else ()
        if files:
            valid = [f for f in files if Path(f).suffix.lower() in {'.txt', '.md', '.pdf', '.docx', '.doc'}]
            if valid:
                self._load_files(tuple(valid))
            elif files:
                self._on_status("Tipo de archivo no soportado", "red")
        return "break"


def _get_time() -> float:
    """Get current time for threshold check."""
    import time
    return time.time()