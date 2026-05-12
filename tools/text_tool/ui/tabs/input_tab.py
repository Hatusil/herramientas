"""Input tab for Text Analyzer UI."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List, Tuple

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog

from tools.text_tool.ui.tabs.base_tab import BaseTab
from core.utils import clean_text

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
        """Build the tab UI."""
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
        """Build the direct text input area."""
        self._text_area = ctk.CTkTextbox(self._frame, wrap="word")
        self._text_area.pack(fill="both", expand=True, padx=10, pady=10)
        self._setup_keyboard_shortcuts()

    def _build_file_input(self) -> None:
        """Build the file selection frame."""
        self._file_frame = ctk.CTkFrame(self._frame)
        self._file_frame.pack(fill="x", padx=10, pady=10)
        self._file_frame.pack_forget()

        ctk.CTkLabel(
            self._file_frame,
            text="📄 Archivos Seleccionados:",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=5)

        self._files_label = ctk.CTkLabel(
            self._file_frame,
            text="No hay archivos seleccionados",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w",
            justify="left",
        )
        self._files_label.pack(fill="x", padx=5, pady=5)

    def _build_url_input(self) -> None:
        """Build the URL input frame."""
        self._url_frame = ctk.CTkFrame(self._frame)
        self._url_frame.pack(fill="x", padx=10, pady=10)
        self._url_frame.pack_forget()

        ctk.CTkLabel(self._url_frame, text="URLs:").pack(anchor="w")

        self._url_container = ctk.CTkFrame(self._url_frame)
        self._url_container.pack(fill="both", expand=True, pady=5)

        url_btns = ctk.CTkFrame(self._url_frame, fg_color="transparent")
        url_btns.pack(fill="x", pady=5)

        ctk.CTkButton(
            url_btns, text="➕ Agregar URL", command=self._add_url_field
        ).pack(side="left", padx=5)

        self._url_count_label = ctk.CTkLabel(url_btns, text="1 URL", text_color="gray")
        self._url_count_label.pack(side="left", padx=10)

        self._url_entries = []
        self._add_url_field()

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

    def _setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts for text area."""
        if self._text_area:
            self._text_area.bind("<Control-v>", self._on_paste)
            self._text_area.bind("<Control-o>", self._on_open_file)
            self._text_area.bind("<Control-s>", self._on_save_file)

    def get_frame(self) -> ctk.CTkFrame:
        """Return the main frame for this tab."""
        return self._frame

    def refresh(self) -> None:
        """Refresh the input tab state."""
        self._update_files_display()

    def _on_input_type_change(self) -> None:
        """Show/hide input frames based on selected type."""
        tipo = self._input_type.get()

        if self._text_area:
            self._text_area.pack_forget()
        if self._file_frame:
            self._file_frame.pack_forget()
        if self._url_frame:
            self._url_frame.pack_forget()

        if tipo == "text":
            self._text_area.pack(fill="both", expand=True, padx=10, pady=10)
            self._load_btn.configure(text="📥 Agregar Texto")
        elif tipo == "files":
            self._file_frame.pack(fill="x", padx=10, pady=10)
            self._load_btn.configure(text="📄 Agregar Archivos")
        elif tipo == "url":
            self._url_frame.pack(fill="x", padx=10, pady=10)
            self._load_btn.configure(text="🌐 Agregar URLs")

    def _add_url_field(self) -> None:
        """Add a new URL input field."""
        row = ctk.CTkFrame(self._url_container, fg_color="transparent")
        row.pack(fill="x", pady=2)

        entry = ctk.CTkEntry(row, placeholder_text="https://...")
        entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        btn = ctk.CTkButton(
            row, text="❌", width=30, command=lambda: self._remove_url_field(row, entry)
        )
        btn.pack(side="left")

        self._url_entries.append((row, entry))
        self._url_count_label.configure(text=f"{len(self._url_entries)} URLs")

    def _remove_url_field(self, row: ctk.CTkFrame, entry: ctk.CTkEntry) -> None:
        """Remove a URL input field."""
        if len(self._url_entries) > 1:
            row.pack_forget()
            self._url_entries = [(r, e) for r, e in self._url_entries if r != row]
            self._url_count_label.configure(text=f"{len(self._url_entries)} URLs")
        else:
            entry.delete(0, tk.END)

    def _load_and_analyze(self) -> None:
        """Load text content based on selected input type."""
        tipo = self._input_type.get()

        try:
            from tools.text_tool.processor import (
                extract_text_from_file,
                extract_text_from_url,
            )

            if tipo == "text":
                self._load_text_input()
            elif tipo == "files":
                self._load_files()
            elif tipo == "url":
                self._load_urls()
        except ImportError as e:
            self.update_status(
                "Instala dependencias: pip install wordcloud nltk pdfplumber requests beautifulsoup4",
                "red",
            )
            logger.error(f"Import error: {e}")

    def _load_text_input(self) -> None:
        """Load text from text input area."""
        text = self._text_area.get("1.0", tk.END).strip()
        if not text:
            self.update_status("Ingresá texto", "orange")
            return

        self.update_status(f"Procesando texto...", "yellow")
        self._parent.update()

        if self.state.text_content:
            self.state.text_content += "\n\n" + text
        else:
            self.state.update_text(text)

        self.state.sources["text"].append(text[:100])
        self.state.update_cleaned(clean_text(self.state.text_content, remove_stopwords=True))
        self._callbacks.emit_text_changed()
        self.update_status(
            f"Texto cargado: {len(self.state.text_content)} caracteres", "green"
        )

    def _load_files(self) -> None:
        """Load text from files."""
        files = filedialog.askopenfilenames(
            title="Seleccionar archivos",
            filetypes=[
                ("Documentos", "*.pdf *.docx *.doc"),
                ("Texto", "*.txt *.md"),
                ("Todos", "*.*"),
            ],
        )
        if not files:
            self.update_status("Seleccioná archivos", "orange")
            return

        self.update_status(f"Procesando {len(files)} archivos...", "yellow")
        self._parent.update()  # Forzar update de UI antes del trabajo pesado

        try:
            from tools.text_tool.processor import extract_text_from_file

            all_text = []
            for f in files:
                result = extract_text_from_file(f)
                if result.get("success"):
                    all_text.append(result["text"])

            new_text = "\n\n".join(all_text)
            if self.state.text_content:
                self.state.text_content += "\n\n" + new_text
            else:
                self.state.update_text(new_text)

            self.state.sources["files"].extend(files)
            self.state.update_cleaned(clean_text(self.state.text_content, remove_stopwords=True))
            self._callbacks.emit_text_changed()
            self.update_status(
                f"{len(files)} archivos: {len(self.state.text_content)} caracteres", "green"
            )
            self.refresh()
        except Exception as e:
            self.update_status(f"Error: {e}", "red")

    def _load_urls(self) -> None:
        """Load text from URLs."""
        urls = [e.get().strip() for _, e in self._url_entries if e.get().strip()]
        if not urls:
            self.update_status("Agregá al menos una URL", "orange")
            return

        logger.info(f"URL SCRAPER: Found {len(urls)} URLs to process: {urls}")
        self.update_status(f"Procesando {len(urls)} URLs...", "yellow")
        self._parent.update()

        try:
            from tools.text_tool.processor import extract_text_from_url

            all_text = []
            failed = []
            for idx, url in enumerate(urls, 1):
                logger.info(f"URL SCRAPER: Processing {idx}/{len(urls)}: {url}")
                self.update_status(f"Procesando {idx}/{len(urls)}: {url[:30]}...", "yellow")

                try:
                    result = extract_text_from_url(url)
                    if result.get("success"):
                        all_text.append(result["text"])
                        logger.info(f"URL SCRAPER: Success - {len(result['text'])} chars from {url}")
                    else:
                        failed.append(url)
                        logger.warning(f"URL SCRAPER: Failed - {result.get('error')} for {url}")
                except Exception as e:
                    failed.append(url)
                    logger.error(f"URL SCRAPER: Error - {e} for {url}")

            new_text = "\n\n".join(all_text)
            logger.info(f"URL SCRAPER: Total collected {len(new_text)} chars")

            if self.state.text_content:
                self.state.text_content += "\n\n" + new_text
            else:
                self.state.update_text(new_text)

            self.state.sources["urls"].extend(urls)
            self.state.update_cleaned(clean_text(self.state.text_content, remove_stopwords=True))
            self._callbacks.emit_text_changed()
            if failed:
                self.update_status(
                    f"{len(all_text)}/{len(urls)} URLs: {len(self.state.text_content)} chars ({len(failed)} fallidas)", "orange"
                )
            else:
                self.update_status(
                    f"{len(urls)} URLs: {len(self.state.text_content)} caracteres", "green"
                )
            logger.info(f"URL SCRAPER: Done - final text_content is {len(self.state.text_content)} chars")
        except Exception as e:
            self.update_status(f"Error: {e}", "red")

    def _on_paste(self, event=None) -> str:
        """Handle Ctrl+V paste."""
        try:
            clipboard_text = self._text_area.clipboard_get()
            if clipboard_text and clipboard_text.strip():
                self._text_area.insert(tk.INSERT, clipboard_text)
                self.update_status(f"Pegado: {len(clipboard_text)} caracteres", "green")
        except tk.TclError:
            self.update_status("Clipboard vacío o no texto", "orange")
        return "break"

    def _on_open_file(self, event=None) -> str:
        """Handle Ctrl+O to open file dialog."""
        files = filedialog.askopenfilenames(
            title="Seleccionar archivos",
            filetypes=[
                ("Texto", "*.txt *.md"),
                ("Documentos", "*.pdf *.docx *.doc"),
                ("Todos", "*.*"),
            ],
        )
        if files:
            self._load_files()
        return "break"

    def _on_save_file(self, event=None) -> str:
        """Handle Ctrl+S to save current text."""
        text_to_save = self.state.cleaned_content or self.state.text_content
        if not text_to_save:
            self.update_status("No hay texto para guardar", "orange")
            return "break"

        file_path = filedialog.asksaveasfilename(
            title="Guardar archivo",
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt"), ("Markdown", "*.md"), ("Todos", "*.*")],
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text_to_save)
                self.update_status(
                    f"Guardado: {len(text_to_save)} caracteres", "green"
                )
            except Exception as e:
                logger.error(f"Error guardando archivo: {e}")
                self.update_status(f"Error al guardar: {e}", "red")

        return "break"

    def _update_files_display(self) -> None:
        """Update the files label display."""
        if not self._files_label:
            return

        files = self.state.sources.get("files", [])
        if not files:
            self._files_label.configure(
                text="No hay archivos seleccionados", text_color="gray"
            )
            return

        file_names = [f.split("/")[-1].split("\\")[-1] for f in files]

        if len(file_names) <= 5:
            text = "📄 " + " • ".join(file_names)
        else:
            text = f"📄 {len(file_names)} archivos:\n• " + "\n• ".join(file_names[:5])
            if len(file_names) > 5:
                text += f"\n... y {len(file_names) - 5} más"

        self._files_label.configure(text=text, text_color="white")