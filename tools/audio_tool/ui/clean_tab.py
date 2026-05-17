"""
Clean Tab - Limpieza de metadatos.

Funciones:
- setup_tab: configura la UI del tab
- clean_metadata: ejecuta la limpieza
"""

import customtkinter as ctk
from core.constants import font, COLORS
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.audio_tool.ui.main_ui import AudioToolUI


def setup_tab(ui: 'AudioToolUI') -> None:
    """Configura el tab de Limpiar."""
    frame = ui.tab_clean

    ctk.CTkLabel(frame, text="Limpiar metadatos (ID3, t\u00edtulo, artista, etc.)", font=font("normal", "bold")).pack(pady=10)

    ctk.CTkLabel(frame, text="Esto eliminar\u00e1: t\u00edtulo, artista, \u00e1lbum, g\u00e9nero, a\u00f1o, etc.", text_color="gray").pack(pady=5)

    ctk.CTkButton(frame, text="\U0001F9F9 Limpiar Metadatos", command=lambda: ui._clean_metadata(),
                   height=40, font=font("small")).pack(pady=20)


def clean_metadata(ui: 'AudioToolUI') -> None:
    """Limpia los metadatos del audio."""
    if not ui._check_files():
        return
    
    ui.status_label.configure(text="🔄 Limpiando metadatos...", text_color=COLORS.get("warning"))
    ui.process_async("clean", ui.files, {})