"""
Info Tab - Información del archivo de audio.

Funciones:
- setup_tab: configura la UI del tab
- show_info: muestra información del archivo
"""

import tkinter as tk
import customtkinter as ctk
from pathlib import Path
from core.constants import font, COLORS
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.audio_tool.ui.main_ui import AudioToolUI


def setup_tab(ui: 'AudioToolUI') -> None:
    """Configura el tab de Info."""
    frame = ui.tab_info

    ctk.CTkLabel(frame, text="Informaci\u00f3n del archivo de audio:", font=font("normal", "bold")).pack(pady=10)

    ui.info_text = ctk.CTkTextbox(frame, width=500, height=300, wrap="word", fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"])
    ui.info_text.pack(padx=10, pady=10)
    ui.info_text.configure(state="disabled")

    ctk.CTkButton(frame, text="\U0001F441\ufe0f Ver Informaci\u00f3n", command=lambda: ui._show_info()).pack(pady=5)


def show_info(ui: 'AudioToolUI') -> None:
    """Muestra información del audio."""
    selected = ui._get_selected_files()
    if not selected:
        ui.status_label.configure(text="Seleccion\u00e1 al menos un archivo", text_color="#FFA500")
        return

    ui.info_text.configure(state="normal")
    ui.info_text.delete("1.0", tk.END)

    all_info = []
    errors = []

    for file_path in selected:
        try:
            from tools.audio_tool.processor import get_audio_info
            info = get_audio_info(file_path)
            if info.get("success"):
                audio_info = f"""\U0001F4C4 {info.get('file_name', 'N/A')}
{'\u2500' * 35}
  \U0001F4BE Tama\u00f1o:      {info.get('file_size', 0) / 1024 / 1024:.2f} MB
  \u23f1\ufe0f Duraci\u00f3n:    {info.get('duration', 0):.1f} seg
  \U0001F4E6 Formato:    {info.get('format', 'N/A')}
  \U0001F50A Codec:      {info.get('codec', 'N/A')}
  \U0001F3B5 Muestreo:   {info.get('sample_rate', 0)} Hz
  \U0001F500 Canales:    {info.get('channels', 0)}
  \U0001F4CA Bitrate:    {info.get('bit_rate', 0) / 1000:.0f} kbps
  \U0001F4DD T\u00edtulo:     {info.get('title', 'N/A')}
  \U0001F464 Artista:    {info.get('artist', 'N/A')}
  \U0001F4C0 \u00c1lbum:      {info.get('album', 'N/A')}
  #\ufe0f\u20e3 Pista:      {info.get('track', 'N/A')}
  \U0001F4C5 A\u00f1o:        {info.get('year', 'N/A')}
  \U0001F3BC G\u00e9nero:     {info.get('genre', 'N/A')}"""
                all_info.append(audio_info)
            else:
                errors.append(f"{Path(file_path).name}: {info.get('error', 'Error')}")
        except Exception as e:
            errors.append(f"{Path(file_path).name}: {str(e)}")

    if all_info:
        ui.info_text.insert("1.0", "\n\n".join(all_info))
    if errors:
        if all_info:
            ui.info_text.insert(tk.END, f"\n\n\u26a0\ufe0f ERRORES:\n" + "\n".join(errors))
        else:
            ui.info_text.insert("1.0", "\u26a0\ufe0f ERRORES:\n" + "\n".join(errors))

    ui.info_text.configure(state="disabled")
    status = f"Mostrando {len(all_info)}/{len(selected)} archivos"
    ui.status_label.configure(text=status, text_color="green" if not errors else "#FFA500")