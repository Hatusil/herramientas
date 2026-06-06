"""File handlers for text_tool UI."""
from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Tuple

if TYPE_CHECKING:
    from tools.text_tool.ui.main_ui import TextAnalyzerUI


def on_open_file(ui: "TextAnalyzerUI", event: Any = None) -> str:
    """Open file dialog and load files."""
    from tkinter import filedialog
    files = filedialog.askopenfilenames(
        title="Seleccionar archivos",
        filetypes=[("Texto", "*.txt *.md"), ("Documentos", "*.pdf *.docx"), ("Todos", "*.*")]
    )
    if files:
        load_files(ui, files)
    return "break"


def on_save_file(ui: "TextAnalyzerUI", event: Any = None) -> str:
    """Save content to file."""
    from tkinter import filedialog
    text = ui.state.cleaned_content or ui.state.text_content
    if not text:
        ui._on_status("No hay texto para guardar", "orange")
        return "break"
    path = filedialog.asksaveasfilename(
        title="Guardar archivo",
        defaultextension=".txt",
        filetypes=[("Texto", "*.txt"), ("Markdown", "*.md"), ("Todos", "*.*")]
    )
    if path:
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)
            ui._on_status(f"Guardado: {os.path.basename(path)}", "green")
        except Exception as e:
            ui._on_status(f"Error al guardar: {e}", "red")
    return "break"


def load_files(ui: "TextAnalyzerUI", files: Tuple[str, ...]) -> None:
    """Load files and add to state."""
    try:
        from tools.text_tool.processor import extract_text_from_file
        for f in files:
            result = extract_text_from_file(f)
            if result.get('success'):
                ui.state.add_file_source(f, result.get('text', '') + "\n")
        ui.state.file_path = files[0] if files else None
        ui._on_text_changed()
        ui._on_status(f"{len(files)} archivos cargados", "green")
    except ImportError:
        ui._on_status("Instala dependencias: wordcloud nltk pdfplumber", "red")


def on_file_drop(ui: "TextAnalyzerUI", event: Any) -> str:
    """Handle file drop event."""
    files = ui.tk.splitlist(event.data) if hasattr(event, 'data') else ()
    if files:
        valid = [f for f in files if Path(f).suffix.lower() in {'.txt', '.md', '.pdf', '.docx', '.doc'}]
        if valid:
            load_files(ui, tuple(valid))
        elif files:
            ui._on_status("Tipo de archivo no soportado", "red")
    return "break"