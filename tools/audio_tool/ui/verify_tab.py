"""
Verify Tab - Verificación de integridad de archivos.

Funciones:
- setup_tab: configura la UI del tab
- verify_audio: ejecuta la verificación
"""

import tkinter as tk
import customtkinter as ctk
from core.constants import font, COLORS
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.audio_tool.ui.main_ui import AudioToolUI


def setup_tab(ui: 'AudioToolUI') -> None:
    """Configura el tab de Verificar."""
    frame = ui.tab_verify

    ctk.CTkLabel(frame, text="Verificar integridad de archivos de audio",
                  font=font("normal", "bold")).pack(pady=10)

    ctk.CTkLabel(frame, text="Verifica qu\u00e9 archivos est\u00e1n corruptos antes de repararlos",
                  text_color="gray").pack(pady=5)

    ui.verify_text = ctk.CTkTextbox(frame, width=500, height=280, wrap="word", fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"])
    ui.verify_text.pack(padx=10, pady=10)
    ui.verify_text.configure(state="disabled")

    ctk.CTkButton(frame, text="\U0001F50D Verificar Archivos", command=lambda: ui._verify_audio(),
                   height=40, font=font("small")).pack(pady=10)


def verify_audio(ui: 'AudioToolUI') -> None:
    """Verifica la integridad de los archivos."""
    selected = ui._get_selected_files()
    if not selected:
        ui.status_label.configure(text="Seleccion\u00e1 al menos un archivo", text_color="#FFA500")
        return

    ui.status_label.configure(text="Verificando archivos...", text_color="#FFD700")
    ui.update()

    try:
        from tools.audio_tool.processor import verify_multiple_audio
        result = verify_multiple_audio(selected)

        ui.verify_text.configure(state="normal")
        ui.verify_text.delete("1.0", tk.END)

        ok_files = [r for r in result["results"] if not r["corrupt"]]
        corrupt_files = [r for r in result["results"] if r["corrupt"]]

        if ok_files:
            ui.verify_text.insert("1.0", f"\u2705 ARCHIVOS OK ({len(ok_files)}):\n")
            for r in ok_files:
                ui.verify_text.insert(tk.END, f"  \u2713 {r['name']}\n")

        if corrupt_files:
            if ok_files:
                ui.verify_text.insert(tk.END, "\n")
            ui.verify_text.insert(tk.END, f"\u274c ARCHIVOS CORRUPTOS ({len(corrupt_files)}):\n")
            for r in corrupt_files:
                ui.verify_text.insert(tk.END, f"  \u2717 {r['name']} - {r['message']}\n")

        divider = "\u2500" * 35
        ui.verify_text.insert(tk.END, f"\n{divider}\n")
        ui.verify_text.insert(tk.END, f"Total: {result['total']} | OK: {result['ok']} | Corruptos: {result['corrupt']}")
        ui.verify_text.configure(state="disabled")

        if result["corrupt"] == 0:
            ui.status_label.configure(text=f"Todos OK ({result['ok']} archivos)", text_color="green")
        else:
            ui.status_label.configure(text=f"{result['ok']} OK, {result['corrupt']} corruptos", text_color="#FFA500")
    except Exception as e:
        ui.status_label.configure(text=f"Error: {str(e)}", text_color="red")