"""
BaseToolUI: Clase base compartida para herramientas con selector de archivos.

Provee métodos comunes de UI para todas las herramientas que necesitan
seleccionar archivos. Las herramientas heredan de esta clase y sobrescriben
los hooks según sea necesario.
"""
import os

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import List, Callable, Optional


class BaseToolUI(ctk.CTkFrame):
    """
    Clase base para UI de herramientas con selector de archivos.
    
    Args:
        master: Frame padre donde se construirá la UI
        on_process: Callback que se llama cuando se procesan archivos
        **kwargs: Argumentos adicionales para CTkFrame
    """
    
    def __init__(self, master, on_process: Callable, **kwargs):
        super().__init__(master, **kwargs)
        
        self.on_process = on_process
        self.files: List[str] = []
        self.file_listbox: Optional[tk.Listbox] = None
        self.status_label: Optional[ctk.CTkLabel] = None
        
        self._setup_ui()
    
    # === Override hooks ===
    
    def _get_file_dialog_filters(self) -> List[tuple]:
        """
        Override: Retorna filtros para el diálogo de archivos.
        
        Returns:
            List of (label, patterns) tuples for filedialog
        """
        return [("Todos los archivos", "*.*")]
    
    def _get_file_label(self) -> str:
        """
        Override: Retorna el texto de la etiqueta para la sección de archivos.
        
        Returns:
            str: Texto de la etiqueta
        """
        return "Archivos:"
    
    def _get_custom_buttons(self) -> List[tuple]:
        """
        Override: Retorna botones adicionales para la barra de archivos.
        
        Returns:
            List of (text, command, options) tuples
        """
        return []
    
    def _add_folder_custom(self) -> bool:
        """
        Override: Implementación personalizada para agregar carpetas.
        
        Returns:
            bool: True si se manejó la acción, False para usar la implementación por defecto
        """
        return False
    
    def _add_files_custom(self) -> bool:
        """
        Override: Implementación personalizada para agregar archivos.
        
        Returns:
            bool: True si se manejó la acción, False para usar la implementación por defecto
        """
        return False
    
    # === Main UI setup ===
    
    def _setup_ui(self) -> None:
        """Construye la UI de la herramienta. Override para customize completa."""
        self._setup_file_selector()
        
        # Subclasses can override _setup_ui() to add more UI elements
        # or call super()._setup_ui() if they just want the file selector
    
    def _setup_file_selector(self) -> None:
        """Construye el selector de archivos con lista y botones."""
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Etiqueta de la sección
        ctk.CTkLabel(
            frame, 
            text=self._get_file_label(), 
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Contenedor para lista con scrollbar
        list_cont = ctk.CTkFrame(frame, fg_color="transparent")
        list_cont.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.file_listbox = tk.Listbox(list_cont, height=3, selectmode=tk.EXTENDED)
        scroll = tk.Scrollbar(list_cont, orient="vertical")
        self.file_listbox.config(yscrollcommand=scroll.set)
        scroll.config(command=self.file_listbox.yview)
        self.file_listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        
        # Botones estándar
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Botón agregar archivos
        ctk.CTkButton(
            btn_frame, 
            text="Agregar...", 
            command=self._add_files, 
            height=35
        ).pack(side="left", padx=2)
        
        # Botón seleccionar todos
        ctk.CTkButton(
            btn_frame, 
            text="✓ Todos", 
            command=self._select_all, 
            height=35
        ).pack(side="left", padx=2)
        
        # Botón deseleccionar todos
        ctk.CTkButton(
            btn_frame, 
            text="✗ Ninguno", 
            command=self._deselect_all, 
            height=35
        ).pack(side="left", padx=2)
        
        # Botón limpiar
        ctk.CTkButton(
            btn_frame, 
            text="🗑️", 
            command=self._clear_files, 
            fg_color="#dc2626", 
            width=40, 
            height=35
        ).pack(side="left", padx=2)
        
        # Botones personalizados del tool
        for btn_text, btn_cmd, btn_opts in self._get_custom_buttons():
            ctk.CTkButton(btn_frame, text=btn_text, command=btn_cmd, **btn_opts).pack(side="left", padx=5)
        
        # Binding para actualizar estado al cambiar selección
        self.file_listbox.bind('<<ListboxSelect>>', lambda e: self._update_selection_status())
        
        # Status label
        self.status_label = ctk.CTkLabel(self, text="", text_color="gray")
        self.status_label.pack(pady=5)
    
    # === File operations ===
    
    def _add_files(self) -> None:
        """Abre diálogo para agregar archivos."""
        # Allow custom implementation
        if self._add_files_custom():
            return
        
        filters = self._get_file_dialog_filters()
        files = filedialog.askopenfilenames(
            title="Seleccionar archivos",
            filetypes=filters
        )
        
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self.file_listbox.insert(tk.END, Path(f).name)
        
        if files:
            self._update_selection_status()
    
    def _add_folder(self) -> None:
        """Abre diálogo para agregar carpeta."""
        # Allow custom implementation
        if self._add_folder_custom():
            return
        
        folder = filedialog.askdirectory(title="Seleccionar carpeta")
        if folder and folder not in self.files:
            self.files.append(folder)
            self.file_listbox.insert(tk.END, f"📁 {Path(folder).name}")
            self._update_selection_status()
    
    def _clear_files(self) -> None:
        """Limpia todos los archivos de la lista."""
        self.files.clear()
        self.file_listbox.delete(0, tk.END)
        self.status_label.configure(text="Lista vacía", text_color="gray")
    
    def _select_all(self) -> None:
        """Selecciona todos los archivos en la lista."""
        self.file_listbox.select_set(0, tk.END)
        self._update_selection_status()
    
    def _deselect_all(self) -> None:
        """Deselecciona todos los archivos."""
        self.file_listbox.select_clear(0, tk.END)
        self._update_selection_status()
    
    def _get_selected_files(self) -> List[str]:
        """
        Retorna la lista de archivos seleccionados.
        
        Returns:
            List[str]: Rutas de los archivos seleccionados
        """
        selected = self.file_listbox.curselection()
        if not selected:
            return []
        return [self.files[i] for i in selected]
    
    def _update_selection_status(self) -> None:
        """Actualiza el label de estado con la selección actual."""
        selected = self._get_selected_files()
        total = len(self.files)
        
        if not selected:
            self.status_label.configure(
                text=f"{total} archivos (ninguno seleccionado)", 
                text_color="gray"
            )
        elif len(selected) == total:
            self.status_label.configure(
                text=f"{total} seleccionados", 
                text_color="blue"
            )
        else:
            self.status_label.configure(
                text=f"{len(selected)}/{total} seleccionados", 
                text_color="blue"
            )
    
    def _check_files(self) -> bool:
        """
        Valida que haya al menos un archivo seleccionado.
        
        Returns:
            bool: True si hay archivos seleccionados, False si no
        """
        selected = self._get_selected_files()
        if not selected:
            self.status_label.configure(
                text="Seleccioná al menos un archivo", 
                text_color="#FFA500"
            )
            return False
        return True