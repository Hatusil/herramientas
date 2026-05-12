"""UI: Interfaz para herramienta de compresión."""
from ui.radiobutton import RadioButton
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import Callable
from core.base_tool_ui import BaseToolUI
from core.tool_builder import create_standard_tool_ui
from core.constants import COLORS


class CompressToolUI(BaseToolUI):
    """UI para comprimir y descomprimir archivos."""

    def __init__(self, master, on_process: Callable, **kwargs):
        super().__init__(master, on_process, **kwargs)
        self.is_processing = False

    def _setup_ui(self):
        r = create_standard_tool_ui(
            self, ("\U0001F4E6", "Compresor de Archivos"),
            "",  # description moved to help_config
            selector_type="file",
            tab_configs=[{"name": "Comprimir"}, {"name": "Extraer"}],
            file_types=[
                ("Archivos y carpetas", "*.*"),
                ("Comprimidos", "*.zip *.tar *.tar.gz *.tar.bz2 *.tgz"),
                ("ZIP", "*.zip"),
                ("Todos", "*.*"),
            ],
            help_config={
                "description": "📦 Comprime archivos en ZIP/TAR.GZ/TAR.BZ2 o extrae contenidos comprimidos",
                "file_label": "Archivos/Carpetas:",
                "usage": [
                    "1. 📥 Agregar archivos/carpetas (+) o 'Agregar carpeta...'",
                    "2. ☑️ Seleccionar con Ctrl+click o botones",
                    "3. 📦 Elegir formato (ZIP/TAR.GZ/TAR.BZ2) y nivel de compresión",
                    "4. ▶️ Click en Comprimir (procesa seleccionados)",
                ],
                "tips": [
                    "💡 ZIP = más compatible (abre en Windows, Mac, Linux)",
                    "💡 TAR.GZ = mejor para Linux/Mac, preserva estructura",
                    "💡 Nivel 6 = buen balance velocidad/tamaño",
                ],
                "warnings": [
                    "⚠️ ZIP→ZIP se omite (ya comprimido)",
                    "⚠️ ZIP límite 4GB por archivo",
                    "⚠️ TAR no abre en Windows directamente",
                    "⚠️ Archivos >1GB pueden tomar minutos",
                ],
            },
        )
        self.files = r["files"]
        self.file_listbox = r["listbox"]
        self.status_label = r["status_label"]
        self.tab_compress = r["tabs"]["Comprimir"]
        self.tab_extract = r["tabs"]["Extraer"]

        ctk.CTkButton(
            r.get("btn_frame"), text="Agregar carpeta...",
            command=r["add_folder"], height=35
        ).pack(side="left", padx=2)

        self._setup_compress_tab()
        self._setup_extract_tab()

    def _setup_compress_tab(self) -> None:
        frame = self.tab_compress

        fmt_frame = ctk.CTkFrame(frame)
        fmt_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(fmt_frame, text="Formato:").pack(side="left", padx=5)
        self.format_var = ctk.StringVar(value="zip")

        RadioButton(fmt_frame, text="ZIP", variable=self.format_var, value="zip").pack(side="left", padx=10)
        RadioButton(fmt_frame, text="TAR.GZ", variable=self.format_var, value="gz").pack(side="left", padx=10)
        RadioButton(fmt_frame, text="TAR.BZ2", variable=self.format_var, value="bz2").pack(side="left", padx=10)

        level_frame = ctk.CTkFrame(frame)
        level_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(level_frame, text="Nivel:").pack(side="left", padx=5)
        self.level_var = ctk.StringVar(value="6")

        for level in [("1", "R\u00e1pido"), ("6", "Normal"), ("9", "M\u00e1ximo")]:
            RadioButton(level_frame, text=level[1], variable=self.level_var, value=level[0]).pack(side="left", padx=10)

        ctk.CTkButton(
            frame, text="\U0001F4E6 Comprimir", command=self._compress,
            height=40, font=ctk.CTkFont(size=14)
        ).pack(pady=20)

    def _compress(self) -> None:
        if not self._check_files():
            return
        fmt = self.format_var.get()
        level = int(self.level_var.get())
        from tools.compress_tool import processor
        if fmt == "zip":
            result = processor.compress_to_zip(self.files, level=level)
        else:
            result = processor.compress_to_tar(self.files, compression=fmt)
        if result["success"]:
            self.status_label.configure(text=result["message"], text_color="green")
        else:
            self.status_label.configure(text=result.get("error", "Error"), text_color="red")

    def _setup_extract_tab(self) -> None:
        frame = self.tab_extract

        ctk.CTkLabel(frame, text="Seleccionar archivo comprimido:").pack(pady=5)

        ctk.CTkButton(
            frame, text="Seleccionar ZIP/TAR...", command=self._extract_file
        ).pack(pady=10)

        self.extract_info = ctk.CTkTextbox(frame, width=400, height=200, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"])
        self.extract_info.pack(padx=10, pady=10)

    def _extract_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[
                ("Comprimidos", "*.zip *.tar *.tar.gz *.tar.bz2 *.tgz"),
                ("ZIP", "*.zip"),
                ("TAR", "*.tar *.tgz"),
                ("Todos", "*.*"),
            ],
        )
        if not file_path:
            return
        from tools.compress_tool import processor
        ext = Path(file_path).suffix.lower()
        if ext == ".zip":
            result = processor.decompress_zip(file_path)
        else:
            result = processor.decompress_tar(file_path)
        if result["success"]:
            self.status_label.configure(text=result["message"], text_color="green")
            if ext == ".zip":
                info = processor.list_zip_contents(file_path)
                if info["success"]:
                    self.extract_info.delete("1.0", tk.END)
                    self.extract_info.insert("1.0", f"Contenido ({info['count']} archivos):\n\n")
                    for f in info["files"][:20]:
                        self.extract_info.insert(tk.END, f"  \U0001F4C4 {f}\n")
                    if len(info["files"]) > 20:
                        self.extract_info.insert(tk.END, f"\n... y {len(info['files']) - 20} m\u00e1s")
        else:
            self.status_label.configure(text=result.get("error", "Error"), text_color="red")
