"""
Normalize Tab - Normalización de volumen.

Funciones:
- setup_tab: configura la UI del tab
- normalize: ejecuta la normalización
"""

import customtkinter as ctk
from core.constants import font
from core.tool_builder import create_radiobutton as RadioButton
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.audio_tool.ui.main_ui import AudioToolUI


def setup_tab(ui: 'AudioToolUI') -> None:
    """Configura el tab de Normalizar."""
    frame = ui.tab_normalize

    ctk.CTkLabel(frame, text="Normalizar volumen del audio", font=font("normal", "bold")).pack(pady=10)

    lufs_frame = ctk.CTkFrame(frame)
    lufs_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(lufs_frame, text="Target LUFS:").pack(side="left", padx=5)
    ui.lufs_var = ctk.StringVar(value="-16")

    rb_font = font("small")
    for val, label in [("-20", "Muy bajo (-20)"), ("-16", "Est\u00e1ndar (-16)"),
                       ("-14", "Alto (-14)"), ("-12", "Muy alto (-12)")]:
        RadioButton(lufs_frame, text=label, variable=ui.lufs_var, value=val, font=rb_font).pack(side="left", padx=5)

    opts_frame = ctk.CTkFrame(frame)
    opts_frame.pack(fill="x", padx=10, pady=5)

    ui.limit_var = ctk.BooleanVar(value=True)
    ctk.CTkCheckBox(opts_frame, text="Aplicar limitador (evita clipping)", variable=ui.limit_var).pack(anchor="w", padx=20)

    quality_frame = ctk.CTkFrame(frame)
    quality_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(quality_frame, text="Calidad MP3:").pack(side="left", padx=5)
    ui.quality_var = ctk.StringVar(value="192")

    for val in ["128", "192", "256", "320"]:
        RadioButton(quality_frame, text=f"{val} kbps", variable=ui.quality_var, value=val).pack(side="left", padx=5)

    sample_frame = ctk.CTkFrame(frame)
    sample_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(sample_frame, text="Remuestreo:").pack(side="left", padx=5)
    ui.sample_var = ctk.StringVar(value="0")

    RadioButton(sample_frame, text="Mantener original", variable=ui.sample_var, value="0").pack(side="left", padx=5)
    for val in ["44100", "48000"]:
        RadioButton(sample_frame, text=f"{val} Hz", variable=ui.sample_var, value=val).pack(side="left", padx=5)

    ui.btn_normalize = ctk.CTkButton(
        frame, text="\U0001F39A\ufe0f Normalizar Volumen", command=lambda: ui._normalize(),
        height=40, font=font("small")
    )
    ui.btn_normalize.pack(pady=20)


def normalize(ui: 'AudioToolUI') -> None:
    """Normaliza el volumen del audio."""
    if not ui._check_files():
        return
    
    ui.status_label.configure(text="🔄 Normalizando...", text_color="#FFD700")
    options = {
        "target_lufs": int(ui.lufs_var.get()),
        "limit_clipping": ui.limit_var.get(),
        "quality": int(ui.quality_var.get()),
    }
    sample = ui.sample_var.get()
    if sample != "0":
        options["sample_rate"] = int(sample)
    ui.process_async("normalize", ui.files, options)