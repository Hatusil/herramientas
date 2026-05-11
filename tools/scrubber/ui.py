import os
import logging
from core.help_panel import add_help
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import List, Callable

# Import BaseToolUI from core
from core.base_tool_ui import BaseToolUI


logger = logging.getLogger(__name__)


class ScrubberToolUI(BaseToolUI):
    """UI para limpiar metadatos de archivos."""
    
    def __init__(self, master, on_process: Callable, **kwargs):
        # Call BaseToolUI __init__ which calls _setup_ui()
        super().__init__(master, on_process, **kwargs)
        
        # Estado: evitar doble click
        self.is_processing = False
        
        # Build tool-specific tabs after base selector
        self._build_tabs()
    
    def _build_tabs(self) -> None:
        """Build tool-specific tabs."""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_images = self.tabview.add("Imágenes")
        self.tab_docs = self.tabview.add("Documentos")
        self.tab_preview = self.tabview.add("Preview")
        
        self._setup_images_tab()
        self._setup_docs_tab()
        self._setup_preview_tab()
    
    def _get_file_label(self) -> str:
        """Override: Label for file section."""
        return "Archivos:"
    
    def _get_file_dialog_filters(self) -> List[tuple]:
        """Override: Filters for file dialog."""
        return [
            ("Todos los archivos", "*.*"),
            ("Imágenes", "*.jpg;*.jpeg;*.png;*.bmp"),
            ("Documentos", "*.docx;*.xlsx"),
            ("PDF", "*.pdf")
        ]
    
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
            description="🧹 Limpia metadatos de imágenes (JPG), documentos (DOCX/XLSX), y PDFs. Útil para privacidad",
            usage=[
                "1. 📥 Agregar archivos (+)",
                "2. ☑️ Seleccionar con Ctrl+click o botones",
                "3. 📑 Elegir tipo (Imágenes/Documentos)",
                "4. 🧹 Click en limpiar (procesa seleccionados)"
            ],
            warnings=[
                "⚠️ Metadatos se ELIMINAN PERMANENTEMENTE",
                "⚠️ Solo JPG soporta EXIF completo, PNG/WebP sin metadatos",
                "⚠️ Usar tab 'Preview' para ver qué se eliminará",
                "⚠️ GPS en fotos revela ubicación"
            ]
        )
        help_panel.pack(fill="x", padx=10, pady=5)
        
        # File selector (from BaseToolUI)
        self._setup_file_selector()
        
        # Status label (from BaseToolUI sets self.status_label)
    
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
        
        # Opciones (solo una puede seleccionarse)
        self.clean_mode_var = ctk.StringVar(value="all")
        
        ctk.CTkRadioButton(
            frame,
            text="Eliminar todos los metadatos (EXIF)",
            variable=self.clean_mode_var,
            value="all"
        ).pack(anchor="w", padx=20, pady=5)
        
        ctk.CTkRadioButton(
            frame,
            text="Solo eliminar GPS (mantener otros datos)",
            variable=self.clean_mode_var,
            value="gps"
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
        
        # Usar solo los seleccionados
        selected = self._get_selected_files()
        
        # Filtrar solo imágenes
        image_exts = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp'}
        image_files = [f for f in selected if Path(f).suffix.lower() in image_exts]
        non_images = len(selected) - len(image_files)
        
        if not image_files:
            msg = "No hay imágenes seleccionadas"
            if non_images > 0:
                msg += f" ({non_images} docs/PDFs omitidos)"
            self.status_label.configure(text=msg, text_color="#FFA500")
            return
        
        options = {
            'remove_all': self.clean_mode_var.get() == 'all',
            'remove_gps': self.clean_mode_var.get() == 'gps'
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
            self.status_label.configure(text="No hay archivos DOCX", text_color="#FFA500")
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
            self.status_label.configure(text="No hay archivos XLSX", text_color="#FFA500")
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
            self.status_label.configure(text="No hay archivos PDF", text_color="#FFA500")
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
                    self.preview_text.insert(tk.END, "Info: PNG/WebP sin EXIF estándar\n")
                    info = {'success': True, 'metadata': {'formato': ext[1:].upper()}}
                elif ext == '.docx':
                    from tools.scrubber.processor import get_docx_metadata
                    info = get_docx_metadata(file_path)
                elif ext == '.xlsx':
                    from tools.scrubber.processor import get_xlsx_metadata
                    info = get_xlsx_metadata(file_path)
                elif ext == '.pdf':
                    from tools.pdf_tool.modules.info import get_pdf_info
                    info = get_pdf_info(file_path)
                elif ext == '.mp3':
                    self.preview_text.insert(tk.END, "Info: MP3 sin metadatos EXIF\n")
                    info = {'success': True, 'metadata': {'formato': 'MP3'}}
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