"""
FilePicker: Selector de archivos con acceso rápido a unidades y favoritos.
"""
import os
import sys
import logging
import subprocess
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from typing import List, Callable

logger = logging.getLogger(__name__)

# Check win32api availability at module level (Issue #2: unhandled import)
try:
    import win32api
    HAS_WIN32API = True
except ImportError:
    HAS_WIN32API = False


class FilePicker(ctk.CTkFrame):
    """
    Selector de archivos con acceso rápido a:
    - Unidades extraíbles/removibles
    - Carpetas frecuentes
    - Directorio actual
    """
    
    def __init__(self, master, filetypes=None, multiple=True, on_select: Callable = None):
        super().__init__(master, fg_color="transparent")
        
        self.filetypes = filetypes or [("Todos", "*.*")]
        self.multiple = multiple
        self.on_select = on_select
        self.files: List[str] = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la UI."""
        self._setup_title()
        self._setup_quick_buttons()
        self._setup_file_list()
        self._setup_action_buttons()
    
    def _setup_title(self):
        """Configura el título."""
        title = ctk.CTkLabel(
            self,
            text="Seleccionar archivos:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 5))
    
    def _setup_quick_buttons(self):
        """Configura los botones de acceso rápido."""
        quick_frame = ctk.CTkFrame(self, fg_color="transparent")
        quick_frame.pack(fill="x", pady=(0, 5))
        
        # Botón directorio actual
        ctk.CTkButton(
            quick_frame,
            text="📂 Actual",
            command=self._open_current_dir,
            width=80,
            height=28
        ).pack(side="left", padx=2)
        
        # Botón escritorio
        if os.path.exists(os.path.expanduser("~/Desktop")):
            ctk.CTkButton(
                quick_frame,
                text="🖥️ Escritorio",
                command=self._open_desktop,
                width=80,
                height=28
            ).pack(side="left", padx=2)
        
        # Botón documentos
        if os.path.exists(os.path.expanduser("~/Documents")):
            ctk.CTkButton(
                quick_frame,
                text="📁 Docs",
                command=self._open_documents,
                width=80,
                height=28
            ).pack(side="left", padx=2)
        
        # Botón descargas
        if os.path.exists(os.path.expanduser("~/Downloads")):
            ctk.CTkButton(
                quick_frame,
                text="⬇️ Descargas",
                command=self._open_downloads,
                width=80,
                height=28
            ).pack(side="left", padx=2)
        
        # Botón unidades removibles
        removable = self._get_removable_drives()
        if removable:
            for drive in removable[:3]:  # Max 3 USBs
                ctk.CTkButton(
                    quick_frame,
                    text=drive,
                    command=lambda d=drive: self._open_folder(d),
                    width=50,
                    height=28
                ).pack(side="left", padx=2)
    
    def _setup_file_list(self):
        """Configura la lista de archivos."""
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill="both", expand=True, pady=5)
        
        # Scrollbar
        scroll = ctk.CTkScrollbar(list_frame)
        scroll.pack(side="right", fill="y")
        
        # Listbox
        self.listbox = tk.Listbox(
            list_frame,
            height=5,
            yscrollcommand=scroll.set,
            bg="#1a1a1a",
            fg="white",
            selectbackground="#3b82f6",
            borderwidth=0
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scroll.config(command=self.listbox.yview)
        
        # Bind para doble click
        self.listbox.bind("<Double-Button-1>", self._on_double_click)
    
    def _setup_action_buttons(self):
        """Configura los botones de acción."""
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(5, 0))
        
        ctk.CTkButton(
            btn_frame,
            text="Seleccionar archivos...",
            command=self._select_files,
            height=32
        ).pack(side="left", padx=2, fill="x", expand=True)
        
        ctk.CTkButton(
            btn_frame,
            text="Seleccionar carpeta",
            command=self._select_folder,
            height=32
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="Limpiar",
            command=self._clear_files,
            fg_color="#dc2626",
            hover_color="#b91c1c",
            height=32
        ).pack(side="left", padx=2)
    
    def _get_removable_drives(self) -> List[str]:
        """Detecta unidades removibles USB."""
        drives = []
        
        if os.name == 'nt':  # Windows
            # Buscar letras de unidad
            import string
            for letter in string.ascii_uppercase[:26]:
                drive = f"{letter}:\\"
                try:
                    if os.path.exists(drive):
                        # Check if removable using win32api if available
                        if HAS_WIN32API:
                            try:
                                drive_type = win32api.GetDriveType(drive)
                                if drive_type == 2:  # DRIVE_REMOVABLE
                                    drives.append(drive)
                            except Exception as e:
                                logger.warning(f"Error checking drive type for {drive}: {e}")
                                # Fallback: check common USB drive letters
                                if letter in ['D', 'E', 'F']:
                                    drives.append(drive)
                        else:
                            # Fallback for systems without win32api
                            if letter in ['D', 'E', 'F']:
                                drives.append(drive)
                except Exception as e:
                    logger.warning(f"Error checking drive {drive}: {e}")
        else:  # Linux
            # Check /media and /mnt
            for base in ['/media', '/mnt', '/run/media']:
                if os.path.exists(base):
                    for user in os.listdir(base):
                        user_path = os.path.join(base, user)
                        if os.path.isdir(user_path):
                            for drive in os.listdir(user_path):
                                full = os.path.join(user_path, drive)
                                if os.path.ismount(full):
                                    drives.append(full)
        
        return drives
    
    def _open_current_dir(self):
        self._select_folder()
    
    def _open_desktop(self):
        desktop = os.path.expanduser("~/Desktop")
        if os.path.exists(desktop):
            self._open_folder(desktop)
    
    def _open_documents(self):
        docs = os.path.expanduser("~/Documents")
        if os.path.exists(docs):
            self._open_folder(docs)
    
    def _open_downloads(self):
        downloads = os.path.expanduser("~/Downloads")
        if os.path.exists(downloads):
            self._open_folder(downloads)
    
    def _open_folder(self, folder_path: str):
        """Abre diálogo en carpeta específica."""
        if os.path.isdir(folder_path):
            files = filedialog.askopenfilenames(
                title=f"Seleccionar de {folder_path}",
                initialdir=folder_path,
                filetypes=self.filetypes
            )
            if files:
                self._add_files(list(files))
    
    def _select_files(self):
        """Seleccionar archivos con diálogo."""
        if self.multiple:
            files = filedialog.askopenfilenames(
                title="Seleccionar archivos",
                filetypes=self.filetypes
            )
        else:
            file = filedialog.askopenfilename(
                title="Seleccionar archivo",
                filetypes=self.filetypes
            )
            files = [file] if file else []
        
        if files:
            self._add_files(files)
    
    def _select_folder(self):
        """Seleccionar carpeta."""
        folder = filedialog.askdirectory(title="Seleccionar carpeta")
        if folder:
            # Add all files in folder
            try:
                files = [os.path.join(folder, f) 
                        for f in os.listdir(folder)
                        if os.path.isfile(os.path.join(folder, f))]
                if files:
                    self._add_files(files)
            except Exception as e:
                logger.warning(f"Error listing folder: {e}")
    
    def _clear_files(self):
        """Limpiar lista."""
        self.files.clear()
        self.listbox.delete(0, tk.END)
    
    def _add_files(self, files: List[str]):
        """Agregar archivos a la lista."""
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self.listbox.insert(tk.END, os.path.basename(f))
        
        if self.on_select:
            self.on_select(self.files)
    
    def _on_double_click(self, event):
        """Doble click abre archivo."""
        selection = self.listbox.curselection()
        if selection:
            idx = selection[0]
            if 0 <= idx < len(self.files):
                file = self.files[idx]
                if os.path.isfile(file):
                    open_file_cross_platform(file)
    
    def get_files(self) -> List[str]:
        """Retorna lista de archivos."""
        return self.files