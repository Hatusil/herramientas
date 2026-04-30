"""UI: Interfaz para herramienta de video."""
import sys
from ui.quick_selector import add_quick_buttons
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.radiobutton import RadioButton
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import List, Dict, Any, Callable


class VideoToolUI(ctk.CTkFrame):
    """UI para procesamiento básico de video."""
    
    def __init__(self, master, on_process: Callable):
        super().__init__(master)
        self.on_process = on_process
        self.files: List[str] = []
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        title = ctk.CTkLabel(self, text="Herramienta de Video", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=(0, 10))
        
        self._setup_file_selector()
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_extract = self.tabview.add("Extraer Audio")
        self.tab_convert = self.tabview.add("Convertir")
        self.tab_info = self.tabview.add("Info")
        
        self._setup_extract_tab()
        self._setup_convert_tab()
        self._setup_info_tab()
        
        self.status_label = ctk.CTkLabel(self, text="", text_color="gray")
        self.status_label.pack(pady=5)
    
    def _setup_file_selector(self) -> None:
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", pady=(0, 10), padx=10)
        
        ctk.CTkLabel(frame, text="Archivo de video:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        list_cont = ctk.CTkFrame(frame, fg_color="transparent")
        list_cont.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.file_listbox = tk.Listbox(list_cont, height=3)
        scroll = tk.Scrollbar(list_cont, orient="vertical")
        self.file_listbox.config(yscrollcommand=scroll.set)
        scroll.config(command=self.file_listbox.yview)
        self.file_listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(btn_frame, text="Seleccionar video...", command=self._add_files).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Limpiar", command=self._clear_files)
        try:
            add_quick_buttons(btn_frame, self.file_listbox if hasattr(self, "file_listbox") else self.files_listbox, self.files)
        except:
            pass.pack(side="left", padx=5)
    
    def _add_files(self) -> None:
        files = filedialog.askopenfilenames(
            title="Seleccionar video",
            filetypes=[("Videos", "*.mp4 *.avi *.mkv *.mov *.webm *.wmv *.flv"), ("Todos", "*.*")]
        )
        
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self.file_listbox.insert(tk.END, Path(f).name)
    
    def _clear_files(self) -> None:
        self.files.clear()
        self.file_listbox.delete(0, tk.END)
    
    def _check_files(self) -> bool:
        if not self.files:
            self.status_label.configure(text="No hay archivos", text_color="orange")
            return False
        return True
    
    def _setup_extract_tab(self) -> None:
        frame = self.tab_extract
        
        ctk.CTkLabel(frame, text="Extraer audio de video:", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        fmt_frame = ctk.CTkFrame(frame)
        fmt_frame.pack(pady=10)
        
        ctk.CTkLabel(fmt_frame, text="Formato:").pack(side="left", padx=5)
        self.audio_format = ctk.StringVar(value="mp3")
        
        RadioButton(fmt_frame, text="MP3", variable=self.audio_format, value="mp3").pack(side="left", padx=10)
        RadioButton(fmt_frame, text="WAV", variable=self.audio_format, value="wav").pack(side="left", padx=10)
        RadioButton(fmt_frame, text="OGG", variable=self.audio_format, value="ogg").pack(side="left", padx=10)
        
        ctk.CTkButton(frame, text="🎵 Extraer Audio", command=self._extract_audio, height=40).pack(pady=20)
    
    def _extract_audio(self) -> None:
        if not self._check_files():
            return
        
        from tools.video_tool.processor import extract_audio
        
        result = extract_audio(self.files[0], self.audio_format.get())
        
        if result['success']:
            self.status_label.configure(text=result['message'], text_color="green")
        else:
            self.status_label.configure(text=result.get('error', 'Error'), text_color="red")
    
    def _setup_convert_tab(self) -> None:
        frame = self.tab_convert
        
        ctk.CTkLabel(frame, text="Convertir video a otro formato:", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        fmt_frame = ctk.CTkFrame(frame)
        fmt_frame.pack(pady=5)
        
        ctk.CTkLabel(fmt_frame, text="Formato salida:").pack(side="left", padx=5)
        self.out_format = ctk.StringVar(value="mp4")
        
        for fmt in ["mp4", "avi", "mkv", "webm", "mov"]:
            RadioButton(fmt_frame, text=fmt, variable=self.out_format, value=fmt).pack(side="left", padx=5)
        
        quality_frame = ctk.CTkFrame(frame)
        quality_frame.pack(pady=5)
        
        ctk.CTkLabel(quality_frame, text="Calidad:").pack(side="left", padx=5)
        self.crf_var = ctk.StringVar(value="23")
        
        RadioButton(quality_frame, text="Alta (18)", variable=self.crf_var, value="18").pack(side="left", padx=5)
        RadioButton(quality_frame, text="Media (23)", variable=self.crf_var, value="23").pack(side="left", padx=5)
        RadioButton(quality_frame, text="Baja (28)", variable=self.crf_var, value="28").pack(side="left", padx=5)
        
        ctk.CTkButton(frame, text="🔄 Convertir", command=self._convert_video, height=40).pack(pady=20)
    
    def _convert_video(self) -> None:
        if not self._check_files():
            return
        
        from tools.video_tool.processor import convert_video
        
        result = convert_video(self.files[0], self.out_format.get(), crf=int(self.crf_var.get()))
        
        if result['success']:
            self.status_label.configure(text=result['message'], text_color="green")
        else:
            self.status_label.configure(text=result.get('error', 'Error'), text_color="red")
    
    def _setup_info_tab(self) -> None:
        frame = self.tab_info
        
        ctk.CTkLabel(frame, text="Información del video:", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        ctk.CTkButton(frame, text="👁️ Ver Info", command=self._show_info).pack(pady=10)
        
        self.info_text = ctk.CTkTextbox(frame, width=400, height=200)
        self.info_text.pack(padx=10, pady=10)
    
    def _show_info(self) -> None:
        if not self._check_files():
            return
        
        from tools.video_tool.processor import get_video_info
        
        result = get_video_info(self.files[0])
        
        self.info_text.delete("1.0", tk.END)
        
        if result['success']:
            self.info_text.insert("1.0", f"""Información del Video:
─────────────────────────────────
Archivo: {result['file_name']}
Tamaño: {result['file_size'] / 1024 / 1024:.2f} MB
Duración: {result['duration']:.2f} seg
Formato: {result['format']}

Video:
─────────────────────────────────
Codec: {result['video_codec']}
Resolución: {result['video_resolution']}
FPS: {result['video_fps']}

Audio:
─────────────────────────────────
Codec: {result['audio_codec']}
""")
        else:
            self.info_text.insert("1.0", f"Error: {result.get('error', 'Desconocido')}")