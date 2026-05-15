"""
FileSelectorMixin - Mixin para selector de archivos.
"""
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import List

import customtkinter as ctk
from core.constants import font, COLORS


class FileSelectorMixin:
    """Mixin que provee funcionalidad de selector de archivos."""
    
    def _setup_file_selector(self) -> None:
        """Construye el selector de archivos con lista y botones."""
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Etiqueta de la sección
        ctk.CTkLabel(
            frame, 
            text=self._get_file_label(), 
            font=font("normal", "bold")
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
            fg_color=COLORS.get("error"), 
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
        """Retorna la lista de archivos seleccionados."""
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
        """Valida que haya al menos un archivo seleccionado."""
        if not self.files:
            self.status_label.configure(text="⚠️ No hay archivos", text_color="orange")
            return False
        return True