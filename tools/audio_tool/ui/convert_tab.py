"""
Convert Tab - Conversión de formato.

Funciones:
- setup_tab: configura la UI del tab
- convert: ejecuta la conversión
"""

import customtkinter as ctk
from core.constants import font
from core.tool_builder import create_radiobutton as RadioButton
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.audio_tool.ui.main_ui import AudioToolUI


def setup_tab(ui: 'AudioToolUI') -> None:
    """Configura el tab de Convertir."""
    frame = ui.tab_convert

    ctk.CTkLabel(frame, text="Convertir a otro formato de audio", font=font("normal", "bold")).pack(pady=10)

    format_frame = ctk.CTkFrame(frame)
    format_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(format_frame, text="Formato de salida:").pack(side="left", padx=5)
    ui.format_var = ctk.StringVar(value="mp3")

    for fmt in ["mp3", "wav", "flac", "ogg"]:
        RadioButton(format_frame, text=fmt.upper(), variable=ui.format_var, value=fmt).pack(side="left", padx=10)

    quality_frame = ctk.CTkFrame(frame)
    quality_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(quality_frame, text="Calidad:").pack(side="left", padx=5)
    ui.conv_quality_var = ctk.StringVar(value="192")

    for val in ["128", "192", "256", "320"]:
        RadioButton(quality_frame, text=f"{val} kbps", variable=ui.conv_quality_var, value=val).pack(side="left", padx=5)

    ctk.CTkLabel(frame, text="Nota: WAV y FLAC usan calidad sin p\u00e9rdida",
                  text_color="gray", font=font("small")).pack(pady=5)

    ctk.CTkButton(frame, text="\U0001F504 Convertir Formato", command=ui._convert,
                   height=40, font=font("small")).pack(pady=20)


def convert(ui: 'AudioToolUI') -> None:
    """Convierte el formato del audio."""
    check = ui._check_files()
    if not check:
        return
    
    ui.status_label.configure(text="🔄 Convirtiendo formato...", text_color="#FFD700")
    ui.process_async("convert", ui.files, {
        "format": ui.format_var.get(),
        "quality": int(ui.conv_quality_var.get()),
    })