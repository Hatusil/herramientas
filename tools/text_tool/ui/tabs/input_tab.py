"""Input tab for Text Analyzer UI.

Este módulo delega a submódulos para SRP:
- input_text.py: Text input area
- input_file.py: File selection
- input_url.py: URL input
"""
from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, List, Tuple

import customtkinter as ctk

from tools.text_tool.ui.tabs.base_tab import BaseTab

# Importar submódulos
from .input_text import setup_text_input
from .input_file import setup_file_input
from .input_url import setup_url_input
from tools.text_tool.processors import extract_text_from_file, extract_text_from_url

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks

logger = logging.getLogger(__name__)


class InputTab(BaseTab):
    """Tab for text input (direct text, files, URLs). A9: async loading."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        state: TextAnalyzerState,
        callbacks: AppCallbacks,
    ) -> None:
        """Initialize InputTab."""
        self._input_type: ctk.StringVar = ctk.StringVar(value="text")
        self._text_area: ctk.CTkTextbox | None = None
        self._url_entries: List[Tuple[ctk.CTkFrame, ctk.CTkEntry]] = []
        self._load_btn: ctk.CTkButton | None = None
        self._file_frame: ctk.CTkFrame | None = None
        self._url_frame: ctk.CTkFrame | None = None
        self._executor = ThreadPoolExecutor(max_workers=2)
        super().__init__(parent, state, callbacks)

    def _setup_frame(self) -> None:
        """Create the main frame for this tab."""
        self._frame = ctk.CTkFrame(self._parent, fg_color="transparent")
        self._build_ui()

    def _build_ui(self) -> None:
        """Build the tab UI delegando a submódulos."""
        self._build_input_type_selector()
        self._build_text_input()
        self._build_file_input()
        self._build_url_input()
        self._build_load_button()
        self._on_input_type_change()

    def _build_input_type_selector(self) -> None:
        """Build the input type radio buttons."""
        tipo_frame = ctk.CTkFrame(self._frame)
        tipo_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkRadioButton(
            tipo_frame,
            text="📝 Texto",
            variable=self._input_type,
            value="text",
            command=self._on_input_type_change,
        ).pack(side="left", padx=5)

        ctk.CTkRadioButton(
            tipo_frame,
            text="📄 Archivos",
            variable=self._input_type,
            value="files",
            command=self._on_input_type_change,
        ).pack(side="left", padx=5)

        ctk.CTkRadioButton(
            tipo_frame,
            text="🌐 URLs",
            variable=self._input_type,
            value="url",
            command=self._on_input_type_change,
        ).pack(side="left", padx=5)

    def _build_text_input(self) -> None:
        """Delegado a input_text.py"""
        self._text_area = setup_text_input(self._frame, self._state, self._callbacks)

    def _build_file_input(self) -> None:
        """Delegado a input_file.py"""
        self._file_frame, self._file_count_label, self._pending_files = setup_file_input(
            self._frame, self._state, self._callbacks)

    def _build_url_input(self) -> None:
        """Delegado a input_url.py"""
        self._url_frame, self._url_entries, self._url_count_label = setup_url_input(
            self._frame, self._state, self._callbacks)

    def _build_load_button(self) -> None:
        """Build the main load button."""
        btn_frame = ctk.CTkFrame(self._frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)

        self._load_btn = ctk.CTkButton(
            btn_frame,
            text="📥 Agregar Texto",
            command=self._load_and_store,
            height=40,
        )
        self._load_btn.pack(fill="x")
        
        # Button text per input type
        self._button_texts = {
            "text": "📥 Agregar Texto",
            "files": "📄 Seleccionar Archivos",
            "url": "🌐 Cargar URLs",
        }

    # === Rest of methods remain here ===
    # (Keep existing logic for events, callbacks, etc.)

    def _on_input_type_change(self) -> None:
        """Handle input type change."""
        tipo = self._input_type.get()
        
        # Show/hide appropriate frame
        if self._text_area:
            self._text_area.pack_forget() if tipo != "text" else self._text_area.pack(fill="both", expand=True, padx=10, pady=10)
        
        if self._file_frame:
            self._file_frame.pack_forget() if tipo != "files" else self._file_frame.pack(fill="x", padx=10, pady=10)
        
        if self._url_frame:
            self._url_frame.pack_forget() if tipo != "url" else self._url_frame.pack(fill="x", padx=10, pady=10)
        
        # Update button text based on input type
        if hasattr(self, '_load_btn') and self._load_btn and hasattr(self, '_button_texts'):
            self._load_btn.configure(text=self._button_texts.get(tipo, "📥 Agregar Texto"))

    def _load_and_store(self) -> None:
        """Load input and store to state only. No analysis triggered - manual flow."""
        input_type = self._input_type.get()

        # Texto directo - síncrono (rápido)
        if input_type == "text" and self._text_area:
            new_text = self._text_area.get("1.0", "end").strip()
            if not new_text:
                self._callbacks.on_status("⚠️ Escribí algún texto primero", "orange")
                return
            self._callbacks.on_status("📝 Texto cargado", "blue")
            self._state.add_text_source(new_text)
            self._finish_loading(1, 1)

        # Archivos - async 
        elif input_type == "files":
            if not self._pending_files:
                self._callbacks.on_status("⚠️ Agregá archivos primero", "orange")
                return
            self._callbacks.on_status(f"📂 Cargando {len(self._pending_files)} archivo(s)...", "blue")
            files_to_load = list(self._pending_files)
            self._executor.submit(self._load_files_async, files_to_load)

        # URLs - async 
        elif input_type == "url":
            urls = [u.get().strip() for _, u in self._url_entries if u.get().strip()]
            if not urls:
                self._callbacks.on_status("⚠️ Escribí al menos una URL", "orange")
                return
            self._callbacks.on_status(f"🌐 Descargando {len(urls)} URL(s)...", "blue")
            self._executor.submit(self._load_urls_async, urls)

    def _load_files_async(self, files: List[str]) -> None:
        """Load files in background thread. A9: thread-safe."""
        total = len(files)
        file_count = 0

        for i, f in enumerate(files, 1):
            self._callbacks.on_status(f"📄 ({i}/{total}) {os.path.basename(f)}", "blue")
            result = extract_text_from_file(f)
            if result.get('success'):
                self._state.add_file_source(f, result.get('text', '') + "\n")
                file_count += 1

        # Update UI in main thread
        def on_done():
            self._pending_files.clear()
            if hasattr(self, '_file_count_label'):
                self._file_count_label.configure(text="0")
            if file_count > 0:
                self._callbacks.on_status(f"✅ {file_count}/{total} archivo(s) cargados", "green")
            else:
                self._callbacks.on_status("⚠️ Ningún archivo pudo ser leído", "red")
            self._finish_loading(file_count, total)

        # Use after() to update UI from main thread
        self._parent.after(0, on_done)

    def _load_urls_async(self, urls: List[str]) -> None:
        """Load URLs in background thread. A9: thread-safe."""
        total = len(urls)
        url_count = 0
        failed_urls = []

        for i, url in enumerate(urls, 1):
            short_url = url[:40] + "..." if len(url) > 40 else url
            self._callbacks.on_status(f"🌐 ({i}/{total}) {short_url}", "blue")
            result = extract_text_from_url(url)
            if result.get('success'):
                self._state.add_url_source(url, result.get('text', '') + "\n")
                url_count += 1
            else:
                err = result.get('error', 'Error desconocido')
                failed_urls.append(f"{short_url}: {err}")
                self._callbacks.on_status(f"❌ {short_url}", "red")

        # Update UI in main thread
        def on_done():
            if url_count > 0:
                msg = f"✅ {url_count}/{total} URL(s) descargadas"
                if failed_urls:
                    msg += f" — {len(failed_urls)} fallaron"
                self._callbacks.on_status(msg, "green")
                for err in failed_urls:
                    self._callbacks.on_status(f"  ⚠️ {err}", "orange")
            else:
                self._callbacks.on_status("⚠️ Ninguna URL pudo ser descargada", "red")
                for err in failed_urls:
                    self._callbacks.on_status(f"  ⚠️ {err}", "orange")
            self._finish_loading(url_count, total)

        self._parent.after(0, on_done)

    def _finish_loading(self, loaded: int, total: int) -> None:
        """Show total loaded and refresh tabs. No analysis trigger - manual flow only."""
        total_chars = len(self._state.text_content)
        total_words = len(self._state.text_content.split())
        self._callbacks.on_status(f"✅ Total: {total_chars} chars, {total_words} palabras", "green")
        if loaded > 0:
            self._callbacks.emit_text_changed()

    def get_frame(self) -> ctk.CTkFrame:
        """Return the main frame for this tab (BaseTab abstract method)."""
        return self._frame