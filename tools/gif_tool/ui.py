"""UI: Interfaz para crear GIFs animados."""
from ui.radiobutton import RadioButton
import customtkinter as ctk
import tkinter as tk
from pathlib import Path
from typing import Callable
from core.base_tool_ui import BaseToolUI
from core.tool_builder import create_standard_tool_ui


class GifToolUI(BaseToolUI):
    """UI para crear GIFs animados."""

    def __init__(self, master, on_process: Callable, **kwargs):
        super().__init__(master, on_process, **kwargs)
        self.is_processing = False

    def _setup_ui(self):
        r = create_standard_tool_ui(
            self, ("\U0001F39E\ufe0f", "Creador de GIFs"),
            "",  # description moved to help_config
            selector_type="file",
            file_types=[
                ("Imágenes", "*.png *.jpg *.jpeg *.bmp *.webp *.gif"),
                ("Todos", "*.*"),
            ],
            help_config={
                "description": "🎞️ Crea GIFs animados de secuencias de imágenes con control de duración y repeticiones",
                "file_label": "Imágenes para el GIF (orden importa):",
                "usage": [
                    "1. 📥 Agregar imágenes en orden de animación",
                    "2. ↕️ Reordenar frames si es necesario (↑↓)",
                    "3. ⏱️ Configurar duración (100-1000ms por frame)",
                    "4. 🔁 Elegir repeticiones (infinito/1/3)",
                    "5. ▶️ Click en 'Crear GIF'",
                ],
                "tips": [
                    "💡 Necesitás al menos 2 imágenes para crear un GIF",
                    "💡 Todas las imágenes deben tener el mismo tamaño",
                    "💡 Usá el botón 'Crear GIF' en la pestaña correspondiente",
                ],
                "warnings": [
                    "⚠️ Se necesitan al menos 2 imágenes",
                    "⚠️ Todas las imágenes deben tener mismo tamaño",
                    "⚠️ GIFs ilimitados pueden ser muy grandes",
                ],
            },
        )
        self.files = r["files"]
        self.file_listbox = r["listbox"]
        self.status_label = r["status_label"]

        self._move_up = self._make_move(-1)
        self._move_down = self._make_move(1)

        ctk.CTkButton(
            r.get("btn_frame"), text="Ordenar \u2191",
            command=self._move_up, width=70
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            r.get("btn_frame"), text="Ordenar \u2193",
            command=self._move_down, width=70
        ).pack(side="left", padx=2)

        self._setup_options()

    def _make_move(self, direction):
        def _move():
            sel = self.file_listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            new_idx = idx + direction
            if new_idx < 0 or new_idx >= len(self.files):
                return
            self.files[idx], self.files[new_idx] = self.files[new_idx], self.files[idx]
            self.file_listbox.delete(0, tk.END)
            for f in self.files:
                self.file_listbox.insert(tk.END, Path(f).name)
            self.file_listbox.selection_set(new_idx)
        return _move

    def _setup_options(self) -> None:
        opts_frame = ctk.CTkFrame(self)
        opts_frame.pack(fill="x", padx=10, pady=5)

        dur_frame = ctk.CTkFrame(opts_frame)
        dur_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(dur_frame, text="Duraci\u00f3n por frame (ms):").pack(side="left", padx=5)
        self.duration_var = ctk.StringVar(value="500")

        for val, label in [("100", "100ms (r\u00e1pido)"), ("200", "200ms"), ("500", "500ms (normal)"), ("1000", "1s (lento)")]:
            RadioButton(dur_frame, text=label, variable=self.duration_var, value=val).pack(side="left", padx=5)

        loop_frame = ctk.CTkFrame(opts_frame)
        loop_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(loop_frame, text="Repeticiones:").pack(side="left", padx=5)
        self.loop_var = ctk.StringVar(value="0")

        RadioButton(loop_frame, text="Infinito", variable=self.loop_var, value="0").pack(side="left", padx=5)
        RadioButton(loop_frame, text="1 vez", variable=self.loop_var, value="1").pack(side="left", padx=5)
        RadioButton(loop_frame, text="3 veces", variable=self.loop_var, value="3").pack(side="left", padx=5)

        ctk.CTkButton(
            self, text="\U0001F3AC Crear GIF", command=self._create_gif,
            height=40, font=ctk.CTkFont(size=14)
        ).pack(pady=10)

        self.info_text = ctk.CTkTextbox(self, width=400, height=100)
        self.info_text.pack(padx=10, pady=10)

    def _create_gif(self) -> None:
        if not self._check_files() or len(self.files) < 2:
            self.status_label.configure(text="Necesitas al menos 2 im\u00e1genes", text_color="#FFA500")
            return

        duration = int(self.duration_var.get())
        loop = int(self.loop_var.get())

        self.status_label.configure(text="Creando GIF...", text_color="#FFD700")

        from tools.gif_tool.processor import create_gif
        result = create_gif(self.files, duration=duration, loop=loop)

        if result["success"]:
            self.status_label.configure(text=result["message"], text_color="green")
            self.info_text.delete("1.0", tk.END)
            self.info_text.insert("1.0", f"\u2705 GIF creado exitosamente!\n\nArchivos: {len(self.files)}\nDuraci\u00f3n: {duration}ms por frame\nLoop: {'infinito' if loop == 0 else loop}")
        else:
            self.status_label.configure(text=result.get("error", "Error"), text_color="red")
