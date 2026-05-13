"""
Transcribe Tab - Transcripción de audio a texto usando OLMoASR.

Funciones:
- setup_tab: configura la UI del tab
- transcribe: ejecuta la transcripción
"""

import customtkinter as ctk
from core.constants import font
from core.tool_builder import create_radiobutton as RadioButton
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.audio_tool.ui.main_ui import AudioToolUI


def setup_tab(ui: 'AudioToolUI') -> None:
    """Configura el tab de Transcribir."""
    frame = ui.tab_transcribe

    ctk.CTkLabel(
        frame, text="Transcribir audio a texto",
        font=font("normal", "bold")
    ).pack(pady=10)

    ctk.CTkLabel(
        frame, text="Convierte voz en texto usando OLMoASR (AI2)",
        text_color="gray", font=font("small")
    ).pack(pady=5)

    # Selector de modelo
    model_frame = ctk.CTkFrame(frame)
    model_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(model_frame, text="Modelo:").pack(side="left", padx=5)
    ui.transcribe_model_var = ctk.StringVar(value="base")

    for model in [("tiny", "Tiny (39M, rápido)"), ("base", "Base (74M)"), ("small", "Small (244M)")]:
        RadioButton(
            model_frame, text=model[1], variable=ui.transcribe_model_var, value=model[0]
        ).pack(side="left", padx=10)

    # Output format
    out_frame = ctk.CTkFrame(frame)
    out_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(out_frame, text="Salida:").pack(side="left", padx=5)
    ui.transcribe_format_var = ctk.StringVar(value="txt")

    for fmt in [("txt", "Texto"), ("srt", "Subtítulos SRT"), ("vtt", "WebVTT")]:
        RadioButton(out_frame, text=fmt[1], variable=ui.transcribe_format_var, value=fmt[0]).pack(side="left", padx=10)

    # Botón
    ctk.CTkButton(
        frame, text="🎙️ Transcribir a Texto",
        command=lambda: ui._transcribe(),
        height=40, font=font("small")
    ).pack(pady=20)


def transcribe(ui: 'AudioToolUI') -> None:
    """Transcribe el audio a texto."""
    if not ui._check_files():
        return

    # Check dependencias
    try:
        import torch
        import transformers
        import librosa
    except ImportError:
        ui.status_label.configure(
            text="⚠️ Dependencias faltantes: pip install torch transformers librosa",
            text_color="orange"
        )
        return

    ui.status_label.configure(text="🔄 Transcribiendo...", text_color="#FFD700")
    ui.process_async("transcribe", ui.files, {
        "model": ui.transcribe_model_var.get(),
        "format": ui.transcribe_format_var.get(),
    })