import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.help_panel import add_help
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import List, Callable
class ScrubberToolUI(ctk.CTkFrame):
    """UI para limpiar metadatos de archivos."""
    
    def __init__(self, master, on_process: Callable):
        super().__init__(master)
        
        self.on_process = on_process
        self.files: List[str] = []
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Configura los widgets de la UI."""
        
        # Título
        title = ctk.CTkLabel(
            self,
            text="Limpiador de Metadatos",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(0, 10))
        
        # Panel de ayuda
        help_panel = add_help(
            self,
            description="🧹 Limpia metadatos de imágenes (EXIF/GPS), documentos (DOCX/XLSX), y PDFs. Útil para privacidad",
            usage=[
                "1. 📥 Agregar archivos (+)",
                "2. ☑️ Seleccionar con Ctrl+click o botones",
                "3. 📑 Elegir tipo",
                "4. 🧹 Click en limpiar (procesa seleccionados)"
            ],
            warnings=[
                "⚠️ Metadatos se ELIMINAN PERMANENTEMENTE",
                "⚠️ Usar tab 'Preview' para ver qué se eliminará",
                "⚠️ GPS en fotos revela ubicación"
            ]
        )
        help_panel.pack(fill="x", padx=10, pady=5)
        
        # Selector de archivos
        self._setup_file_selector()
        
        # Tabs
        self._setup_tabs()
    
    def _setup_file_selector(self) -> None:
        """Configura el selector de archivos."""
        files_frame = ctk.CTkFrame(self)
        files_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        ctk.CTkLabel(
            files_frame,
            text="Archivos:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Lista de archivos
        list_container = ctk.CTkFrame(files_frame, fg_color="transparent")
        list_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.file_listbox = tk.Listbox(
            list_container,
            height=4,
            selectmode=tk.EXTENDED
        )
        scrollbar = tk.Scrollbar(list_container, orient="vertical")
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_listbox.yview)
        
        self.file_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botones
        btn_frame = ctk.CTkFrame(files_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="+ Agregar archivos...",
            command=self._add_files
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="✓ Todos",
            command=self._select_all
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="✗ Ninguno",
            command=self._deselect_all
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️",
            command=self._clear_files,
            fg_color="#dc2626",
            width=40
        ).pack(side="left", padx=2)
        
        self.file_listbox.bind('<<ListboxSelect>>', lambda e: self._update_selection_status())
    
    def _setup_tabs(self) -> None:
        """Configura los tabs."""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_images = self.tabview.add("Imágenes")
        self.tab_docs = self.tabview.add("Documentos")
        self.tab_preview = self.tabview.add("Preview")
        
        self._setup_images_tab()
        self._setup_docs_tab()
        self._setup_preview_tab()
        
        # Status
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            text_color="gray"
        )
        self.status_label.pack(pady=5)
    
    def _add_files(self) -> None:
        """Abre diálogo para seleccionar archivos."""
        files = filedialog.askopenfilenames(
            title="Seleccionar archivos",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.tiff"),
                ("Documentos", "*.docx *.xlsx"),
                ("Todos", "*.*")
            ]
        )
        
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self.file_listbox.insert(tk.END, Path(f).name)
        if files:
            self._update_selection_status()
    
    def _clear_files(self) -> None:
        """Limpia la lista de archivos."""
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
        """Verifica que haya archivos seleccionados."""
        if not self.files:
            self.status_label.configure(text="No hay archivos seleccionados", text_color="orange")
            return False
        return True
    
    # =========================================================================
    # TAB: IMÁGENES
    # =========================================================================
    def _setup_images_tab(self) -> None:
        frame = self.tab_images
        
        info = ctk.CTkLabel(
            frame,
            text="Opciones de limpieza para imágenes JPG:",
            font=ctk.CTkFont(weight="bold")
        )
        info.pack(pady=10)
        
        # Opciones
        self.remove_all_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            frame,
            text="Eliminar todos los metadatos (EXIF)",
            variable=self.remove_all_var
        ).pack(anchor="w", padx=20, pady=5)
        
        self.remove_gps_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            frame,
            text="Solo eliminar GPS (mantener otros datos)",
            variable=self.remove_gps_var
        ).pack(anchor="w", padx=20, pady=5)
        
        # Info
        info2 = ctk.CTkLabel(
            frame,
            text="Esto eliminará: fecha de captura, cámara, GPS, ubicación, etc.",
            text_color="gray",
            font=ctk.CTkFont(size=14)
        )
        info2.pack(pady=10)
        
        # Botón
        ctk.CTkButton(
            frame,
            text="🧹 Limpiar Metadatos de Imágenes",
            command=self._clean_images,
            height=40,
            font=ctk.CTkFont(size=14)
        ).pack(pady=20)
    
    def _clean_images(self) -> None:
        if not self._check_files():
            return
        
        # Filtrar solo imágenes
        image_exts = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp'}
        image_files = [f for f in self.files if Path(f).suffix.lower() in image_exts]
        
        if not image_files:
            self.status_label.configure(text="No hay imágenes seleccionadas", text_color="orange")
            return
        
        options = {
            'remove_all': self.remove_all_var.get(),
            'remove_gps': self.remove_gps_var.get(),
        }
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        # Procesar cada archivo
        results = []
        for f in image_files:
            result = self.on_process('clean_image', f, options)
            results.append(result)
        
        # Mostrar resultado
        success_count = sum(1 for r in results if r.get('success'))
        total = len(image_files)
        
        if success_count == 0:
            msg = f"Ninguno necesitaba limpieza"
        elif success_count == total:
            msg = f"✓ Limpiados {success_count} archivos"
        else:
            msg = f"✓ Limpiados {success_count}/{total} archivos"
        
        self.status_label.configure(text=msg, text_color="green")
    
    # =========================================================================
    # TAB: DOCUMENTOS
    # =========================================================================
    def _setup_docs_tab(self) -> None:
        frame = self.tab_docs
        
        info = ctk.CTkLabel(
            frame,
            text="Limpiar metadatos de documentos:",
            font=ctk.CTkFont(weight="bold")
        )
        info.pack(pady=10)
        
        # Info
        info2 = ctk.CTkLabel(
            frame,
            text="Esto eliminará: autor, título, fecha de creación,\ncomentarios, última modificación por, etc.",
            text_color="gray"
        )
        info2.pack(pady=5)
        
        # Botón DOCX
        ctk.CTkButton(
            frame,
            text="📄 Limpiar DOCX",
            command=self._clean_docx,
            height=35
        ).pack(pady=5)
        
        # Botón XLSX
        ctk.CTkButton(
            frame,
            text="📊 Limpiar XLSX",
            command=self._clean_xlsx,
            height=35
        ).pack(pady=5)
        
        # También PDF (usar el processor del PDF tool)
        ctk.CTkButton(
            frame,
            text="📑 Limpiar PDF (metadatos)",
            command=self._clean_pdf,
            height=35
        ).pack(pady=5)
    
    def _clean_docx(self) -> None:
        if not self._check_files():
            return
        
        docx_files = [f for f in self.files if f.lower().endswith('.docx')]
        
        if not docx_files:
            self.status_label.configure(text="No hay archivos DOCX", text_color="orange")
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        results = []
        for f in docx_files:
            result = self.on_process('clean_docx', f, {})
            results.append(result)
        
        success = sum(1 for r in results if r.get('success'))
        self.status_label.configure(
            text=f"Limpiados {success}/{len(docx_files)} DOCX",
            text_color="green"
        )
    
    def _clean_xlsx(self) -> None:
        if not self._check_files():
            return
        
        xlsx_files = [f for f in self.files if f.lower().endswith('.xlsx')]
        
        if not xlsx_files:
            self.status_label.configure(text="No hay archivos XLSX", text_color="orange")
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        results = []
        for f in xlsx_files:
            result = self.on_process('clean_xlsx', f, {})
            results.append(result)
        
        success = sum(1 for r in results if r.get('success'))
        self.status_label.configure(
            text=f"Limpiados {success}/{len(xlsx_files)} XLSX",
            text_color="green"
        )
    
    def _clean_pdf(self) -> None:
        if not self._check_files():
            return
        
        pdf_files = [f for f in self.files if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            self.status_label.configure(text="No hay archivos PDF", text_color="orange")
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        results = []
        for f in pdf_files:
            result = self.on_process('clean_pdf', f, {})
            results.append(result)
        
        success = sum(1 for r in results if r.get('success'))
        self.status_label.configure(
            text=f"Limpiados {success}/{len(pdf_files)} PDFs",
            text_color="green"
        )
    
    # =========================================================================
    # TAB: PREVIEW
    # =========================================================================
    def _setup_preview_tab(self) -> None:
        frame = self.tab_preview
        
        ctk.CTkLabel(
            frame,
            text="Ver metadatos del archivo seleccionado:",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=10)
        
        # Área de texto
        self.preview_text = ctk.CTkTextbox(frame, width=450, height=250)
        self.preview_text.pack(padx=10, pady=10)
        
        # Botón ver
        ctk.CTkButton(
            frame,
            text="👁️ Ver Metadatos",
            command=self._show_metadata
        ).pack(pady=5)
    
    def _show_metadata(self) -> None:
        if not self._check_files():
            return
        
        self.preview_text.delete("1.0", tk.END)
        
        # Procesar TODOS los archivos
        for i, file_path in enumerate(self.files):
            self.preview_text.insert(tk.END, f"\n[{i+1}] {os.path.basename(file_path)}\n{'='*30}\n")
            
            ext = Path(file_path).suffix.lower()
            
            try:
                if ext in {'.jpg', '.jpeg'}:
                    from tools.scrubber.processor import get_image_metadata
                    info = get_image_metadata(file_path)
                elif ext in {'.png', '.webp'}:
                    self.preview_text.insert(tk.END, "Información: PNG/WebP no tienen EXIF como JPG\n")
                    info = {'success': True, 'metadata': {'formato': ext.upper()}}
                elif ext == '.docx':
                    from tools.scrubber.processor import get_docx_metadata
                    info = get_docx_metadata(file_path)
                elif ext == '.xlsx':
                    from tools.scrubber.processor import get_xlsx_metadata
                    info = get_xlsx_metadata(file_path)
                elif ext == '.pdf':
                    from tools.pdf_tool.processor import get_pdf_info
                    info = get_pdf_info(file_path)
                else:
                    self.preview_text.insert(tk.END, "Formato no soportado\n")
                    continue
                
                if info.get('success'):
                    metadata = info.get('metadata', {})
                    for key, value in metadata.items():
                        if value:
                            self.preview_text.insert(tk.END, f"{key}: {value}\n")
                else:
                    self.preview_text.insert(tk.END, f"Error: {info.get('error', 'Desconocido')}\n")
                    
            except Exception as e:
                self.preview_text.insert(tk.END, f"Error: {str(e)}\n")