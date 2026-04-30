"""
QuickFileSelector: Selector de archivos con acceso rápido.
Se puede integrar en cualquier tool existente.
"""
import os
import logging
import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
from typing import List, Callable
import tkinter as tk

logger = logging.getLogger(__name__)


class QuickFileSelector:
    """
    Agrega botones de acceso rápido a un frame con listbox existente.
    
    Uso:
        selector = QuickFileSelector(frame, listbox, files_list, on_change)
        selector.add_quick_buttons()
    """
    
    def __init__(self, parent_frame, listbox: tk.Listbox, files_list: List[str], on_change: Callable = None):
        self.parent = parent_frame
        self.listbox = listbox
        self.files = files_list
        self.on_change = on_change
    
    def add_quick_buttons(self):
        """Agrega botones de acceso rápido."""
        quick_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        quick_frame.pack(fill="x", pady=(0, 5))
        
        # Botones de acceso rápido tipo botón
        ctk.CTkButton(
            quick_frame,
            text="📂",
            tooltip="Directorio actual",
            command=self._open_current,
            width=35,
            height=28
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            quick_frame,
            text="🖥️",
            tooltip="Escritorio",
            command=self._open_desktop,
            width=35,
            height=28
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            quick_frame,
            text="📁",
            tooltip="Documentos",
            command=self._open_documents,
            width=35,
            height=28
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            quick_frame,
            text="⬇️",
            tooltip="Descargas",
            command=self._open_downloads,
            width=35,
            height=28
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            quick_frame,
            text="💾",
            tooltip="USB / Disco extraíble",
            command=self._open_removable,
            width=35,
            height=28
        ).pack(side="left", padx=2)
    
    def _open_current(self):
        self._open_folder(os.getcwd())
    
    def _open_desktop(self):
        desktop = os.path.expanduser("~/Desktop")
        if os.path.exists(desktop):
            self._open_folder(desktop)
        else:
            self._open_folder(os.getcwd())
    
    def _open_documents(self):
        docs = os.path.expanduser("~/Documents")
        if os.path.exists(docs):
            self._open_folder(docs)
    
    def _open_downloads(self):
        downloads = os.path.expanduser("~/Downloads")
        if os.path.exists(downloads):
            self._open_folder(downloads)
    
    def _open_removable(self):
        """Abre diálogo para seleccionar unidad removable."""
        # En Windows, intenta abrir en D:, E:, etc.
        if os.name == 'nt':
            for letter in ['D', 'E', 'F', 'G']:
                drive = f"{letter}:\\"
                try:
                    if os.path.exists(drive):
                        self._open_folder(drive)
                        return
                except Exception as e:
                    logger.warning(f"Error checking drive {drive}: {e}")
        
        # Fallback a folder picker
        folder = filedialog.askdirectory(title="Seleccionar carpeta (USB/disco)")
        if folder:
            self._open_folder(folder)
    
    def _open_folder(self, folder: str):
        """Abre archivos de una carpeta."""
        try:
            files = filedialog.askopenfilenames(
                title=f"Seleccionar de {folder}",
                initialdir=folder
            )
            for f in files:
                if f not in self.files:
                    self.files.append(f)
                    self.listbox.insert(tk.END, Path(f).name)
            
            if files and self.on_change:
                self.on_change(self.files)
        except Exception as e:
            logger.warning(f"Error in open folder: {e}")


def add_quick_buttons(parent_frame, listbox: tk.Listbox, files_list: List[str], on_change: Callable = None):
    """Función helper para agregar botones de acceso rápido."""
    selector = QuickFileSelector(parent_frame, listbox, files_list, on_change)
    selector.add_quick_buttons()
    return selector