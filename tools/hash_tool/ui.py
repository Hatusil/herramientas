"""UI: Interfaz para Hash/Checksum tool."""
import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.help_panel import add_help
from ui.radiobutton import RadioButton
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import List, Callable


logger = logging.getLogger(__name__)


class HashToolUI(ctk.CTkFrame):
    """UI para calcular y verificar checksums."""
    
    def __init__(self, master, on_process: Callable):
        super().__init__(master)
        
        self.on_process = on_process
        self.files: List[str] = []
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        # Título
        title = ctk.CTkLabel(self, text="Hash y Checksums", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=(0, 10))
        
        # Panel de ayuda
        help_panel = add_help(
            self,
            description="🔐 Calcula y verifica hashes (MD5/SHA1/SHA256/SHA512) para verificar integridad de archivos descargados o copiar/mover sin cambios",
            usage=[
                "1. 📥 Agregar archivos (+)",
                "2. ☑️ Seleccionar con Ctrl+click o botones",
                "3. 🎯 Seleccionar algoritmo (SHA256 recomendado)",
                "4. 🔢 Click en calcular (procesa seleccionados)",
                "",
                "📌 ¿PARA QUÉ SIRVE?",
                "• Verificar descargas: Compara el hash calculado con el del servidor",
                "• Detectar cambios: Si hash es diferente, el archivo fue modificado",
                "• Identificar duplicados: Mismo hash = mismo archivo"
            ],
            warnings=[
                "⚠️ Hash diferente = archivo modificado o corrupto",
                "⚠️ MD5 no es seguro - solo para verificación de descarga",
                "⚠️ Verificación debe ser exacta (case-sensitive)",
                "⚠️ Copiar un archivo NO cambia su hash"
            ]
        )
        help_panel.pack(fill="x", padx=10, pady=5)
        
        # Selector
        self._setup_file_selector()
        
        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_calc = self.tabview.add("Calcular")
        self.tab_verify = self.tabview.add("Verificar")
        self.tab_list = self.tabview.add("Lista de Archivos")
        
        self._setup_calc_tab()
        self._setup_verify_tab()
        self._setup_list_tab()
        
        self.status_label = ctk.CTkLabel(self, text="", text_color="gray")
        self.status_label.pack(pady=5)
    
    def _setup_file_selector(self) -> None:
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", pady=(0, 10), padx=10)
        
        ctk.CTkLabel(frame, text="Archivos:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
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
        
        ctk.CTkButton(btn_frame, text="Agregar...", command=self._add_files, height=35).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="✓ Todos", command=self._select_all, height=35).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="✗ Ninguno", command=self._deselect_all, height=35).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="🗑️", command=self._clear_files, fg_color="#dc2626", width=40, height=35).pack(side="left", padx=2)
        
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
            self.status_label.configure(text="Seleccioná al menos un archivo", text_color="#FFA500")
            return False
        return True
    
    def _setup_calc_tab(self) -> None:
        frame = self.tab_calc
        
        ctk.CTkLabel(frame, text="Calcular hash (huella única del archivo):", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        # Explicación
        info = ctk.CTkLabel(
            frame,
            text="SHA256 = recommended | MD5 = only for old downloads",
            text_color="gray",
            font=ctk.CTkFont(size=11)
        )
        info.pack(pady=5)
        
        self.algo_var = ctk.StringVar(value="sha256")
        
        for algo in [("md5", "MD5"), ("sha1", "SHA1"), ("sha256", "SHA256"), ("sha512", "SHA512")]:
            RadioButton(frame, text=algo[1], variable=self.algo_var, value=algo[0]).pack(pady=2)
        
        ctk.CTkButton(frame, text="🔢 Calcular Hash", command=self._calculate, height=40).pack(pady=20)
        
        # Resultado
        self.calc_result = ctk.CTkTextbox(frame, width=400, height=150)
        self.calc_result.pack(padx=10, pady=10)
    
    def _calculate(self) -> None:
        if not self._check_files():
            return
        
        algo = self.algo_var.get()
        
        self.calc_result.delete("1.0", tk.END)
        self.calc_result.insert("1.0", f"Calculando {algo.upper()}...\n\n")
        
        from tools.hash_tool.processor import calculate_hash
        
        for f in self.files:
            result = calculate_hash(f, algo)
            if result['success']:
                self.calc_result.insert(tk.END, f"{result['file_name']}:\n  {result['hash']}\n\n")
            else:
                self.calc_result.insert(tk.END, f"Error: {result.get('error')}\n")
        
        self.status_label.configure(text=f"Calculado para {len(self.files)} archivos", text_color="green")
    
    def _setup_verify_tab(self) -> None:
        frame = self.tab_verify
        
        ctk.CTkLabel(frame, text="Verificar hash (comparar con valor conocido):", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        # Info labels
        info = ctk.CTkLabel(
            frame,
            text="Ingresa el hash del servidor o el original para comparar",
            text_color="gray",
            font=ctk.CTkFont(size=12)
        )
        info.pack(pady=5)
        
        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(input_frame, text="Hash esperado:").pack(side="left", padx=5)
        self.expected_hash = ctk.CTkEntry(input_frame, width=300)
        self.expected_hash.pack(side="left", padx=5)
        
        algo_frame = ctk.CTkFrame(frame)
        algo_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(algo_frame, text="Algoritmo:").pack(side="left", padx=5)
        self.verify_algo = ctk.StringVar(value="sha256")
        
        for algo in [("md5", "MD5"), ("sha1", "SHA1"), ("sha256", "SHA256")]:
            RadioButton(algo_frame, text=algo[1], variable=self.verify_algo, value=algo[0]).pack(side="left", padx=10)
        
        ctk.CTkButton(frame, text="✓ Verificar", command=self._verify, height=40).pack(pady=10)
        
        self.verify_result = ctk.CTkTextbox(frame, width=400, height=150)
        self.verify_result.pack(padx=10, pady=10)
    
    def _verify(self) -> None:
        if not self._check_files():
            return
        
        expected = self.expected_hash.get().strip()
        if not expected:
            self.status_label.configure(text="Ingrese el hash esperado", text_color="#FFA500")
            return
        
        algo = self.verify_algo.get()
        
        self.verify_result.delete("1.0", tk.END)
        
        from tools.hash_tool.processor import verify_hash
        
        # Procesar TODOS los archivos
        for file_path in self.files:
            result = verify_hash(file_path, expected, algo)
            
            if result['success']:
                if result['match']:
                    self.verify_result.insert(tk.END, f"[OK] {result['file_name']}: ✅ CORRESPIDE\n")
                else:
                    self.verify_result.insert(tk.END, f"[FAIL] {result['file_name']}: ❌ NO CORRESPIDE\n  Esperado: {result['expected'][:20]}...\n  Actual: {result['actual'][:20]}...\n")
    
    def _setup_list_tab(self) -> None:
        frame = self.tab_list
        
        ctk.CTkLabel(frame, text="Lista de archivos con todos los hashes:", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        ctk.CTkButton(frame, text="📋 Calcular Todos los Hashes", command=self._calc_all).pack(pady=10)
        
        self.all_hashes = ctk.CTkTextbox(frame, width=400, height=250)
        self.all_hashes.pack(padx=10, pady=10)
    
    def _calc_all(self) -> None:
        if not self._check_files():
            return
        
        self.all_hashes.delete("1.0", tk.END)
        
        from tools.hash_tool.processor import calculate_all_hashes
        
        for f in self.files:
            result = calculate_all_hashes(f)
            if result['success']:
                self.all_hashes.insert(tk.END, f"📄 {result['file_name']} ({result['file_size']} bytes)\n")
                for algo, h in result['hashes'].items():
                    self.all_hashes.insert(tk.END, f"  {algo}: {h}\n")
                self.all_hashes.insert(tk.END, "\n")
        
        self.status_label.configure(text="Todos los hashes calculados", text_color="green")