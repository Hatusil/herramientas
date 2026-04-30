import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.help_panel import add_help
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import List, Callable, Dict, Any
class PDFToolUI(ctk.CTkFrame):
    """UI para procesamiento de archivos PDF."""
    
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
            text="Procesamiento de PDF",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(0, 10))
        
        # Panel de ayuda
        help_panel = add_help(
            self,
            description="📄 Procesa PDFs: watermark, anotar, rotar, combinar, extraer páginas, agregar números, encriptar, comprimir, ver info",
            usage=[
                "1. 📥 Agregar PDFs (+)",
                "2. ☑️ Seleccionar con Ctrl+click o botones",
                "3. 📑 Elegir operación",
                "4. ▶️ Click en ejecutar (procesa seleccionados)"
            ],
            warnings=[
                "⚠️ PDFs encriptados requieren contraseña primero",
                "⚠️ Combinar/extraer son destructivos - crea nuevo archivo",
                "⚠️ Watermark modifica el original"
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
            text="Archivos PDF:",
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
            text="+ Agregar PDFs...",
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
        
        # Bind selection change
        self.file_listbox.bind('<<ListboxSelect>>', lambda e: self._update_selection_status())
    
    def _setup_tabs(self) -> None:
        """Configura los tabs de operaciones."""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Crear tabs
        self.tab_watermark = self.tabview.add("Watermark")
        self.tab_edit = self.tabview.add("Editar")
        self.tab_transform = self.tabview.add("Transformar")
        self.tab_combine = self.tabview.add("Combinar")
        self.tab_numbers = self.tabview.add("Números")
        self.tab_security = self.tabview.add("Seguridad")
        self.tab_optimize = self.tabview.add("Optimizar")
        self.tab_info = self.tabview.add("Info")
        
        # Configurar cada tab
        self._setup_watermark_tab()
        self._setup_edit_tab()
        self._setup_transform_tab()
        self._setup_combine_tab()
        self._setup_numbers_tab()
        self._setup_security_tab()
        self._setup_optimize_tab()
        self._setup_info_tab()
        
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
            title="Seleccionar archivos PDF",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
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
        selected = self._get_selected_files()
        if not selected:
            self.status_label.configure(text="Seleccioná al menos un archivo", text_color="orange")
            return False
        return True
    
    # =========================================================================
    # TAB: WATERMARK
    # =========================================================================
    def _setup_watermark_tab(self) -> None:
        frame = self.tab_watermark
        
        # Texto
        text_frame = ctk.CTkFrame(frame)
        text_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(text_frame, text="Texto:").pack(side="left", padx=5)
        self.watermark_text = ctk.CTkEntry(text_frame, width=200)
        self.watermark_text.insert(0, "WATERMARK")
        self.watermark_text.pack(side="left", padx=5)
        
        # Opciones
        options_frame = ctk.CTkFrame(frame)
        options_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(options_frame, text="Tamaño:").pack(side="left", padx=5)
        self.watermark_size = ctk.CTkEntry(options_frame, width=60)
        self.watermark_size.insert(0, "48")
        self.watermark_size.pack(side="left", padx=5)
        
        ctk.CTkLabel(options_frame, text="Color:").pack(side="left", padx=5)
        self.watermark_color = ctk.CTkEntry(options_frame, width=80)
        self.watermark_color.insert(0, "#888888")
        self.watermark_color.pack(side="left", padx=5)
        
        ctk.CTkLabel(options_frame, text="Opacidad:").pack(side="left", padx=5)
        self.watermark_opacity = ctk.CTkEntry(options_frame, width=60)
        self.watermark_opacity.insert(0, "0.3")
        self.watermark_opacity.pack(side="left", padx=5)
        
        ctk.CTkLabel(options_frame, text="Rotación:").pack(side="left", padx=5)
        self.watermark_rotation = ctk.CTkEntry(options_frame, width=60)
        self.watermark_rotation.insert(0, "45")
        self.watermark_rotation.pack(side="left", padx=5)
        
        # Botones
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Aplicar Watermark de Texto",
            command=self._apply_text_watermark,
            height=40
        ).pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(
            btn_frame,
            text="Quitar Watermarks",
            command=self._remove_watermark,
            height=40
        ).pack(side="left", padx=5, fill="x", expand=True)
    
    def _apply_text_watermark(self) -> None:
        if not self._check_files():
            return
        
        text = self.watermark_text.get() or "WATERMARK"
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        result = self.on_process('text_watermark', self.files, {
            'text': text,
            'font_size': int(self.watermark_size.get() or 48),
            'color': self.watermark_color.get() or '#888888',
            'opacity': float(self.watermark_opacity.get() or 0.3),
            'rotation': int(self.watermark_rotation.get() or 45),
        })
        
        self._show_result(result)
    
    def _remove_watermark(self) -> None:
        if not self._check_files():
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        result = self.on_process('remove_watermark', self.files, {})
        
        self._show_result(result)
    
    # =========================================================================
    # TAB: EDITAR
    # =========================================================================
    def _setup_edit_tab(self) -> None:
        frame = self.tab_edit
        
        # Anotación
        ann_frame = ctk.CTkFrame(frame)
        ann_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(ann_frame, text="Agregar Anotación:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        
        pos_frame = ctk.CTkFrame(ann_frame, fg_color="transparent")
        pos_frame.pack(fill="x", padx=5)
        
        ctk.CTkLabel(pos_frame, text="Texto:").pack(side="left", padx=5)
        self.annot_text = ctk.CTkEntry(pos_frame, width=150)
        self.annot_text.pack(side="left", padx=5)
        
        ctk.CTkLabel(pos_frame, text="Página:").pack(side="left", padx=5)
        self.annot_page = ctk.CTkEntry(pos_frame, width=50)
        self.annot_page.insert(0, "0")
        self.annot_page.pack(side="left", padx=5)
        
        ctk.CTkLabel(pos_frame, text="X:").pack(side="left", padx=5)
        self.annot_x = ctk.CTkEntry(pos_frame, width=50)
        self.annot_x.insert(0, "100")
        self.annot_x.pack(side="left", padx=5)
        
        ctk.CTkLabel(pos_frame, text="Y:").pack(side="left", padx=5)
        self.annot_y = ctk.CTkEntry(pos_frame, width=50)
        self.annot_y.insert(0, "100")
        self.annot_y.pack(side="left", padx=5)
        
        ctk.CTkButton(
            ann_frame,
            text="Agregar Anotación",
            command=self._add_annotation
        ).pack(pady=5)
        
        # Censurar
        redact_frame = ctk.CTkFrame(frame)
        redact_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(redact_frame, text="Censurar Área:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        
        redact_pos = ctk.CTkFrame(redact_frame, fg_color="transparent")
        redact_pos.pack(fill="x", padx=5)
        
        ctk.CTkLabel(redact_pos, text="Página:").pack(side="left", padx=5)
        self.redact_page = ctk.CTkEntry(redact_pos, width=50)
        self.redact_page.insert(0, "0")
        self.redact_page.pack(side="left", padx=5)
        
        ctk.CTkLabel(redact_pos, text="X:").pack(side="left", padx=5)
        self.redact_x = ctk.CTkEntry(redact_pos, width=50)
        self.redact_x.insert(0, "100")
        self.redact_x.pack(side="left", padx=5)
        
        ctk.CTkLabel(redact_pos, text="Y:").pack(side="left", padx=5)
        self.redact_y = ctk.CTkEntry(redact_pos, width=50)
        self.redact_y.insert(0, "100")
        self.redact_y.pack(side="left", padx=5)
        
        ctk.CTkLabel(redact_pos, text="Ancho:").pack(side="left", padx=5)
        self.redact_w = ctk.CTkEntry(redact_pos, width=50)
        self.redact_w.insert(0, "100")
        self.redact_w.pack(side="left", padx=5)
        
        ctk.CTkLabel(redact_pos, text="Alto:").pack(side="left", padx=5)
        self.redact_h = ctk.CTkEntry(redact_pos, width=50)
        self.redact_h.insert(0, "30")
        self.redact_h.pack(side="left", padx=5)
        
        ctk.CTkButton(
            redact_frame,
            text="Censurar",
            command=self._redact_area
        ).pack(pady=5)
    
    def _add_annotation(self) -> None:
        if not self._check_files():
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        result = self.on_process('add_annotation', self.files, {
            'text': self.annot_text.get(),
            'page': int(self.annot_page.get() or 0),
            'x': float(self.annot_x.get() or 100),
            'y': float(self.annot_y.get() or 100),
        })
        
        self._show_result(result)
    
    def _redact_area(self) -> None:
        if not self._check_files():
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        result = self.on_process('redact', self.files, {
            'page': int(self.redact_page.get() or 0),
            'x': float(self.redact_x.get() or 100),
            'y': float(self.redact_y.get() or 100),
            'width': float(self.redact_w.get() or 100),
            'height': float(self.redact_h.get() or 30),
        })
        
        self._show_result(result)
    
    # =========================================================================
    # TAB: TRANSFORMAR
    # =========================================================================
    def _setup_transform_tab(self) -> None:
        frame = self.tab_transform
        
        # Rotar
        rotate_frame = ctk.CTkFrame(frame)
        rotate_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(rotate_frame, text="Rotar páginas:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        
        rot_opts = ctk.CTkFrame(rotate_frame, fg_color="transparent")
        rot_opts.pack(fill="x", padx=5)
        
        self.rotate_var = ctk.StringVar(value="90")
        
        for deg in ["90", "180", "270"]:
            ctk.CTkRadioButton(
                rot_opts,
                text=f"{deg}°",
                variable=self.rotate_var,
                value=deg
            ).pack(side="left", padx=10)
        
        ctk.CTkLabel(rot_opts, text="Páginas (vacío=todas):").pack(side="left", padx=(20, 5))
        self.rotate_pages = ctk.CTkEntry(rot_opts, width=100)
        self.rotate_pages.pack(side="left", padx=5)
        
        ctk.CTkButton(
            rotate_frame,
            text="Rotar",
            command=self._rotate_pages
        ).pack(pady=5)
        
        # Reordenar
        reorder_frame = ctk.CTkFrame(frame)
        reorder_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(reorder_frame, text="Reordenar páginas:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        
        ctk.CTkLabel(reorder_frame, text="Nuevo orden (ej: 3,1,2):").pack(anchor="w", padx=10)
        self.reorder_input = ctk.CTkEntry(reorder_frame, width=200)
        self.reorder_input.pack(padx=10, pady=5)
        
        ctk.CTkButton(
            reorder_frame,
            text="Reordenar",
            command=self._reorder_pages
        ).pack(pady=5)
    
    def _rotate_pages(self) -> None:
        if not self._check_files():
            return
        
        degrees = int(self.rotate_var.get())
        
        pages = None
        if self.rotate_pages.get().strip():
            pages = [int(p) for p in self.rotate_pages.get().split(',')]
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        result = self.on_process('rotate', self.files, {
            'degrees': degrees,
            'pages': pages
        })
        
        self._show_result(result)
    
    def _reorder_pages(self) -> None:
        if not self._check_files():
            return
        
        order_str = self.reorder_input.get().strip()
        if not order_str:
            self.status_label.configure(text="Ingrese el orden de páginas", text_color="orange")
            return
        
        try:
            new_order = [int(p) for p in order_str.split(',')]
        except ValueError:
            self.status_label.configure(text="Orden inválido", text_color="red")
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        result = self.on_process('reorder', self.files, {
            'new_order': new_order
        })
        
        self._show_result(result)
    
    # =========================================================================
    # TAB: COMBINAR
    # =========================================================================
    def _setup_combine_tab(self) -> None:
        frame = self.tab_combine
        
        # Combinar
        merge_frame = ctk.CTkFrame(frame)
        merge_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(merge_frame, text="Combinar PDFs:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        
        ctk.CTkLabel(
            merge_frame,
            text="Seleccione múltiples PDFs en el selector de archivos",
            text_color="gray"
        ).pack(anchor="w", padx=10)
        
        ctk.CTkButton(
            merge_frame,
            text="Combinar en un PDF",
            command=self._merge_pdfs,
            height=40
        ).pack(pady=5)
        
        # Extraer
        extract_frame = ctk.CTkFrame(frame)
        extract_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(extract_frame, text="Extraer páginas:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        
        ctk.CTkLabel(extract_frame, text="Páginas (ej: 1,3,5 o 1-5):").pack(anchor="w", padx=10)
        self.extract_pages = ctk.CTkEntry(extract_frame, width=200)
        self.extract_pages.pack(padx=10, pady=5)
        
        ctk.CTkButton(
            extract_frame,
            text="Extraer",
            command=self._extract_pages
        ).pack(pady=5)
    
    def _merge_pdfs(self) -> None:
        if not self._check_files() or len(self.files) < 2:
            self.status_label.configure(text="Seleccione al menos 2 PDFs", text_color="orange")
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        result = self.on_process('merge', self.files, {})
        
        self._show_result(result)
    
    def _extract_pages(self) -> None:
        if not self._check_files():
            return
        
        pages_str = self.extract_pages.get().strip()
        if not pages_str:
            self.status_label.configure(text="Ingrese las páginas a extraer", text_color="orange")
            return
        
        # Parsear páginas (soporta: "1,3,5" o "1-5")
        pages = []
        try:
            if '-' in pages_str:
                # Rango
                parts = pages_str.split('-')
                start = int(parts[0])
                end = int(parts[1])
                pages = list(range(start, end + 1))
            else:
                # Coma-separated
                pages = [int(p.strip()) for p in pages_str.split(',')]
        except ValueError:
            self.status_label.configure(text="Formato de páginas inválido", text_color="red")
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        result = self.on_process('extract', self.files, {'pages': pages})
        
        self._show_result(result)
    
    # =========================================================================
    # TAB: NÚMEROS DE PÁGINA
    # =========================================================================
    def _setup_numbers_tab(self) -> None:
        frame = self.tab_numbers
        
        num_frame = ctk.CTkFrame(frame)
        num_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(num_frame, text="Agregar números de página:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        
        opts = ctk.CTkFrame(num_frame, fg_color="transparent")
        opts.pack(fill="x", padx=5)
        
        ctk.CTkLabel(opts, text="Posición:").pack(side="left", padx=5)
        self.num_position = ctk.CTkOptionMenu(opts, values=["footer", "header"], width=100)
        self.num_position.set("footer")
        self.num_position.pack(side="left", padx=5)
        
        ctk.CTkLabel(opts, text="Inicio:").pack(side="left", padx=5)
        self.num_start = ctk.CTkEntry(opts, width=50)
        self.num_start.insert(0, "1")
        self.num_start.pack(side="left", padx=5)
        
        ctk.CTkLabel(opts, text="Formato:").pack(side="left", padx=5)
        self.num_format = ctk.CTkEntry(opts, width=120)
        self.num_format.insert(0, "Página {n} de {total}")
        self.num_format.pack(side="left", padx=5)
        
        ctk.CTkButton(
            num_frame,
            text="Agregar Números",
            command=self._add_page_numbers,
            height=40
        ).pack(pady=10)
    
    def _add_page_numbers(self) -> None:
        if not self._check_files():
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        result = self.on_process('page_numbers', self.files, {
            'position': self.num_position.get(),
            'start': int(self.num_start.get() or 1),
            'format': self.num_format.get() or "Página {n} de {total}",
        })
        
        self._show_result(result)
    
    # =========================================================================
    # TAB: SEGURIDAD
    # =========================================================================
    def _setup_security_tab(self) -> None:
        frame = self.tab_security
        
        # Bloquear
        lock_frame = ctk.CTkFrame(frame)
        lock_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(lock_frame, text="Bloquear PDF:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        
        pwd_frame = ctk.CTkFrame(lock_frame, fg_color="transparent")
        pwd_frame.pack(fill="x", padx=5)
        
        ctk.CTkLabel(pwd_frame, text="Contraseña:").pack(side="left", padx=5)
        self.lock_password = ctk.CTkEntry(pwd_frame, show="*", width=150)
        self.lock_password.pack(side="left", padx=5)
        
        ctk.CTkButton(
            lock_frame,
            text="Bloquear",
            command=self._encrypt_pdf,
            height=40
        ).pack(pady=5)
        
        # Desbloquear
        unlock_frame = ctk.CTkFrame(frame)
        unlock_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(unlock_frame, text="Desbloquear PDF:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        
        unlock_pwd = ctk.CTkFrame(unlock_frame, fg_color="transparent")
        unlock_pwd.pack(fill="x", padx=5)
        
        ctk.CTkLabel(unlock_pwd, text="Contraseña:").pack(side="left", padx=5)
        self.unlock_password = ctk.CTkEntry(unlock_pwd, show="*", width=150)
        self.unlock_password.pack(side="left", padx=5)
        
        ctk.CTkButton(
            unlock_frame,
            text="Desbloquear",
            command=self._decrypt_pdf,
            height=40
        ).pack(pady=5)
    
    def _encrypt_pdf(self) -> None:
        if not self._check_files():
            return
        
        password = self.lock_password.get()
        if not password:
            self.status_label.configure(text="Ingrese una contraseña", text_color="orange")
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        result = self.on_process('encrypt', self.files, {'password': password})
        
        self._show_result(result)
    
    def _decrypt_pdf(self) -> None:
        if not self._check_files():
            return
        
        password = self.unlock_password.get()
        if not password:
            self.status_label.configure(text="Ingrese la contraseña", text_color="orange")
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        result = self.on_process('decrypt', self.files, {'password': password})
        
        self._show_result(result)
    
    # =========================================================================
    # TAB: OPTIMIZAR
    # =========================================================================
    def _setup_optimize_tab(self) -> None:
        frame = self.tab_optimize
        
        # Comprimir
        compress_frame = ctk.CTkFrame(frame)
        compress_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(compress_frame, text="Comprimir PDF:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        
        comp_opts = ctk.CTkFrame(compress_frame, fg_color="transparent")
        comp_opts.pack(fill="x", padx=5)
        
        ctk.CTkLabel(comp_opts, text="Nivel:").pack(side="left", padx=5)
        self.compress_level = ctk.CTkOptionMenu(comp_opts, values=["low", "medium", "high"], width=100)
        self.compress_level.set("medium")
        self.compress_level.pack(side="left", padx=5)
        
        ctk.CTkButton(
            compress_frame,
            text="Comprimir",
            command=self._compress_pdf,
            height=40
        ).pack(pady=5)
        
        # Limpiar metadatos
        clean_frame = ctk.CTkFrame(frame)
        clean_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(clean_frame, text="Limpiar metadatos:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        
        ctk.CTkButton(
            clean_frame,
            text="Limpiar Metadatos",
            command=self._clean_metadata,
            height=40
        ).pack(pady=5)
    
    def _compress_pdf(self) -> None:
        if not self._check_files():
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        result = self.on_process('compress', self.files, {
            'level': self.compress_level.get()
        })
        
        self._show_result(result)
    
    def _clean_metadata(self) -> None:
        if not self._check_files():
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        result = self.on_process('clean_metadata', self.files, {})
        
        self._show_result(result)
    
    # =========================================================================
    # TAB: INFO
    # =========================================================================
    def _setup_info_tab(self) -> None:
        frame = self.tab_info
        
        info_frame = ctk.CTkFrame(frame)
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(info_frame, text="Información del PDF:", font=ctk.CTkFont(weight="bold")).pack(anchor="n", pady=5)
        
        # Área de texto para mostrar info
        self.info_text = ctk.CTkTextbox(info_frame, width=400, height=200)
        self.info_text.pack(padx=10, pady=10, fill="both", expand=True)
        
        ctk.CTkButton(
            info_frame,
            text="Ver Información",
            command=self._show_pdf_info
        ).pack(pady=5)
    
    def _show_pdf_info(self) -> None:
        if not self._check_files():
            return
        
        if not self.files:
            self.status_label.configure(text="Seleccione un PDF", text_color="orange")
            return
        
        # Mostrar info del primer archivo
        from tools.pdf_tool.processor import get_pdf_info
        
        info = get_pdf_info(self.files[0])
        
        self.info_text.delete("1.0", tk.END)
        
        if info.get('success'):
            self.info_text.insert("1.0", f"""Información del PDF:
─────────────────────────────────
Archivo: {info.get('file_name', 'N/A')}
Tamaño: {info.get('file_size', 0)} bytes
Páginas: {info.get('num_pages', 0)}
Encriptado: {'Sí' if info.get('is_encrypted') else 'No'}

Metadatos:
─────────────────────────────────
Título: {info.get('title', 'N/A')}
Autor: {info.get('author', 'N/A')}
Creador: {info.get('creator', 'N/A')}
Productor: {info.get('producer', 'N/A')}
Fecha creación: {info.get('creation_date', 'N/A')}
""")
            
            # Info de páginas
            pages = info.get('pages', [])
            if pages:
                self.info_text.insert(tk.END, "\nPáginas:\n─────────────────────────────────\n")
                for p in pages[:10]:  # Mostrar max 10
                    self.info_text.insert(tk.END, f"Página {p['page_num']}: Rotación={p['rotation']}°\n")
        else:
            self.info_text.insert("1.0", f"Error: {info.get('error', 'Error desconocido')}")
    
    # =========================================================================
    # UTILIDADES
    # =========================================================================
    def _show_result(self, result: Dict[str, Any]) -> None:
        """Muestra el resultado del procesamiento."""
        if result.get('success'):
            self.status_label.configure(
                text=result.get('message', 'Completado'),
                text_color="green"
            )
        else:
            self.status_label.configure(
                text=result.get('message', 'Error'),
                text_color="red"
            )