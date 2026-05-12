"""UI: Interfaz para herramienta de video."""
import threading
from ui.radiobutton import RadioButton
import customtkinter as ctk
import tkinter as tk
from pathlib import Path
from typing import Callable
from core.base_tool_ui import BaseToolUI
from core.tool_builder import create_standard_tool_ui
from core.constants import COLORS


class VideoToolUI(BaseToolUI):
    """UI para procesamiento b\u00e1sico de video."""

    def __init__(self, master, on_process: Callable, **kwargs):
        super().__init__(master, on_process, **kwargs)
        self.is_processing = False
        self._setup_progress_bar()

    def _setup_ui(self):
        r = create_standard_tool_ui(
            self, ("\U0001F3AC", "Herramienta de Video"),
            "",  # description moved to help_config
            selector_type="file",
            tab_configs=[{"name": "Extraer Audio"}, {"name": "Convertir"}, {"name": "Info"}],
            file_types=[
                ("Videos", "*.mp4 *.avi *.mkv *.mov *.webm *.wmv *.flv"),
                ("Todos", "*.*"),
            ],
            help_config={
                "description": "🎬 Procesa video: extrae audio, convierte formato, muestra información detallada",
                "file_label": "Archivo de video:",
                "usage": [
                    "1. 📥 Agregar videos (+)",
                    "2. ☑️ Seleccionar con Ctrl+click o botones 'Todos'/'Ninguno'",
                    "3. 📑 Elegir operación (Extraer Audio/Convertir/Info)",
                    "4. ⚙️ Configurar formato y calidad CRF",
                    "5. ▶️ Click en ejecutar (procesa solo los seleccionados)",
                ],
                "tips": [
                    "💡 CRF: 18=mejor calidad, 23=normal, 28=más baja",
                    "💡 CRF bajo = archivo más grande y mejor calidad",
                    "💡 FFmpeg debe estar instalado para funcionar",
                ],
                "warnings": [
                    "⚠️ mp4→mp4 con CRF23 se omite (ya en formato)",
                    "⚠️ Cambiar CRF para forzar recodificación",
                    "⚠️ Conversión puede tardar minutos",
                    "⚠️ FFmpeg debe estar instalado",
                    "⚠️ Archivos >1GB necesitan mucho espacio",
                ],
            },
        )
        self.files = r["files"]
        self.file_listbox = r["listbox"]
        self.status_label = r["status_label"]
        self.tab_extract = r["tabs"]["Extraer Audio"]
        self.tab_convert = r["tabs"]["Convertir"]
        self.tab_info = r["tabs"]["Info"]

        self._setup_extract_tab()
        self._setup_convert_tab()
        self._setup_info_tab()

    def _hide_progress_bar(self, progress_bar) -> None:
        progress_bar.set(0)
        progress_bar.pack_forget()

    def _setup_extract_tab(self) -> None:
        frame = self.tab_extract

        ctk.CTkLabel(frame, text="Extraer audio de video:", font=ctk.CTkFont(weight="bold")).pack(pady=10)

        fmt_frame = ctk.CTkFrame(frame)
        fmt_frame.pack(pady=10)

        ctk.CTkLabel(fmt_frame, text="Formato:").pack(side="left", padx=5)
        self.audio_format = ctk.StringVar(value="mp3")

        rb_font = ("Segoe UI", 12)
        RadioButton(fmt_frame, text="MP3", variable=self.audio_format, value="mp3", font=rb_font).pack(side="left", padx=10)
        RadioButton(fmt_frame, text="WAV", variable=self.audio_format, value="wav", font=rb_font).pack(side="left", padx=10)
        RadioButton(fmt_frame, text="OGG", variable=self.audio_format, value="ogg", font=rb_font).pack(side="left", padx=10)

        self.extract_progress = ctk.CTkProgressBar(frame, width=300)
        self.extract_progress.pack(pady=10)
        self.extract_progress.pack_forget()
        self.extract_progress.set(0)

        ctk.CTkButton(frame, text="\U0001F4BF Extraer Audio", command=self._extract_audio, height=40).pack(pady=10)

    def _extract_audio(self) -> None:
        if not self._check_files():
            return
        self.extract_progress.pack()
        self.extract_progress.set(0.1)
        self.status_label.configure(text="Extrayendo audio...", text_color="#FFD700")
        self.update()

        def extract_thread():
            try:
                from tools.video_tool.processor import extract_audio
                selected = self._get_selected_files()
                total = len(selected)
                success_count = 0
                errors = []

                for i, video_file in enumerate(selected):
                    progress = (i + 1) / total
                    self.after(0, lambda p=progress: self.extract_progress.set(p))
                    result = extract_audio(video_file, self.audio_format.get())
                    if result["success"]:
                        success_count += 1
                    else:
                        errors.append(Path(video_file).name)

                if success_count == total:
                    final_result = {"success": True, "message": f"\u2713 Audio extra\u00eddo de {total} videos"}
                elif success_count > 0:
                    final_result = {"success": True, "message": f"\u2713 {success_count}/{total} OK, {len(errors)} errores"}
                else:
                    final_result = {"success": False, "error": f'Errores: {", ".join(errors[:3])}'}

                self.after(0, lambda: self._on_extract_done(final_result))
            except Exception as e:
                self.after(0, lambda: self._on_extract_done({"success": False, "error": str(e)}))

        threading.Thread(target=extract_thread, daemon=True).start()

    def _on_extract_done(self, result: dict) -> None:
        self.extract_progress.set(1)
        if result["success"]:
            self.status_label.configure(text=result["message"], text_color="green")
        else:
            self.status_label.configure(text=result.get("error", "Error"), text_color="red")
        self.after(3000, lambda: self._hide_progress_bar(self.extract_progress))

    def _setup_convert_tab(self) -> None:
        frame = self.tab_convert

        ctk.CTkLabel(frame, text="Convertir video a otro formato:", font=ctk.CTkFont(weight="bold")).pack(pady=10)

        fmt_frame = ctk.CTkFrame(frame)
        fmt_frame.pack(pady=5)

        ctk.CTkLabel(fmt_frame, text="Formato salida:").pack(side="left", padx=5)
        self.out_format = ctk.StringVar(value="mp4")

        rb_font = ("Segoe UI", 12)
        for fmt in ["mp4", "avi", "mkv", "mov"]:
            RadioButton(fmt_frame, text=fmt, variable=self.out_format, value=fmt, font=rb_font).pack(side="left", padx=5)

        quality_frame = ctk.CTkFrame(frame)
        quality_frame.pack(pady=5)

        ctk.CTkLabel(quality_frame, text="Calidad:").pack(side="left", padx=5)
        self.crf_var = ctk.StringVar(value="23")

        for val, label in [("18", "Alta (18)"), ("23", "Media (23)"), ("28", "Baja (28)")]:
            RadioButton(quality_frame, text=label, variable=self.crf_var, value=val, font=rb_font).pack(side="left", padx=5)

        self.convert_progress = ctk.CTkProgressBar(frame, width=300)
        self.convert_progress.pack(pady=10)
        self.convert_progress.pack_forget()
        self.convert_progress.set(0)

        ctk.CTkButton(frame, text="\U0001F504 Convertir", command=self._convert_video, height=40).pack(pady=10)

    def _convert_video(self) -> None:
        if not self._check_files():
            return
        self.convert_progress.pack()
        self.convert_progress.set(0.1)
        selected = self._get_selected_files()
        self.status_label.configure(text=f"Convirtiendo 0/{len(selected)}...", text_color="#FFD700")
        self.update()

        def convert_thread():
            try:
                from tools.video_tool.processor import convert_video
                total = len(selected)
                success_count = 0
                errors = []
                skipped_files = []

                for i, video_file in enumerate(selected):
                    progress = (i + 1) / total
                    self.after(0, lambda p=progress, c=i + 1: self._update_convert_progress(p, c, total))
                    result = convert_video([video_file], self.out_format.get(), crf=int(self.crf_var.get()))
                    if result.get("skipped"):
                        skipped_files.extend(result["skipped"])
                    elif result["success"]:
                        success_count += 1
                    else:
                        errors.append(Path(video_file).name)

                if skipped_files and success_count == 0:
                    final_result = {"success": True, "message": f"\u2713 {len(skipped_files)} Videos ya estaban en formato"}
                elif skipped_files and success_count > 0:
                    final_result = {"success": True, "message": f"\u2713 {success_count} convertidos, {len(skipped_files)} omitidos"}
                elif success_count == total:
                    final_result = {"success": True, "message": f"\u2713 {total} videos convertidos"}
                elif success_count > 0:
                    final_result = {"success": True, "message": f"\u2713 {success_count}/{total} OK"}
                else:
                    final_result = {"success": False, "error": f'Errores: {", ".join(errors[:3])}'}

                self.after(0, lambda: self._on_convert_done(final_result))
            except Exception as e:
                self.after(0, lambda: self._on_convert_done({"success": False, "error": str(e)}))

        threading.Thread(target=convert_thread, daemon=True).start()

    def _update_convert_progress(self, progress: float, current: int, total: int) -> None:
        self.convert_progress.set(progress)
        self.status_label.configure(text=f"Convirtiendo {current}/{total}...", text_color="#FFD700")

    def _on_convert_done(self, result: dict) -> None:
        self.convert_progress.set(1)
        if result["success"]:
            self.status_label.configure(text=result["message"], text_color="green")
        else:
            self.status_label.configure(text=result.get("error", "Error"), text_color="red")
        self.after(3000, lambda: self._hide_progress_bar(self.convert_progress))

    def _setup_info_tab(self) -> None:
        frame = self.tab_info

        ctk.CTkLabel(frame, text="Informaci\u00f3n del video:", font=ctk.CTkFont(weight="bold")).pack(pady=10)

        ctk.CTkButton(frame, text="\U0001F441\ufe0f Ver Info", command=self._show_info).pack(pady=10)

        self.info_text = ctk.CTkTextbox(frame, width=500, height=300, wrap="word", fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"])
        self.info_text.pack(padx=10, pady=10)
        self.info_text.configure(state="disabled")

    def _show_info(self) -> None:
        if not self._check_files():
            self.status_label.configure(text="Seleccion\u00e1 un video primero", text_color="#FFA500")
            return

        from tools.video_tool.processor import get_video_info

        self.status_label.configure(text="Cargando info...", text_color="#FFD700")
        self.update()

        selected = self._get_selected_files()
        if not selected:
            self.status_label.configure(text="Seleccion\u00e1 un video", text_color="#FFA500")
            return

        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", tk.END)

        all_info = []
        errors = []

        for video_path in selected:
            result = get_video_info(video_path)
            if result["success"]:
                fps = result["video_fps"]
                if "/" in str(fps):
                    try:
                        num, den = fps.split("/")
                        fps = f"{float(num)/float(den):.2f}"
                    except (ValueError, ZeroDivisionError):
                        pass

                fmt = result["format"] or "N/A"
                if "," in fmt:
                    fmt = fmt.split(",")[0]

                res = result["video_resolution"] or "N/A"

                info = f"""\U0001F4F9 {result['file_name']}
{'\u2500' * 35}
  \U0001F4E6 Formato:     {fmt}
  \U0001F4BE Tama\u00f1o:      {result['file_size'] / 1024 / 1024:.2f} MB
  \u23f1\ufe0f Duraci\u00f3n:    {result['duration']:.1f}s
  \U0001F3AC Video:       {result['video_codec'] or 'N/A'} | {res}
  \u26a1 Bitrate:     {result.get('video_bitrate', 'N/A')}
  \U0001F39E\ufe0f FPS:        {fps}
  \U0001F50A Audio:       {result['audio_codec'] or 'N/A'}"""
                all_info.append(info)
            else:
                errors.append(f"{Path(video_path).name}: {result.get('error', 'Error')}")

        if all_info:
            self.info_text.insert("1.0", "\n\n".join(all_info))
        if errors:
            if all_info:
                self.info_text.insert(tk.END, f"\n\n\u26a0\ufe0f ERRORES:\n" + "\n".join(errors))
            else:
                self.info_text.insert("1.0", "\u26a0\ufe0f ERRORES:\n" + "\n".join(errors))

        if errors and not all_info:
            self.status_label.configure(text="Error al cargar info", text_color="red")
        else:
            self._update_selection_status()

        self.info_text.configure(state="disabled")
