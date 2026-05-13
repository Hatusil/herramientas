"""
Edit Meta Tab - Edición de metadatos.

Funciones:
- setup_tab: configura la UI del tab
- edit_metadata: ejecuta la edición
"""

import customtkinter as ctk
from core.constants import font
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.audio_tool.ui.main_ui import AudioToolUI


def setup_tab(ui: 'AudioToolUI') -> None:
    """Configura el tab de Editar Metadatos."""
    frame = ui.tab_edit_meta

    ctk.CTkLabel(frame, text="Editar metadatos (t\u00edtulo, artista, \u00e1lbum, g\u00e9nero...)",
                  font=font("normal", "bold")).pack(pady=10)

    container = ctk.CTkFrame(frame)
    container.pack(fill="both", expand=True, padx=20, pady=10)

    fields = [
        ("title", "T\u00edtulo:"),
        ("artist", "Artista:"),
        ("album", "\u00c1lbum:"),
        ("genre", "G\u00e9nero:"),
        ("year", "A\u00f1o:"),
        ("track", "Pista:"),
        ("comment", "Comentario:"),
        ("composer", "Compositor:"),
    ]

    ui.meta_vars = {}
    for i, (key, label) in enumerate(fields):
        row = i // 2
        col = (i % 2) * 2
        ctk.CTkLabel(container, text=label).grid(row=row, column=col, padx=5, pady=5, sticky="e")
        var = ctk.StringVar()
        ui.meta_vars[key] = var
        ctk.CTkEntry(container, textvariable=var, width=180).grid(row=row, column=col + 1, padx=5, pady=5, sticky="w")

    ctk.CTkButton(container, text="\u270F\ufe0f Editar Metadatos", command=lambda: ui._edit_metadata(),
                   height=40, font=font("small")).grid(row=4, column=0, columnspan=4, pady=20)


def edit_metadata(ui: 'AudioToolUI') -> None:
    """Edita los metadatos del audio."""
    if not ui._check_files():
        return
    
    options = {k: v.get() for k, v in ui.meta_vars.items() if v.get().strip()}
    if not options:
        ui.status_label.configure(text="Ingresa al menos un campo", text_color="#FFA500")
        return
    
    ui.status_label.configure(text="🔄 Editando metadatos...", text_color="#FFD700")
    ui.process_async("edit_metadata", ui.files, options)