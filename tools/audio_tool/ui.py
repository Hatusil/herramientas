"""UI: Interfaz de usuario para la herramienta de audio."""
import os
import logging
from core.help_panel import add_help
from ui.radiobutton import RadioButton
import customtkinter as ctk
import tkinter as tk
from pathlib import Path
from typing import List, Callable, Dict, Any
from core.base_tool_ui import BaseToolUI
from core.tool_builder import create_standard_tool_ui
from core.constants import font

logger = logging.getLogger(__name__)


class AudioToolUI(BaseToolUI):
    """UI para procesamiento de archivos de audio."""

    def __init__(self, master, on_process: Callable, **kwargs):
        super().__init__(master, on_process, **kwargs)
        self.is_processing = False
        self._setup_progress_bar()

    def _setup_ui(self):
        r = create_standard_tool_ui(
            self, ("\U0001F3B5", "Procesamiento de Audio"),
            "\U0001F3B5 Procesa audio MP3/WAV/FLAC/OGG/M4A: normaliza volumen, limpia metadatos ID3, convierte formato, repara archivos, muestra info",
            selector_type="file",
            tab_configs=[
                {"name": "Normalizar"}, {"name": "Limpiar"},
                {"name": "Editar Metadatos"}, {"name": "Convertir"},
                {"name": "Reparar"}, {"name": "Info"}, {"name": "Verificar"},
            ],
            file_types=[
                ("Audio files", "*.mp3 *.wav *.flac *.ogg *.m4a *.aac"),
                ("MP3", "*.mp3"),
                ("Todos", "*.*"),
            ],
            help_config={
                "file_label": "Archivos de audio:",
                "usage": [
                    "1. \U0001F4E5 Agregar archivos (+)",
                    "2. \u2611\ufe0f Seleccionar con Ctrl+click o botones 'Todos'/'Ninguno'",
                    "3. \U0001F4D1 Elegir operaci\u00f3n (Normalizar/Limpiar/Convertir/Reparar/Info)",
                    "4. \u2699\ufe0f Configurar opciones LUFS o calidad (192k default)",
                    "5. \u25b6\ufe0f Click en ejecutar (procesa solo los seleccionados)",
                ],
                "warnings": [
                    "\u26a0\ufe0f mp3\u2192mp3 con calidad 192k se omite (ya en formato)",
                    "\u26a0\ufe0f Cambiar calidad para forzar conversi\u00f3n",
                    "\u26a0\ufe0f Normalizaci\u00f3n alta puede afectar calidad",
                    "\u26a0\ufe0f Conversi\u00f3n siempre crea nuevo archivo",
                    "\u26a0\ufe0f Reparar archivos severos puede dejar artefactos",
                ],
            },
        )
        self.files = r["files"]
        self.file_listbox = r["listbox"]
        self.status_label = r["status_label"]
        self.tab_normalize = r["tabs"]["Normalizar"]
        self.tab_clean = r["tabs"]["Limpiar"]
        self.tab_edit_meta = r["tabs"]["Editar Metadatos"]
        self.tab_convert = r["tabs"]["Convertir"]
        self.tab_repair = r["tabs"]["Reparar"]
        self.tab_info = r["tabs"]["Info"]
        self.tab_verify = r["tabs"]["Verificar"]

        self._setup_normalize_tab()
        self._setup_clean_tab()
        self._setup_edit_meta_tab()
        self._setup_convert_tab()
        self._setup_repair_tab()
        self._setup_info_tab()
        self._setup_verify_tab()

    def _setup_normalize_tab(self) -> None:
        frame = self.tab_normalize

        ctk.CTkLabel(frame, text="Normalizar volumen del audio", font=font("normal", "bold")).pack(pady=10)

        lufs_frame = ctk.CTkFrame(frame)
        lufs_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(lufs_frame, text="Target LUFS:").pack(side="left", padx=5)
        self.lufs_var = ctk.StringVar(value="-16")

        rb_font = font("small")
        for val, label in [("-20", "Muy bajo (-20)"), ("-16", "Est\u00e1ndar (-16)"),
                           ("-14", "Alto (-14)"), ("-12", "Muy alto (-12)")]:
            RadioButton(lufs_frame, text=label, variable=self.lufs_var, value=val, font=rb_font).pack(side="left", padx=5)

        opts_frame = ctk.CTkFrame(frame)
        opts_frame.pack(fill="x", padx=10, pady=5)

        self.limit_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(opts_frame, text="Aplicar limitador (evita clipping)", variable=self.limit_var).pack(anchor="w", padx=20)

        quality_frame = ctk.CTkFrame(frame)
        quality_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(quality_frame, text="Calidad MP3:").pack(side="left", padx=5)
        self.quality_var = ctk.StringVar(value="192")

        for val in ["128", "192", "256", "320"]:
            RadioButton(quality_frame, text=f"{val} kbps", variable=self.quality_var, value=val).pack(side="left", padx=5)

        sample_frame = ctk.CTkFrame(frame)
        sample_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(sample_frame, text="Remuestreo:").pack(side="left", padx=5)
        self.sample_var = ctk.StringVar(value="0")

        RadioButton(sample_frame, text="Mantener original", variable=self.sample_var, value="0").pack(side="left", padx=5)
        for val in ["44100", "48000"]:
            RadioButton(sample_frame, text=f"{val} Hz", variable=self.sample_var, value=val).pack(side="left", padx=5)

        self.btn_normalize = ctk.CTkButton(
            frame, text="\U0001F39A\ufe0f Normalizar Volumen", command=self._normalize,
            height=40, font=font("small")
        )
        self.btn_normalize.pack(pady=20)

    def _normalize(self) -> None:
        if self.is_processing:
            return
        if not self._check_files():
            return
        self.is_processing = True
        options = {
            "target_lufs": int(self.lufs_var.get()),
            "limit_clipping": self.limit_var.get(),
            "quality": int(self.quality_var.get()),
        }
        sample = self.sample_var.get()
        if sample != "0":
            options["sample_rate"] = int(sample)
        self.process_async("normalize", self.files, options)

    def _setup_clean_tab(self) -> None:
        frame = self.tab_clean

        ctk.CTkLabel(frame, text="Limpiar metadatos (ID3, t\u00edtulo, artista, etc.)", font=font("normal", "bold")).pack(pady=10)

        ctk.CTkLabel(frame, text="Esto eliminar\u00e1: t\u00edtulo, artista, \u00e1lbum, g\u00e9nero, a\u00f1o, etc.", text_color="gray").pack(pady=5)

        ctk.CTkButton(frame, text="\U0001F9F9 Limpiar Metadatos", command=self._clean_metadata,
                       height=40, font=font("small")).pack(pady=20)

    def _clean_metadata(self) -> None:
        if self.is_processing:
            return
        if not self._check_files():
            return
        self.is_processing = True
        self.process_async("clean", self.files, {})

    def _setup_edit_meta_tab(self) -> None:
        frame = self.tab_edit_meta

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

        self.meta_vars = {}
        for i, (key, label) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            ctk.CTkLabel(container, text=label).grid(row=row, column=col, padx=5, pady=5, sticky="e")
            var = ctk.StringVar()
            self.meta_vars[key] = var
            ctk.CTkEntry(container, textvariable=var, width=180).grid(row=row, column=col + 1, padx=5, pady=5, sticky="w")

        ctk.CTkButton(container, text="\u270F\ufe0f Editar Metadatos", command=self._edit_metadata,
                       height=40, font=font("small")).grid(row=4, column=0, columnspan=4, pady=20)

    def _edit_metadata(self) -> None:
        if self.is_processing:
            return
        if not self._check_files():
            return
        options = {k: v.get() for k, v in self.meta_vars.items() if v.get().strip()}
        if not options:
            self.status_label.configure(text="Ingresa al menos un campo", text_color="#FFA500")
            return
        self.is_processing = True
        self.process_async("edit_metadata", self.files, options)

    def _setup_convert_tab(self) -> None:
        frame = self.tab_convert

        ctk.CTkLabel(frame, text="Convertir a otro formato de audio", font=font("normal", "bold")).pack(pady=10)

        format_frame = ctk.CTkFrame(frame)
        format_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(format_frame, text="Formato de salida:").pack(side="left", padx=5)
        self.format_var = ctk.StringVar(value="mp3")

        for fmt in ["mp3", "wav", "flac", "ogg"]:
            RadioButton(format_frame, text=fmt.upper(), variable=self.format_var, value=fmt).pack(side="left", padx=10)

        quality_frame = ctk.CTkFrame(frame)
        quality_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(quality_frame, text="Calidad:").pack(side="left", padx=5)
        self.conv_quality_var = ctk.StringVar(value="192")

        for val in ["128", "192", "256", "320"]:
            RadioButton(quality_frame, text=f"{val} kbps", variable=self.conv_quality_var, value=val).pack(side="left", padx=5)

        ctk.CTkLabel(frame, text="Nota: WAV y FLAC usan calidad sin p\u00e9rdida",
                      text_color="gray", font=font("small")).pack(pady=5)

        ctk.CTkButton(frame, text="\U0001F504 Convertir Formato", command=self._convert,
                       height=40, font=font("small")).pack(pady=20)

    def _convert(self) -> None:
        if self.is_processing:
            return
        if not self._check_files():
            return
        self.is_processing = True
        self.process_async("convert", self.files, {
            "format": self.format_var.get(),
            "quality": int(self.conv_quality_var.get()),
        })

    def _setup_repair_tab(self) -> None:
        frame = self.tab_repair

        ctk.CTkLabel(frame, text="Reparar archivos de audio corruptos", font=font("normal", "bold")).pack(pady=10)

        ctk.CTkLabel(frame, text="Primero verific\u00e1 qu\u00e9 archivos est\u00e1n corruptos, luego decid\u00ed qu\u00e9 reparar",
                      text_color="gray").pack(pady=5)

        self.repair_verify_text = ctk.CTkTextbox(frame, width=500, height=180, wrap="word")
        self.repair_verify_text.pack(padx=10, pady=10)
        self.repair_verify_text.configure(state="disabled")

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="\U0001F50D Verificar", command=self._verify_before_repair,
                       height=35, width=120).pack(side="left", padx=3)

        self.btn_repair_corrupt = ctk.CTkButton(
            btn_frame, text="\U0001F527 Solo Corruptos",
            command=lambda: self._do_repair(mode="corrupt"),
            height=35, width=130, state="disabled"
        )
        self.btn_repair_corrupt.pack(side="left", padx=3)

        self.btn_repair_all = ctk.CTkButton(
            btn_frame, text="\U0001F527 Reparar Todos",
            command=lambda: self._do_repair(mode="all"),
            height=35, width=130, state="disabled"
        )
        self.btn_repair_all.pack(side="left", padx=3)

        self.verify_state = {"ok": [], "corrupt": []}

    def _verify_before_repair(self) -> None:
        selected = self._get_selected_files()
        if not selected:
            self.status_label.configure(text="Seleccion\u00e1 al menos un archivo", text_color="#FFA500")
            return

        self.status_label.configure(text="Verificando...", text_color="#FFD700")
        self.repair_verify_text.configure(state="normal")
        self.repair_verify_text.delete("1.0", tk.END)
        self.update()

        try:
            from tools.audio_tool.processor import verify_multiple_audio
            result = verify_multiple_audio(selected)

            ok_files = [r for r in result["results"] if not r["corrupt"]]
            corrupt_files = [r for r in result["results"] if r["corrupt"]]

            self.verify_state = {"ok": [r["file"] for r in ok_files], "corrupt": [r["file"] for r in corrupt_files]}

            self.repair_verify_text.insert("1.0", f"\U0001F4CA VERIFICACI\u00d3N:\n{'\u2500' * 35}\n")

            if ok_files:
                self.repair_verify_text.insert(tk.END, f"\u2705 OK ({len(ok_files)}):\n")
                for r in ok_files:
                    self.repair_verify_text.insert(tk.END, f"  \u2713 {r['name']}\n")
                self.repair_verify_text.insert(tk.END, "\n")

            if corrupt_files:
                self.repair_verify_text.insert(tk.END, f"\u274c CORRUPTOS ({len(corrupt_files)}):\n")
                for r in corrupt_files:
                    self.repair_verify_text.insert(tk.END, f"  \u2717 {r['name']}\n")

            self.repair_verify_text.insert(tk.END, f"\n{'\u2500' * 35}\nTotal: {result['total']} | OK: {result['ok']} | corruptos: {result['corrupt']}")
            self.repair_verify_text.configure(state="disabled")

            if len(corrupt_files) > 0:
                self.btn_repair_corrupt.configure(state="normal")
                self.status_label.configure(text=f"{len(corrupt_files)} corruptos", text_color="#FFA500")
            else:
                self.btn_repair_corrupt.configure(state="disabled")
                self.status_label.configure(text="Todos OK", text_color="green")

            self.btn_repair_all.configure(state="normal" if len(ok_files) > 0 else "disabled")
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")

    def _do_repair(self, mode: str) -> None:
        if self.is_processing:
            return
        if mode == "corrupt":
            files = self.verify_state["corrupt"]
            if not files:
                return
        else:
            files = self._get_selected_files()
        self.is_processing = True
        self.process_async("repair", files, {})

    def _setup_verify_tab(self) -> None:
        frame = self.tab_verify

        ctk.CTkLabel(frame, text="Verificar integridad de archivos de audio",
                      font=font("normal", "bold")).pack(pady=10)

        ctk.CTkLabel(frame, text="Verifica qu\u00e9 archivos est\u00e1n corruptos antes de repararlos",
                      text_color="gray").pack(pady=5)

        self.verify_text = ctk.CTkTextbox(frame, width=500, height=280, wrap="word")
        self.verify_text.pack(padx=10, pady=10)
        self.verify_text.configure(state="disabled")

        ctk.CTkButton(frame, text="\U0001F50D Verificar Archivos", command=self._verify_audio,
                       height=40, font=font("small")).pack(pady=10)

    def _verify_audio(self) -> None:
        selected = self._get_selected_files()
        if not selected:
            self.status_label.configure(text="Seleccion\u00e1 al menos un archivo", text_color="#FFA500")
            return

        self.status_label.configure(text="Verificando archivos...", text_color="#FFD700")
        self.update()

        try:
            from tools.audio_tool.processor import verify_multiple_audio
            result = verify_multiple_audio(selected)

            self.verify_text.configure(state="normal")
            self.verify_text.delete("1.0", tk.END)

            ok_files = [r for r in result["results"] if not r["corrupt"]]
            corrupt_files = [r for r in result["results"] if r["corrupt"]]

            if ok_files:
                self.verify_text.insert("1.0", f"\u2705 ARCHIVOS OK ({len(ok_files)}):\n")
                for r in ok_files:
                    self.verify_text.insert(tk.END, f"  \u2713 {r['name']}\n")

            if corrupt_files:
                if ok_files:
                    self.verify_text.insert(tk.END, "\n")
                self.verify_text.insert(tk.END, f"\u274c ARCHIVOS CORRUPTOS ({len(corrupt_files)}):\n")
                for r in corrupt_files:
                    self.verify_text.insert(tk.END, f"  \u2717 {r['name']} - {r['message']}\n")

            self.verify_text.insert(tk.END, f"\n{'\u2500' * 35}\n")
            self.verify_text.insert(tk.END, f"Total: {result['total']} | OK: {result['ok']} | Corruptos: {result['corrupt']}")
            self.verify_text.configure(state="disabled")

            if result["corrupt"] == 0:
                self.status_label.configure(text=f"Todos OK ({result['ok']} archivos)", text_color="green")
            else:
                self.status_label.configure(text=f"{result['ok']} OK, {result['corrupt']} corruptos", text_color="#FFA500")
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")

    def _setup_info_tab(self) -> None:
        frame = self.tab_info

        ctk.CTkLabel(frame, text="Informaci\u00f3n del archivo de audio:", font=font("normal", "bold")).pack(pady=10)

        self.info_text = ctk.CTkTextbox(frame, width=500, height=300, wrap="word")
        self.info_text.pack(padx=10, pady=10)
        self.info_text.configure(state="disabled")

        ctk.CTkButton(frame, text="\U0001F441\ufe0f Ver Informaci\u00f3n", command=self._show_info).pack(pady=5)

    def _show_info(self) -> None:
        selected = self._get_selected_files()
        if not selected:
            self.status_label.configure(text="Seleccion\u00e1 al menos un archivo", text_color="#FFA500")
            return

        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", tk.END)

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
            self.info_text.insert("1.0", "\n\n".join(all_info))
        if errors:
            if all_info:
                self.info_text.insert(tk.END, f"\n\n\u26a0\ufe0f ERRORES:\n" + "\n".join(errors))
            else:
                self.info_text.insert("1.0", "\u26a0\ufe0f ERRORES:\n" + "\n".join(errors))

        self.info_text.configure(state="disabled")
        status = f"Mostrando {len(all_info)}/{len(selected)} archivos"
        self.status_label.configure(text=status, text_color="green" if not errors else "#FFA500")

    def _show_result(self, result: Dict[str, Any]) -> None:
        if result.get("success"):
            self.status_label.configure(text=result.get("message", "Completado"), text_color="green")
        else:
            self.status_label.configure(text=result.get("message", "Error"), text_color="red")
