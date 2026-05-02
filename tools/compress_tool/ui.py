"""UI: Interfaz para herramienta de compresión."""
import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.help_panel import add_help
from ui.radiobutton import RadioButton
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import List, Callable
import os


logger = logging.getLogger(__name__)


class CompressToolUI(ctk.CTkFrame):
    """UI para comprimir y descomprimir archivos."""
    
    def __init__(self, master, on_process: Callable):
        super().__init__(master)
        self.on_process = on_process
        self.files: List[str] = []
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        title = ctk.CTkLabel(self, text="Compresor de Archivos", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=(0, 10))
        
        # Panel de ayuda
        help_panel = add_help(
            self,
            description="📦 Comprime archivos en ZIP/TAR.GZ/TAR.BZ2 o extrae contenidos de archivos comprimidos",
            usage=[
                "1. 📥 Agregar archivos/carpetas (+)",
                "2. ☑️ Seleccionar con Ctrl+click o botones",
                "3. 📦 Elegir formato y nivel de compresión",
                "4. ▶️ Click en Comprimir (procesa seleccionados)"
            ],
            warnings=[
                "⚠️ ZIP límite 4GB por archivo",
                "⚠️ TAR no abre en Windows directamente",
                "⚠️ Archivos >1GB pueden tomar minutos"
            ]
        )
        help_panel.pack(fill="x", padx=10, pady=5)
        
        self._setup_file_selector()
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_compress = self.tabview.add("Comprimir")
        self.tab_extract = self.tabview.add("Extraer")
        
        self._setup_compress_tab()
        self._setup_extract_tab()
        
        self.status_label = ctk.CTkLabel(self, text="", text_color="gray")
        self.status_label.pack(pady=5)
    
    def _setup_file_selector(self) -> None:
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", pady=(0, 10), padx=10)
        
        ctk.CTkLabel(frame, text="Archivos/Carpetas:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        list_cont = ctk.CTkFrame(frame, fg_color="transparent")
        list_cont.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.file_listbox = tk.Listbox(list_cont, height=3, selectmode=tk.EXTENDED)
        scroll = tk.Scrollbar(list_cont, orient="vertical")
        self.file_listbox.config(yscrollcommand=scroll.set)
        scroll.config(command=self.file_listbox.yview)
        self.file_listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(btn_frame, text="Agregar archivos...", command=self._add_files).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Agregar carpeta...", command=self._add_folder).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="✓ Todos", command=self._select_all).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="✗ Ninguno", command=self._deselect_all).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="🗑️", command=self._clear_files, fg_color="#dc2626", width=40).pack(side="left", padx=2)
        
        # Bind selection change
        self.file_listbox.bind('<<ListboxSelect>>', lambda e: self._update_selection_status())
    
    def _add_files(self) -> None:
        files = filedialog.askopenfilenames(title="Seleccionar archivos")
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self.file_listbox.insert(tk.END, Path(f).name)
        if files:
            self._update_selection_status()
    
    def _add_folder(self) -> None:
        folder = filedialog.askdirectory(title="Seleccionar carpeta")
        if folder and folder not in self.files:
            self.files.append(folder)
            self.file_listbox.insert(tk.END, f"📁 {Path(folder).name}")
            self._update_selection_status()
    
    def _clear_files(self) -> None:
        self.files.clear()
        self.file_listbox.delete(0, tk.END)
        self.status_label.configure(text="Lista vacía", text_color="gray")
    
    def _select_all(self) -> None:
        self.file_listbox.select_set(0, tk.END)
        self._update_selection_status()
    
    def _deselect_all(self) -> None:
        self.file_listbox.select_clear(0, tk.END)
        self._update_selection_status()
    
    def _get_selected_files(self) -> List[str]:
        selected = self.file_listbox.curselection()
        if not selected:
            return []
        return [self.files[i] for i in selected]
    
    def _update_selection_status(self) -> None:
        selected = self._get_selected_files()
        total = len(self.files)
        if not selected:
            self.status_label.configure(text=f"{total} archivos (ninguno seleccionado)", text_color="gray")
        elif len(selected) == total:
            self.status_label.configure(text=f"{total} seleccionados", text_color="blue")
        else:
            self.status_label.configure(text=f"{len(selected)}/{total} seleccionados", text_color="blue")
    
    def _check_files(self) -> bool:
        selected = self._get_selected_files()
        if not selected:
            self.status_label.configure(text="Seleccioná al menos un archivo", text_color="orange")
            return False
        return True
    
    def _setup_compress_tab(self) -> None:
        frame = self.tab_compress
        
        # Formato
        fmt_frame = ctk.CTkFrame(frame)
        fmt_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(fmt_frame, text="Formato:").pack(side="left", padx=5)
        self.format_var = ctk.StringVar(value="zip")
        
        RadioButton(fmt_frame, text="ZIP", variable=self.format_var, value="zip").pack(side="left", padx=10)
        RadioButton(fmt_frame, text="TAR.GZ", variable=self.format_var, value="gz").pack(side="left", padx=10)
        RadioButton(fmt_frame, text="TAR.BZ2", variable=self.format_var, value="bz2").pack(side="left", padx=10)
        
        # Nivel de compresión
        level_frame = ctk.CTkFrame(frame)
        level_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(level_frame, text="Nivel:").pack(side="left", padx=5)
        self.level_var = ctk.StringVar(value="6")
        
        for level in [("1", "Rápido"), ("6", "Normal"), ("9", "Máximo")]:
            RadioButton(level_frame, text=level[1], variable=self.level_var, value=level[0]).pack(side="left", padx=10)
        
        ctk.CTkButton(frame, text="📦 Comprimir", command=self._compress, height=40, font=ctk.CTkFont(size=14)).pack(pady=20)
    
    def _compress(self) -> None:
        if not self._check_files():
            return
        
        fmt = self.format_var.get()
        level = int(self.level_var.get())
        
        from tools.compress_tool import processor
        
        if fmt == 'zip':
            result = processor.compress_to_zip(self.files, level=level)
        else:
            result = processor.compress_to_tar(self.files, compression=fmt if fmt != 'zip' else None)
        
        if result['success']:
            self.status_label.configure(text=result['message'], text_color="green")
        else:
            self.status_label.configure(text=result.get('error', 'Error'), text_color="red")
    
    def _setup_extract_tab(self) -> None:
        frame = self.tab_extract
        
        ctk.CTkLabel(frame, text="Seleccionar archivo comprimido:").pack(pady=5)
        
        ctk.CTkButton(frame, text="Seleccionar ZIP/TAR...", command=self._extract_file).pack(pady=10)
        
        self.extract_info = ctk.CTkTextbox(frame, width=400, height=200)
        self.extract_info.pack(padx=10, pady=10)
    
    def _extract_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Comprimidos", "*.zip *.tar *.tar.gz *.tar.bz2 *.tgz"), ("ZIP", "*.zip"), ("TAR", "*.tar *.tgz"), ("Todos", "*.*")]
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
            
            # Mostrar contenido si es ZIP
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