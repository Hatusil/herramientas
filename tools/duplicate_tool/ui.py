"""
UI: Interfaz para encontrar archivos duplicados.
"""
import logging
import os
import customtkinter as ctk
from ui.help_panel import add_help
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)

def RadioButton(parent, **kwargs):
    return tk.Radiobutton(parent, **kwargs)


class DuplicateToolUI(ctk.CTkFrame):
    """UI para encontrar archivos duplicados."""
    
    def __init__(self, master, on_process: Callable):
        super().__init__(master)
        self.on_process = on_process
        self.duplicate_groups = []  # Almacena grupos de duplicados
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        title = ctk.CTkLabel(self, text="Encontrar Duplicados", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=(0, 10))
        
        # Panel de ayuda
        help_panel = add_help(
            self,
            description="📋 Encuentra y elimina duplicados por tamaño o hash MD5.",
            usage=[
                "1. Elegir carpeta a escanear",
                "2. Método: Tamaño (rápido) o Hash (exacto)",
                "3. Seleccionar tipos de archivo",
                "4. Buscar Duplicados",
                "5. Marcar los que eliminar",
                "6. Eliminar Seleccionados"
            ],
            warnings=[
                "⚠️ Eliminación IRREVERSIBLE",
                "⚠️ Dejá siempre al menos 1 archivo",
                "💡 Hash = resultados exactos"
            ]
        )
        help_panel.pack(fill="x", padx=10, pady=5)
        
        folder_frame = ctk.CTkFrame(self)
        folder_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(folder_frame, text="Carpeta a escanear:").pack(anchor="w", padx=10, pady=5)
        
        input_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=5)
        
        self.folder_entry = ctk.CTkEntry(input_frame, width=350)
        self.folder_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(input_frame, text="Elegir", width=60, command=self._select_folder).pack(side="left")
        
        opts_frame = ctk.CTkFrame(self)
        opts_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(opts_frame, text="Método:").pack(side="left", padx=5)
        self.method_var = ctk.StringVar(value="size")
        
        RadioButton(opts_frame, text="Por tamaño (rápido)", variable=self.method_var, value="size").pack(side="left", padx=10)
        RadioButton(opts_frame, text="Por hash (exacto)", variable=self.method_var, value="hash").pack(side="left", padx=10)
        
        ext_frame = ctk.CTkFrame(self)
        ext_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(ext_frame, text="Buscar en:").pack(side="left", padx=5)
        self.img_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(ext_frame, text="Imágenes", variable=self.img_var).pack(side="left", padx=5)
        
        self.doc_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(ext_frame, text="Documentos", variable=self.doc_var).pack(side="left", padx=5)
        
        self.audio_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(ext_frame, text="Audio/Video", variable=self.audio_var).pack(side="left", padx=5)
        
        ctk.CTkButton(self, text="🔍 Buscar Duplicados", command=self._find_duplicates, height=40).pack(pady=10)
        
        # Resultados con checkboxes para seleccionar
        results_frame = ctk.CTkFrame(self)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(results_frame, text="Resultados (seleccione los que quiere eliminar):", 
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5, 0))
        
        # Scrollable frame para los resultados
        self.results_scroll = ctk.CTkScrollableFrame(results_frame)
        self.results_scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Info de resultados
        self.results_info = ctk.CTkLabel(results_frame, text="", text_color="gray")
        self.results_info.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Botones de acción
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(action_frame, text="✅ Seleccionar Todos", 
                      command=self._select_all).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="⭕ Deseleccionar Todos", 
                      command=self._deselect_all).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionados", 
                      command=self._delete_selected, fg_color="red", 
                      hover_color="darkred").pack(side="left", padx=5)
        
        # Status
        self.status_label = ctk.CTkLabel(self, text="", text_color="gray")
        self.status_label.pack(pady=5)
    
    def _select_folder(self) -> None:
        folder = filedialog.askdirectory(title="Seleccionar carpeta")
        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)
            self.status_label.configure(text=f"Carpeta: {folder}", text_color="gray")
    
    def _find_duplicates(self) -> None:
        folder = self.folder_entry.get().strip()
        if not folder or not Path(folder).exists():
            self.status_label.configure(text="Seleccione una carpeta válida", text_color="orange")
            return
        
        exts = []
        if self.img_var.get():
            exts.extend(['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'])
        if self.doc_var.get():
            exts.extend(['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.odt'])
        if self.audio_var.get():
            exts.extend(['.mp3', '.wav', '.flac', '.mp4', '.avi', '.mkv'])
        
        if not exts:
            self.status_label.configure(text="Seleccione al menos un tipo", text_color="orange")
            return
        
        self.status_label.configure(text="Escaneando...", text_color="yellow")
        self.update()
        
        from tools.duplicate_tool.processor import find_duplicates_by_size, find_duplicates_by_hash
        
        method = self.method_var.get()
        
        if method == 'size':
            result = find_duplicates_by_size(folder)
        else:
            result = find_duplicates_by_hash(folder, exts)
        
        # Limpiar resultados anteriores
        for widget in self.results_scroll.winfo_children():
            widget.destroy()
        
        self.duplicate_groups = []
        
        if result['success']:
            dups = result.get('potential_duplicates', {}) if method == 'size' else result.get('duplicates', {})
            
            if not dups:
                ctk.CTkLabel(self.results_scroll, text="✅ No se encontraron duplicados", 
                            text_color="green").pack(pady=20)
                self.status_label.configure(text="Sin duplicados", text_color="green")
                self.results_info.configure(text="0 archivos duplicados")
            else:
                # Crear checkboxes para cada archivo
                total_files = 0
                for key, files in dups.items():
                    if not files:
                        continue
                    
                    # Determinar label del grupo
                    if method == 'size':
                        group_label = f"Grupo: {key/1024:.1f} KB ({len(files)} archivos)"
                    else:
                        group_label = f"Grupo: {len(files)} archivos"
                    
                    group_frame = ctk.CTkFrame(self.results_scroll)
                    group_frame.pack(fill="x", pady=2, padx=5)
                    
                    ctk.CTkLabel(group_frame, text=group_label, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5)
                    
                    for f in files:
                        total_files += 1
                        var = ctk.BooleanVar(value=False)
                        cb = ctk.CTkCheckBox(group_frame, text=f, variable=var)
                        cb.pack(anchor="w", padx=20, pady=1)
                        
                        # Guardar referencia con el checkbox
                        self.duplicate_groups.append((f, var, cb))
                
                self.status_label.configure(text=f"Encontrados: {result['count']} grupos", text_color="green")
                self.results_info.configure(text=f"Total: {total_files} archivos duplicados (seleccione para eliminar)")
        else:
            ctk.CTkLabel(self.results_scroll, text=f"❌ Error: {result.get('error', 'Error')}", 
                        text_color="red").pack(pady=20)
            self.status_label.configure(text=result.get('error', 'Error'), text_color="red")
    
    def _select_all(self) -> None:
        """Selecciona todos los archivos."""
        for path, var, cb in self.duplicate_groups:
            var.set(True)
    
    def _deselect_all(self) -> None:
        """Deselecciona todos los archivos."""
        for path, var, cb in self.duplicate_groups:
            var.set(False)
    
    def _delete_selected(self) -> None:
        """Elimina los archivos seleccionados."""
        selected = [(path, cb) for path, var, cb in self.duplicate_groups if var.get()]
        
        if not selected:
            messagebox.showwarning("Advertencia", "No hay archivos seleccionados")
            return
        
        # Confirmar eliminación
        if not messagebox.askyesno("Confirmar", 
                                    f"¿Eliminar {len(selected)} archivos seleccionados?\n\nEsta acción no se puede deshacer."):
            return
        
        deleted = 0
        errors = 0
        
        for path, cb in selected:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    deleted += 1
                    cb.destroy()  # Quitar de la UI
                else:
                    errors += 1
            except Exception as e:
                errors += 1
                logger.warning(f"Error eliminando {path}: {e}")
        
        # Actualizar lista
        self.duplicate_groups = [(p, v, c) for p, v, c in self.duplicate_groups if not v.get()]
        
        remaining = len(self.duplicate_groups)
        self.results_info.configure(text=f"Eliminados: {deleted}, Errors: {errors}, Restantes: {remaining}")
        
        if deleted > 0:
            messagebox.showinfo("Éxito", f"Se eliminaron {deleted} archivos")
        
        if errors > 0:
            messagebox.showwarning("Errores", f"No se pudieron eliminar {errors} archivos")