"""
Keyboard shortcuts para TextAnalyzerUI.
Separado de main_ui.py por SRP (máxima R0: clases <300 líneas).
"""
import logging
import os
import tkinter as tk
from tkinter import filedialog
from typing import Any, Callable

logger = logging.getLogger(__name__)

# Key bindings configuration
KEY_BINDINGS = [
    ('<Control-v>', 'paste', 'Pegar desde clipboard'),
    ('<Control-o>', 'open', 'Abrir archivo'),
    ('<Control-s>', 'save', 'Guardar archivo'),
    ('<Control-Return>', 'run', 'Ejecutar análisis'),
    ('<Escape>', 'cancel', 'Cancelar análisis'),
]


def setup_shortcuts(ui: Any, handlers: dict) -> None:
    """Configura los keyboard shortcuts."""
    bindings = [
        ('<Control-v>', handlers.get('on_paste')),
        ('<Control-o>', handlers.get('on_open')),
        ('<Control-s>', handlers.get('on_save')),
        ('<Control-Return>', handlers.get('on_run')),
        ('<Escape>', handlers.get('on_cancel')),
    ]
    for key, handler in bindings:
        if handler:
            ui.bind(key, handler)


def handle_paste(ui: Any, event: Any = None) -> str:
    """Handle Ctrl+V."""
    try:
        text = ui.clipboard_get()
        if text and text.strip():
            ui.state.update_text(text)
            ui._on_status(f"Pegado: {len(text)} caracteres", "green")
    except tk.TclError:
        ui._on_status("Clipboard vacío", "orange")
    return "break"


def handle_open(ui: Any, event: Any = None) -> str:
    """Handle Ctrl+O."""
    files = filedialog.askopenfilenames(
        title="Seleccionar archivos",
        filetypes=[("Texto", "*.txt *.md"), ("Documentos", "*.pdf *.docx"), ("Todos", "*.*")]
    )
    if files:
        ui._load_files(files)
    return "break"


def handle_save(ui: Any, event: Any = None) -> str:
    """Handle Ctrl+S."""
    text = ui.state.cleaned_content or ui.state.text_content
    if not text:
        ui._on_status("No hay texto para guardar", "orange")
        return "break"

    path = filedialog.asksaveasfilename(
        title="Guardar archivo", defaultextension=".txt",
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


def handle_run(ui: Any, event: Any = None) -> str:
    """Handle Ctrl+Enter."""
    ui._run_all_analysis()
    return "break"


def handle_cancel(ui: Any, event: Any = None) -> str:
    """Handle Escape."""
    if ui._is_processing:
        ui._is_processing = False
        from tools.text_tool.ui.threading_utils import _stop_progress
        _stop_progress(ui)
        ui._on_status("Análisis cancelado", "orange")
    return "break"