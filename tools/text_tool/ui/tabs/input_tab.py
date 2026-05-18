"""Input tab for Text Analyzer UI.

Este módulo delega a submódulos para SRP:
- input_text.py: Text input area
- input_file.py: File selection
- input_url.py: URL input
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List, Tuple

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog

from tools.text_tool.ui.tabs.base_tab import BaseTab
from core.utils import clean_text
from core.constants import COLORS

# Importar submódulos
from .input_text import setup_text_input
from .input_file import setup_file_input
from .input_url import setup_url_input

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks

logger = logging.getLogger(__name__)


class InputTab(BaseTab):
    """Tab for text input (direct text, files, URLs)."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        state: TextAnalyzerState,
        callbacks: AppCallbacks,
    ) -> None:
        """Initialize InputTab."""
        self._input_type: ctk.StringVar = ctk.StringVar(value="text")
        self._text_area: ctk.CTkTextbox | None = None
        self._files_label: ctk.CTkLabel | None = None
        self._url_entries: List[Tuple[ctk.CTkFrame, ctk.CTkEntry]] = []
        self._url_count_label: ctk.CTkLabel | None = None
        self._url_container: ctk.CTkFrame | None = None
        self._load_btn: ctk.CTkButton | None = None
        self._file_frame: ctk.CTkFrame | None = None
        self._url_frame: ctk.CTkFrame | None = None
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
        self._file_frame, self._file_label = setup_file_input(self._frame, self._state, self._callbacks)

    def _build_url_input(self) -> None:
        """Delegado a input_url.py"""
        self._url_frame, self._url_entries = setup_url_input(self._frame, self._state, self._callbacks)

    def _build_load_button(self) -> None:
        """Build the main load button."""
        btn_frame = ctk.CTkFrame(self._frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)

        self._load_btn = ctk.CTkButton(
            btn_frame,
            text="📥 Agregar Texto",
            command=self._load_and_analyze,
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

    def _load_and_analyze(self) -> None:
        """Load input and trigger analysis."""
        text = ""
        input_type = self._input_type.get()
        
        if input_type == "text" and self._text_area:
            text = self._text_area.get("1.0", "end").strip()
        elif input_type == "files":
            from tkinter import filedialog
            files = filedialog.askopenfilenames(
                title="Seleccionar archivos para analizar",
                filetypes=[
                    ("Todos los soportados", "*.*"),
                    ("PDF", "*.pdf"),
                    ("Word", "*.docx *.doc"),
                    ("Excel", "*.xlsx *.xls"),
                    ("CSV", "*.csv"),
                    ("Texto plano", "*.txt *.md"),
                ]
            )
            if files:
                file_count = 0
                self._callbacks.on_status("Cargando archivos...", "blue")
                from tools.text_tool.processors import extract_text_from_file
                for f in files:
                    result = extract_text_from_file(f)
                    if result.get('success'):
                        text += result.get('text', '') + "\n"
                        file_count += 1
                        self._callbacks.on_status(f"Procesando {file_count}/{len(files)}...", "blue")
                    else:
                        logger.warning(f"Could not extract text from {f}: {result.get('error')}")
                # Update file label
                if hasattr(self, '_file_label') and self._file_label:
                    self._file_label.configure(text=f"{file_count} archivo(s) cargado(s)")
                # Feedback solo en status
                self._callbacks.on_status(f"Listo: {file_count} archivo(s)", "green")
        elif input_type == "url":
            url_count = 0
            print(f"[DEBUG] URL entries: {len(self._url_entries)}")
            for entry_frame, url_entry in self._url_entries:
                url = url_entry.get().strip()
                print(f"[DEBUG] URL value: '{url}'")
            self._callbacks.on_status("Cargando URLs...", "blue")
            for _, url_entry in self._url_entries:
                url = url_entry.get().strip()
                if url:
                    try:
                        import requests
                        print(f"[DEBUG] Fetching: {url}")
                        self._callbacks.on_status(f"Descargando {url}...", "blue")
                        response = requests.get(url, timeout=10)
                        print(f"[DEBUG] Got response: {len(response.text)} chars")
                        text += response.text + "\n"
                        url_count += 1
                    except Exception as e:
                        print(f"[DEBUG] Error fetching {url}: {e}")
                        logger.warning(f"Could not fetch {url}: {e}")
            if url_count > 0:
                self._callbacks.on_status(f"Listo: {url_count} URL(s)", "green")
            else:
                self._callbacks.on_status("⚠️ No se pudieron cargar las URLs", "orange")
        
        if text:
            self._state.update_text(text)
            self._callbacks.on_status(f"✅ {len(text)} caracteres cargados", "green")
            self._callbacks.request_analysis("run_specific", {"type": "stats", "params": {}})
        elif input_type in ("files", "url"):
            # Show message if no text was loaded
            msg = "No se pudieron cargar los archivos" if input_type == "files" else "No se pudieron cargar las URLs"
            self._callbacks.on_status(f"⚠️ {msg}", COLORS.get("warning", "orange"))
        else:
            self._callbacks.on_status("⚠️ No hay texto para analizar", COLORS.get("warning", "orange"))

    def get_frame(self) -> ctk.CTkFrame:
        """Return the main frame for this tab (BaseTab abstract method)."""
        return self._frame