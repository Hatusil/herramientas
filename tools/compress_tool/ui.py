"""UI: Interfaz para herramienta de compresión."""
import logging
import os
from core.help_panel import add_help
from ui.radiobutton import RadioButton
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import List, Callable

# Import BaseToolUI from core
from core.base_tool_ui import BaseToolUI


logger = logging.getLogger(__name__)


class CompressToolUI(BaseToolUI):
    """UI para comprimir y descomprimir archivos."""
    
    def __init__(self, master, on_process: Callable, **kwargs):
        # Call BaseToolUI __init__
        super().__init__(master, on_process, **kwargs)
        
        # Build tool-specific tabs after base selector
        self._build_tabs()
    
    def _build_tabs(self) -> None:
        """Build tool-specific tabs."""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_compress = self.tabview.add("Comprimir")
        self.tab_extract = self.tabview.add("Extraer")
        
        self._setup_compress_tab()
        self._setup_extract_tab()
    
    def _get_file_label(self) -> str:
        """Override: Label for file section."""
        return "Archivos/Carpetas:"
    
    def _get_file_dialog_filters(self) -> List[tuple]:
        """Override: Filters for file dialog."""
        return [
            ("Archivos y carpetas", "*.*"),
            ("Comprimidos", "*.zip *.tar *.tar.gz *.tar.bz2 *.tgz"),
            ("ZIP", "*.zip"),
            ("Todos", "*.*")
        ]
    
    def _get_custom_buttons(self) -> List[tuple]:
        """Override: Custom buttons for file selector."""
        # Button to add folder
        return [
            ("Agregar carpeta...", self._add_folder, {"height": 35})
        ]
    
    def _setup_ui(self) -> None:
        title = ctk.CTkLabel(
            self, 
            text="Compresor de Archivos", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(0, 10))
        
        # Help panel
        help_panel = add_help(
            self,
            description="📦 Comprime archivos en ZIP/TAR.GZ/TAR.BZ2 o extrae contenidos de archivos comprimidos",
            usage=[
                "1. 📥 Agregar archivos/carpetas (+)",
                "2. ☑️ Seleccionar con Ctrl+click o botones",
                "3. 📦 Elegir formato (ZIP/TAR) y nivel de compresión",
                "4. ▶️ Click en Comprimir (procesa seleccionados)"
            ],
            warnings=[
                "⚠️ ZIP→ZIP se omite (ya comprimido)",
                "⚠️ ZIP límite 4GB por archivo",
                "⚠️ TAR no abre en Windows directamente",
                "⚠️ Archivos >1GB pueden tomar minutos"
            ]
        )
        help_panel.pack(fill="x", padx=10, pady=5)
        
        # File selector (from BaseToolUI)
        self._setup_file_selector()
        
        # Status label (from BaseToolUI)
    
    def _setup_compress_tab(self) -> None:
        frame = self.tab_compress
        
        # Format
        fmt_frame = ctk.CTkFrame(frame)
        fmt_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(fmt_frame, text="Formato:").pack(side="left", padx=5)
        self.format_var = ctk.StringVar(value="zip")
        
        RadioButton(fmt_frame, text="ZIP", variable=self.format_var, value="zip").pack(side="left", padx=10)
        RadioButton(fmt_frame, text="TAR.GZ", variable=self.format_var, value="gz").pack(side="left", padx=10)
        RadioButton(fmt_frame, text="TAR.BZ2", variable=self.format_var, value="bz2").pack(side="left", padx=10)
        
        # Compression level
        level_frame = ctk.CTkFrame(frame)
        level_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(level_frame, text="Nivel:").pack(side="left", padx=5)
        self.level_var = ctk.StringVar(value="6")
        
        for level in [("1", "Rápido"), ("6", "Normal"), ("9", "Máximo")]:
            RadioButton(level_frame, text=level[1], variable=self.level_var, value=level[0]).pack(side="left", padx=10)
        
        ctk.CTkButton(
            frame, 
            text="📦 Comprimir", 
            command=self._compress, 
            height=40, 
            font=ctk.CTkFont(size=14)
        ).pack(pady=20)
    
    def _compress(self) -> None:
        if not self._check_files():
            return
        
        fmt = self.format_var.get()
        level = int(self.level_var.get())
        
        from tools.compress_tool import processor
        
        if fmt == 'zip':
            result = processor.compress_to_zip(self.files, level=level)
        else:
            compression: str = fmt if fmt != 'zip' else "gz"
            result = processor.compress_to_tar(self.files, compression=compression)
        
        if result['success']:
            self.status_label.configure(text=result['message'], text_color="green")
        else:
            self.status_label.configure(text=result.get('error', 'Error'), text_color="red")
    
    def _setup_extract_tab(self) -> None:
        frame = self.tab_extract
        
        ctk.CTkLabel(
            frame, 
            text="Seleccionar archivo comprimido:"
        ).pack(pady=5)
        
        ctk.CTkButton(
            frame, 
            text="Seleccionar ZIP/TAR...", 
            command=self._extract_file
        ).pack(pady=10)
        
        self.extract_info = ctk.CTkTextbox(frame, width=400, height=200)
        self.extract_info.pack(padx=10, pady=10)
    
    def _extract_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[
                ("Comprimidos", "*.zip *.tar *.tar.gz *.tar.bz2 *.tgz"),
                ("ZIP", "*.zip"),
                ("TAR", "*.tar *.tgz"),
                ("Todos", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        from tools.compress_tool import processor
        
        ext = Path(file_path).suffix.lower()
        
        if ext == '.zip':
            result = processor.decompress_zip(file_path)
        else:
            result = processor.decompress_tar(file_path)
        
        if result['success']:
            self.status_label.configure(text=result['message'], text_color="green")
            
            # Show contents if ZIP
            if ext == '.zip':
                info = processor.list_zip_contents(file_path)
                if info['success']:
                    self.extract_info.delete("1.0", tk.END)
                    self.extract_info.insert("1.0", f"Contenido ({info['count']} archivos):\n\n")
                    for f in info['files'][:20]:
                        self.extract_info.insert(tk.END, f"  📄 {f}\n")
                    if len(info['files']) > 20:
                        self.extract_info.insert(tk.END, f"\n... y {len(info['files']) - 20} más")
        else:
            self.status_label.configure(text=result.get('error', 'Error'), text_color="red")