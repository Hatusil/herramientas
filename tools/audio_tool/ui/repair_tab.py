"""
Repair Tab - Reparación de archivos corruptos.

Funciones:
- setup_tab: configura la UI del tab
- verify_before_repair, do_repair
"""

import tkinter as tk
import customtkinter as ctk
from core.constants import font
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.audio_tool.ui.main_ui import AudioToolUI


def setup_tab(ui: 'AudioToolUI') -> None:
    """Configura el tab de Reparar."""
    frame = ui.tab_repair

    ctk.CTkLabel(frame, text="Reparar archivos de audio corruptos", font=font("normal", "bold")).pack(pady=10)

    ctk.CTkLabel(frame, text="Primero verific\u00e1 qu\u00e9 archivos est\u00e1n corruptos, luego decid\u00ed qu\u00e9 reparar",
                  text_color="gray").pack(pady=5)

    ui.repair_verify_text = ctk.CTkTextbox(frame, width=500, height=180, wrap="word")
    ui.repair_verify_text.pack(padx=10, pady=10)
    ui.repair_verify_text.configure(state="disabled")

    btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
    btn_frame.pack(pady=10)

    ctk.CTkButton(btn_frame, text="\U0001F50D Verificar", command=lambda: ui._verify_before_repair(),
                   height=35, width=120).pack(side="left", padx=3)

    ui.btn_repair_corrupt = ctk.CTkButton(
        btn_frame, text="\U0001F527 Solo Corruptos",
        command=lambda: ui._do_repair(mode="corrupt"),
        height=35, width=130, state="disabled"
    )
    ui.btn_repair_corrupt.pack(side="left", padx=3)

    ui.btn_repair_all = ctk.CTkButton(
        btn_frame, text="\U0001F527 Reparar Todos",
        command=lambda: ui._do_repair(mode="all"),
        height=35, width=130, state="disabled"
    )
    ui.btn_repair_all.pack(side="left", padx=3)

    ui.verify_state = {"ok": [], "corrupt": []}


def verify_before_repair(ui: 'AudioToolUI') -> None:
    """Verifica archivos antes de reparar."""
    selected = ui._get_selected_files()
    if not selected:
        ui.status_label.configure(text="Seleccion\u00e1 al menos un archivo", text_color="#FFA500")
        return

    ui.status_label.configure(text="Verificando...", text_color="#FFD700")
    ui.repair_verify_text.configure(state="normal")
    ui.repair_verify_text.delete("1.0", tk.END)
    ui.update()

    try:
        from tools.audio_tool.processor import verify_multiple_audio
        result = verify_multiple_audio(selected)

        ok_files = [r for r in result["results"] if not r["corrupt"]]
        corrupt_files = [r for r in result["results"] if r["corrupt"]]

        ui.verify_state = {"ok": [r["file"] for r in ok_files], "corrupt": [r["file"] for r in corrupt_files]}

        ui.repair_verify_text.insert("1.0", f"\U0001F4CA VERIFICACI\u00d3N:\n{'\u2500' * 35}\n")

        if ok_files:
            ui.repair_verify_text.insert(tk.END, f"\u2705 OK ({len(ok_files)}):\n")
            for r in ok_files:
                ui.repair_verify_text.insert(tk.END, f"  \u2713 {r['name']}\n")
            ui.repair_verify_text.insert(tk.END, "\n")

        if corrupt_files:
            ui.repair_verify_text.insert(tk.END, f"\u274c CORRUPTOS ({len(corrupt_files)}):\n")
            for r in corrupt_files:
                ui.repair_verify_text.insert(tk.END, f"  \u2717 {r['name']}\n")

        ui.repair_verify_text.insert(tk.END, f"\n{'\u2500' * 35}\nTotal: {result['total']} | OK: {result['ok']} | corruptos: {result['corrupt']}")
        ui.repair_verify_text.configure(state="disabled")

        if len(corrupt_files) > 0:
            ui.btn_repair_corrupt.configure(state="normal")
            ui.status_label.configure(text=f"{len(corrupt_files)} corruptos", text_color="#FFA500")
        else:
            ui.btn_repair_corrupt.configure(state="disabled")
            ui.status_label.configure(text="Todos OK", text_color="green")

        ui.btn_repair_all.configure(state="normal" if len(ok_files) > 0 else "disabled")
    except Exception as e:
        ui.status_label.configure(text=f"Error: {str(e)}", text_color="red")


def do_repair(ui: 'AudioToolUI', mode: str) -> None:
    """Repara archivos de audio."""
    if ui.is_processing:
        return
    if mode == "corrupt":
        files = ui.verify_state["corrupt"]
        if not files:
            return
    else:
        files = ui._get_selected_files()
    ui.is_processing = True
    ui.process_async("repair", files, {})