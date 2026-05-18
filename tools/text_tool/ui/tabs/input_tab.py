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
        
        # === FASE 1: CARGAR CONTENIDO ===
        
        if input_type == "text" and self._text_area:
            text = self._text_area.get("1.0", "end").strip()
            if text:
                self._callbacks.on_status("📝 Cargando texto...", "blue")
                self._callbacks.on_status(f"✅ Texto cargado ({len(text)} caracteres)", "green")
            else:
                self._callbacks.on_status("⚠️ Escribí algún texto primero", "orange")
                return
                
        elif input_type == "files":
            from tkinter import filedialog
            files = filedialog.askopenfilenames(
                title="Seleccionar archivos",
                filetypes=[
                    ("Todos", "*.*"),
                    ("PDF", "*.pdf"),
                    ("Word", "*.docx"),
                    ("Excel", "*.xlsx"),
                    ("CSV", "*.csv"),
                    ("Texto", "*.txt *.md"),
                ]
            )
            if not files:
                self._callbacks.on_status("⚠️ No seleccionaste archivos", "orange")
                return
                
            file_count = 0
            self._callbacks.on_status("📂 Cargando archivos...", "blue")
            from tools.text_tool.processors import extract_text_from_file
            for i, f in enumerate(files, 1):
                result = extract_text_from_file(f)
                if result.get('success'):
                    text += result.get('text', '') + "\n"
                    file_count += 1
                    self._callbacks.on_status(f"📄 Procesando {i}/{len(files)}...", "blue")
                else:
                    logger.warning(f"Error: {result.get('error')}")
            
            if hasattr(self, '_file_label') and self._file_label:
                self._file_label.configure(text=f"{file_count} archivo(s)")
            # Update state sources
            self._state.sources["files"].extend(list(files))
            self._callbacks.on_status(f"✅ {file_count} archivo(s) cargado(s)", "green")
            
        elif input_type == "url":
            urls = [u.get().strip() for _, u in self._url_entries if u.get().strip()]
            if not urls:
                self._callbacks.on_status("⚠️ Escribí al menos una URL", "orange")
                return
                
            url_count = 0
            self._callbacks.on_status("🌐 Descargando URLs...", "blue")
            for i, url in enumerate(urls, 1):
                try:
                    import requests
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    self._callbacks.on_status(f"🌐 Descargando {i}/{len(urls)}...", "blue")
                    response = requests.get(url, headers=headers, timeout=10)
                    text += response.text + "\n"
                    url_count += 1
                except Exception as e:
                    logger.warning(f"Error: {e}")
            
            self._callbacks.on_status(f"✅ {url_count} URL(s) descargada(s)", "green")
            self._state.sources["urls"].extend(urls)
        
        # === FASE 2: ANALIZAR ===
        
        if text:
            self._state.update_text(text)
            self._callbacks.on_status("📊 Ejecutando análisis...", "blue")
            self._callbacks.request_analysis("run_specific", {"type": "stats", "params": {}})
        else:
            self._callbacks.on_status("⚠️ No hay contenido para analizar", "orange")

    def get_frame(self) -> ctk.CTkFrame:
        """Return the main frame for this tab (BaseTab abstract method)."""
        return self._frame