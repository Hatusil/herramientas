import os
from core.help_panel import add_help
from ui.radiobutton import RadioButton
import customtkinter as ctk
import tkinter as tk
from pathlib import Path
from typing import List, Callable, Dict

# Import BaseToolUI from core
from core.base_tool_ui import BaseToolUI


class RenameToolUI(BaseToolUI):
    """UI para renombrar archivos en masa."""
    
    def __init__(self, master, on_process: Callable, **kwargs):
        # Call BaseToolUI __init__
        super().__init__(master, on_process, **kwargs)
        
        # Build tool-specific tabs
        self._build_tabs()
    
    def _build_tabs(self) -> None:
        """Build tool-specific tabs."""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_prefix = self.tabview.add("Prefijo")
        self.tab_suffix = self.tabview.add("Sufijo")
        self.tab_replace = self.tabview.add("Reemplazar")
        self.tab_numbers = self.tabview.add("Números")
        self.tab_case = self.tabview.add("May/Min")
        
        self._setup_prefix_tab()
        self._setup_suffix_tab()
        self._setup_replace_tab()
        self._setup_numbers_tab()
        self._setup_case_tab()
    
    def _get_file_label(self) -> str:
        """Override: Label for file section."""
        return "Archivos a renombrar:"
    
    def _setup_ui(self) -> None:
        title = ctk.CTkLabel(
            self, 
            text="Renombrador de Archivos", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(0, 10))
        
        # Help panel
        help_panel = add_help(
            self,
            description="🔤 Renombra archivos: prefijos, sufijos, buscar/reemplazar, números, mayúsculas/minúsculas",
            usage=[
                "1. 📥 Agregar archivos (+)",
                "2. ☑️ Seleccionar con Ctrl+click o botones",
                "3. 📑 Elegir operación",
                "4. ▶️ Click en ejecutar (procesa seleccionados)"
            ],
            warnings=[
                "⚠️ Operación DESTRUCTIVA sin deshacer",
                "⚠️ Verificar nombres ANTES de cerrar",
                "⚠️ Números pueden sobrescribir existentes"
            ]
        )
        help_panel.pack(fill="x", padx=10, pady=5)
        
        # File selector (from BaseToolUI)
        self._setup_file_selector()
        
        # Status label (from BaseToolUI)
    
    def _setup_prefix_tab(self) -> None:
        frame = self.tab_prefix
        
        ctk.CTkLabel(
            frame, 
            text="Agregar prefijo al nombre:", 
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=10)
        
        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(pady=10)
        
        ctk.CTkLabel(input_frame, text="Prefijo:").pack(side="left", padx=5)
        self.prefix_entry = ctk.CTkEntry(input_frame, width=200)
        self.prefix_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame, 
            text="🔖 Agregar Prefijo", 
            command=self._add_prefix, 
            height=40
        ).pack(pady=20)
    
    def _add_prefix(self) -> None:
        if not self._check_files():
            return
        
        prefix = self.prefix_entry.get()
        if not prefix:
            self.status_label.configure(text="Ingrese un prefijo", text_color="#FFA500")
            return
        
        from tools.rename_tool.processor import rename_with_prefix
        result = rename_with_prefix(self.files, prefix)
        
        self._handle_result(result)
    
    def _setup_suffix_tab(self) -> None:
        frame = self.tab_suffix
        
        ctk.CTkLabel(
            frame, 
            text="Agregar sufijo antes de la extensión:", 
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=10)
        
        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(pady=10)
        
        ctk.CTkLabel(input_frame, text="Sufijo:").pack(side="left", padx=5)
        self.suffix_entry = ctk.CTkEntry(input_frame, width=200)
        self.suffix_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame, 
            text="🔖 Agregar Sufijo", 
            command=self._add_suffix, 
            height=40
        ).pack(pady=20)
    
    def _add_suffix(self) -> None:
        if not self._check_files():
            return
        
        suffix = self.suffix_entry.get()
        
        from tools.rename_tool.processor import rename_with_suffix
        result = rename_with_suffix(self.files, suffix)
        
        self._handle_result(result)
    
    def _setup_replace_tab(self) -> None:
        frame = self.tab_replace
        
        ctk.CTkLabel(
            frame, 
            text="Reemplazar texto en los nombres:", 
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=10)
        
        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(pady=5)
        
        ctk.CTkLabel(input_frame, text="Buscar:").pack(side="left", padx=5)
        self.find_entry = ctk.CTkEntry(input_frame, width=150)
        self.find_entry.pack(side="left", padx=5)
        
        input_frame2 = ctk.CTkFrame(frame)
        input_frame2.pack(pady=5)
        
        ctk.CTkLabel(input_frame2, text="Reemplazar con:").pack(side="left", padx=5)
        self.replace_entry = ctk.CTkEntry(input_frame2, width=150)
        self.replace_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame, 
            text="🔄 Reemplazar", 
            command=self._do_replace, 
            height=40
        ).pack(pady=10)
    
    def _do_replace(self) -> None:
        if not self._check_files():
            return
        
        find = self.find_entry.get()
        if not find:
            self.status_label.configure(text="Ingrese texto a buscar", text_color="#FFA500")
            return
        
        replace = self.replace_entry.get()
        
        from tools.rename_tool.processor import rename_replace
        result = rename_replace(self.files, find, replace)
        
        self._handle_result(result)
    
    def _setup_numbers_tab(self) -> None:
        frame = self.tab_numbers
        
        ctk.CTkLabel(
            frame, 
            text="Renombrar con números secuenciales:", 
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=10)
        
        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(pady=5)
        
        ctk.CTkLabel(input_frame, text="Iniciar desde:").pack(side="left", padx=5)
        self.start_entry = ctk.CTkEntry(input_frame, width=60)
        self.start_entry.insert(0, "1")
        self.start_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(input_frame, text="Patrón:").pack(side="left", padx=5)
        self.pattern_entry = ctk.CTkEntry(input_frame, width=120)
        self.pattern_entry.insert(0, "{name}_{n}")
        self.pattern_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(
            frame, 
            text="(Usa {name} para nombre original y {n} para número)", 
            text_color="gray", 
            font=ctk.CTkFont(size=13)
        ).pack(pady=2)
        
        ctk.CTkButton(
            frame, 
            text="🔢 Numerar", 
            command=self._do_number, 
            height=40
        ).pack(pady=10)
    
    def _do_number(self) -> None:
        if not self._check_files():
            return
        
        start = int(self.start_entry.get() or 1)
        pattern = self.pattern_entry.get() or "{name}_{n}"
        
        from tools.rename_tool.processor import rename_numbered
        result = rename_numbered(self.files, start=start, pattern=pattern)
        
        self._handle_result(result)
    
    def _setup_case_tab(self) -> None:
        frame = self.tab_case
        
        ctk.CTkLabel(
            frame, 
            text="Cambiar mayúsculas/minúsculas:", 
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=10)
        
        self.case_var = ctk.StringVar(value="lower")
        
        RadioButton(frame, text="minúsculas", variable=self.case_var, value="lower").pack(pady=5)
        RadioButton(frame, text="MAYÚSCULAS", variable=self.case_var, value="upper").pack(pady=5)
        RadioButton(frame, text="Título (Capital)", variable=self.case_var, value="title").pack(pady=5)
        
        ctk.CTkButton(
            frame, 
            text="🔄 Convertir", 
            command=self._do_case, 
            height=40
        ).pack(pady=20)
    
    def _do_case(self) -> None:
        if not self._check_files():
            return
        
        case = self.case_var.get()
        
        from tools.rename_tool.processor import rename_case
        result = rename_case(self.files, case)
        
        self._handle_result(result)
    
    def _handle_result(self, result: Dict) -> None:
        if result.get('success'):
            self.status_label.configure(text=result['message'], text_color="green")
            if result.get('errors'):
                self.status_label.configure(text=f"{result['message']} - {len(result['errors'])} errores", text_color="#FFA500")
            # Clear only if successful
            self._clear_files()
        else:
            self.status_label.configure(text=result.get('error', 'Error'), text_color="red")