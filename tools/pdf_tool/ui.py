import os
import logging
from core.help_panel import add_help
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import List, Callable, Dict, Any, Optional
from PIL import Image, ImageTk

# Import BaseToolUI from core
from core.base_tool_ui import BaseToolUI


logger = logging.getLogger(__name__)


# =============================================================================
# UTILIDADES - THUMBNAIL
# =============================================================================

def get_pdf_thumbnail(file_path: str, size: tuple = (200, 250)) -> Optional[Image.Image]:
    """
    Genera un thumbnail de la primera página de un PDF usando Fitz.
    
    Args:
        file_path: Ruta al archivo PDF
        size: Tamaño del thumbnail (ancho, alto)
        
    Returns:
        PIL Image o None si falla
    """
    try:
        import fitz
        doc = fitz.open(file_path)
        if doc.page_count < 1:
            doc.close()
            return None
        
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))  # Reducir resolución
        img = pix.pil_image()
        doc.close()
        
        # Redimensionar
        img.thumbnail(size, Image.Resampling.LANCZOS)
        return img
    except Exception as e:
        logger.warning(f"Error generando thumbnail: {e}")
        return None


class PDFToolUI(BaseToolUI):
    """UI para procesamiento de archivos PDF."""
    
    def __init__(self, master, on_process: Callable, **kwargs):
        # Call BaseToolUI __init__ which calls _setup_ui()
        super().__init__(master, on_process, **kwargs)
        
        # Build tool-specific tabs after base selector
        self._build_tabs()
    
    def _build_tabs(self) -> None:
        """Build tool-specific tabs."""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Reorganizar pestañas en orden funcional:
        # 1. INFO (propiedades)
        # 2. EDITAR (extract, reorder)
        # 3. TRANSFORMAR (rotate, optimize)
        # 4. WATERMARK (add/remove)
        # 5. SEGURIDAD (password, encrypt)
        # 6. COMBINAR (merge)
        
        self.tab_info = self.tabview.add("Info")
        self.tab_edit = self.tabview.add("Editar")
        self.tab_transform = self.tabview.add("Transformar")
        self.tab_watermark = self.tabview.add("Watermark")
        self.tab_security = self.tabview.add("Seguridad")
        self.tab_combine = self.tabview.add("Combinar")
        self.tab_numbers = self.tabview.add("Números")
        self.tab_optimize = self.tabview.add("Optimizar")
        self.tab_pipeline = self.tabview.add("Pipeline")
        
        # Configurar cada tab
        self._setup_info_tab()
        self._setup_edit_tab()
        self._setup_transform_tab()
        self._setup_watermark_tab()
        self._setup_security_tab()
        self._setup_combine_tab()
        self._setup_numbers_tab()
        self._setup_optimize_tab()
        self._setup_pipeline_tab()
    
    def _get_file_label(self) -> str:
        """Override: Label for file section."""
        return "Archivos PDF:"
    
    def _get_file_dialog_filters(self) -> List[tuple]:
        """Override: Filters for file dialog."""
        return [
            ("PDF files", "*.pdf"),
            ("All files", "*.*")
        ]
    
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
                "1. 📥 Agregar PDFs con 'Agregar PDFs...'",
                "2. 📑 Elegir operación (Watermark/Editar/Transformar/etc)",
                "3. ⚙️ Configurar opciones",
                "4. ▶️ Click en ejecutar"
            ],
            warnings=[
                "⚠️ PDFs encriptados requieren contraseña primero",
                "⚠️ Combinar/extraer son destructivos - crea nuevo archivo",
                "⚠️ Watermark modifica el original"
            ]
        )
        help_panel.pack(fill="x", padx=10, pady=5)
        
        # File selector (from BaseToolUI)
        self._setup_file_selector()
        
        # Status label (from BaseToolUI sets self.status_label)
    
    # =========================================================================
    # TAB: WATERMARK
    # =========================================================================
    def _setup_watermark_tab(self) -> None:
        frame = self.tab_watermark
        
        # Toggle para tipo de watermark (texto vs imagen)
        self.watermark_type = ctk.StringVar(value="text")
        
        type_frame = ctk.CTkFrame(frame)
        type_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(type_frame, text="Tipo:").pack(side="left", padx=5)
        ctk.CTkRadioButton(
            type_frame,
            text="Texto",
            variable=self.watermark_type,
            value="text",
            command=self._update_watermark_inputs
        ).pack(side="left", padx=5)
        ctk.CTkRadioButton(
            type_frame,
            text="Imagen",
            variable=self.watermark_type,
            value="image",
            command=self._update_watermark_inputs
        ).pack(side="left", padx=5)
        
        # Contenedor para inputs (se actualiza según el tipo)
        self.watermark_inputs_frame = ctk.CTkFrame(frame)
        self.watermark_inputs_frame.pack(fill="x", padx=10, pady=5)
        
        # Texto
        text_frame = ctk.CTkFrame(self.watermark_inputs_frame)
        text_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(text_frame, text="Texto:").pack(side="left", padx=5)
        self.watermark_text = ctk.CTkEntry(text_frame, width=200)
        self.watermark_text.insert(0, "WATERMARK")
        self.watermark_text.pack(side="left", padx=5)
        
        # Imagen (inicialmente oculto)
        self.image_frame = ctk.CTkFrame(self.watermark_inputs_frame)
        
        ctk.CTkLabel(self.image_frame, text="Imagen:").pack(side="left", padx=5)
        self.watermark_image_path = ctk.CTkEntry(self.image_frame, width=200)
        self.watermark_image_path.pack(side="left", padx=5)
        
        ctk.CTkButton(
            self.image_frame,
            text="Examinar...",
            command=self._select_watermark_image,
            width=80
        ).pack(side="left", padx=5)
        
        # Opciones avanzadas
        options_frame = ctk.CTkFrame(frame)
        options_frame.pack(fill="x", padx=10, pady=5)
        
        # Tamaño de fuente
        ctk.CTkLabel(options_frame, text="Tamaño:").pack(side="left", padx=5)
        self.watermark_size = ctk.CTkEntry(options_frame, width=60)
        self.watermark_size.insert(0, "48")
        self.watermark_size.pack(side="left", padx=5)
        
        # Color
        ctk.CTkLabel(options_frame, text="Color:").pack(side="left", padx=5)
        self.watermark_color = ctk.CTkEntry(options_frame, width=80)
        self.watermark_color.insert(0, "#888888")
        self.watermark_color.pack(side="left", padx=5)
        
        # opacity slider (0-100)
        opacity_frame = ctk.CTkFrame(frame)
        opacity_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(opacity_frame, text="Opacidad:").pack(side="left", padx=5)
        self.watermark_opacity_slider = ctk.CTkSlider(
            opacity_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self._on_opacity_slider_change
        )
        self.watermark_opacity_slider.set(30)
        self.watermark_opacity_slider.pack(side="left", padx=5, fill="x", expand=True)
        
        self.watermark_opacity_label = ctk.CTkLabel(opacity_frame, text="30%", width=50)
        self.watermark_opacity_label.pack(side="left", padx=5)
        
        # Rotation slider (0-360)
        rotation_frame = ctk.CTkFrame(frame)
        rotation_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(rotation_frame, text="Rotación:").pack(side="left", padx=5)
        self.watermark_rotation_slider = ctk.CTkSlider(
            rotation_frame,
            from_=0,
            to=360,
            number_of_steps=36,
            command=self._on_rotation_slider_change
        )
        self.watermark_rotation_slider.set(45)
        self.watermark_rotation_slider.pack(side="left", padx=5, fill="x", expand=True)
        
        self.watermark_rotation_label = ctk.CTkLabel(rotation_frame, text="45°", width=50)
        self.watermark_rotation_label.pack(side="left", padx=5)
        
        # Position
        position_frame = ctk.CTkFrame(frame)
        position_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(position_frame, text="Posición:").pack(side="left", padx=5)
        self.watermark_position = ctk.CTkOptionMenu(
            position_frame,
            values=["center", "top-left", "top-right", "bottom-left", "bottom-right", "diagonal", "custom"],
            width=120
        )
        self.watermark_position.set("center")
        self.watermark_position.pack(side="left", padx=5)
        
        ctk.CTkLabel(position_frame, text="X:").pack(side="left", padx=5)
        self.watermark_pos_x = ctk.CTkEntry(position_frame, width=60)
        self.watermark_pos_x.insert(0, "")
        self.watermark_pos_x.pack(side="left", padx=5)
        
        ctk.CTkLabel(position_frame, text="Y:").pack(side="left", padx=5)
        self.watermark_pos_y = ctk.CTkEntry(position_frame, width=60)
        self.watermark_pos_y.insert(0, "")
        self.watermark_pos_y.pack(side="left", padx=5)
        
        # Botones
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Aplicar Watermark",
            command=self._apply_text_watermark,
            height=40
        ).pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(
            btn_frame,
            text="Quitar Watermarks",
            command=self._remove_watermark,
            height=40
        ).pack(side="left", padx=5, fill="x", expand=True)
    
    def _on_opacity_slider_change(self, value: float) -> None:
        """Actualiza la etiqueta de opacidad."""
        self.watermark_opacity_label.configure(text=f"{int(value)}%")
    
    def _on_rotation_slider_change(self, value: float) -> None:
        """Actualiza la etiqueta de rotación."""
        self.watermark_rotation_label.configure(text=f"{int(value)}°")
    
    def _update_watermark_inputs(self) -> None:
        """Actualiza los inputs según el tipo de watermark."""
        # Limpiar frame de inputs
        for widget in self.watermark_inputs_frame.winfo_children():
            widget.destroy()
        
        if self.watermark_type.get() == "text":
            text_frame = ctk.CTkFrame(self.watermark_inputs_frame)
            text_frame.pack(fill="x", padx=5, pady=5)
            
            ctk.CTkLabel(text_frame, text="Texto:").pack(side="left", padx=5)
            self.watermark_text = ctk.CTkEntry(text_frame, width=200)
            self.watermark_text.insert(0, "WATERMARK")
            self.watermark_text.pack(side="left", padx=5)
        else:
            img_frame = ctk.CTkFrame(self.watermark_inputs_frame)
            img_frame.pack(fill="x", padx=5, pady=5)
            
            ctk.CTkLabel(img_frame, text="Imagen:").pack(side="left", padx=5)
            self.watermark_image_path = ctk.CTkEntry(img_frame, width=200)
            self.watermark_image_path.pack(side="left", padx=5)
            
            ctk.CTkButton(
                img_frame,
                text="Examinar...",
                command=self._select_watermark_image,
                width=80
            ).pack(side="left", padx=5)
    
    def _select_watermark_image(self) -> None:
        """Selecciona una imagen para watermark."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos", "*.*")]
        )
        if file_path:
            self.watermark_image_path.delete(0, tk.END)
            self.watermark_image_path.insert(0, file_path)
    
    def _apply_text_watermark(self) -> None:
        if not self._check_files():
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        # Determinar tipo de watermark
        if self.watermark_type.get() == "image":
            image_path = self.watermark_image_path.get()
            if not image_path:
                self.status_label.configure(text="Seleccione una imagen", text_color="#FFA500")
                return
            
            result = self.on_process('image_watermark', self.files, {
                'image_path': image_path,
                'scale': 0.5,
                'opacity': self.watermark_opacity_slider.get() / 100.0,
                'position': self.watermark_position.get(),
            })
        else:
            text = self.watermark_text.get() or "WATERMARK"
            
            # Posición personalizada
            position = self.watermark_position.get()
            position_x = None
            position_y = None
            
            if position == 'custom':
                try:
                    position_x = float(self.watermark_pos_x.get()) if self.watermark_pos_x.get() else None
                    position_y = float(self.watermark_pos_y.get()) if self.watermark_pos_y.get() else None
                except ValueError:
                    self.status_label.configure(text="Coordenadas inválidas", text_color="red")
                    return
            
            result = self.on_process('text_watermark', self.files, {
                'text': text,
                'font_size': int(self.watermark_size.get() or 48),
                'color': self.watermark_color.get() or '#888888',
                'opacity': self.watermark_opacity_slider.get() / 100.0,
                'rotation': int(self.watermark_rotation_slider.get()),
                'position': position,
                'position_x': position_x,
                'position_y': position_y,
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
        
        # Extraer rango de páginas
        extract_frame = ctk.CTkFrame(frame)
        extract_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(extract_frame, text="Extraer páginas:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        
        range_frame = ctk.CTkFrame(extract_frame, fg_color="transparent")
        range_frame.pack(fill="x", padx=5)
        
        ctk.CTkLabel(range_frame, text="Desde:").pack(side="left", padx=5)
        self.extract_start = ctk.CTkEntry(range_frame, width=50)
        self.extract_start.insert(0, "1")
        self.extract_start.pack(side="left", padx=5)
        
        ctk.CTkLabel(range_frame, text="Hasta:").pack(side="left", padx=5)
        self.extract_end = ctk.CTkEntry(range_frame, width=50)
        self.extract_end.insert(0, "1")
        self.extract_end.pack(side="left", padx=5)
        
        ctk.CTkButton(
            extract_frame,
            text="Extraer Rango",
            command=self._extract_range
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
    
    def _extract_range(self) -> None:
        """Extrae un rango de páginas."""
        if not self._check_files():
            return
        
        try:
            start = int(self.extract_start.get())
            end = int(self.extract_end.get())
        except ValueError:
            self.status_label.configure(text="Números de página inválidos", text_color="red")
            return
        
        if start < 1 or end < 1:
            self.status_label.configure(text="Los números deben ser >= 1", text_color="red")
            return
        
        if start > end:
            self.status_label.configure(text="Inicio debe ser menor que fin", text_color="red")
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        result = self.on_process('extract_range', self.files, {
            'start': start,
            'end': end,
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
            self.status_label.configure(text="Ingrese el orden de páginas", text_color="#FFA500")
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
            self.status_label.configure(text="Seleccione al menos 2 PDFs", text_color="#FFA500")
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        result = self.on_process('merge', self.files, {})
        
        self._show_result(result)
    
    def _extract_pages(self) -> None:
        if not self._check_files():
            return
        
        pages_str = self.extract_pages.get().strip()
        if not pages_str:
            self.status_label.configure(text="Ingrese las páginas a extraer", text_color="#FFA500")
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
            self.status_label.configure(text="Ingrese una contraseña", text_color="#FFA500")
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        result = self.on_process('encrypt', self.files, {'password': password})
        
        self._show_result(result)
    
    def _decrypt_pdf(self) -> None:
        if not self._check_files():
            return
        
        password = self.unlock_password.get()
        if not password:
            self.status_label.configure(text="Ingrese la contraseña", text_color="#FFA500")
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
    
    # =========================================================================
    # TAB: PIPELINE
    # =========================================================================
    def _setup_pipeline_tab(self) -> None:
        """Configura el tab de Pipeline."""
        frame = self.tab_pipeline
        self.pipeline_operations = []  # Lista de operaciones acumuladas
        
        # Frame principal
        main_frame = ctk.CTkFrame(frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        ctk.CTkLabel(
            main_frame,
            text="Pipeline de Operaciones",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(0, 10))
        
        # Frame para agregar operaciones
        add_frame = ctk.CTkFrame(main_frame)
        add_frame.pack(fill="x", pady=5)
        
        # Selector de tipo de operación
        ctk.CTkLabel(add_frame, text="Operación:").pack(side="left", padx=5)
        self.pipeline_op_type = ctk.CTkOptionMenu(
            add_frame,
            values=["reorder", "watermark", "rotate", "extract"],
            width=100
        )
        self.pipeline_op_type.set("reorder")
        self.pipeline_op_type.pack(side="left", padx=5)
        
        # Parámetros dinámica según tipo
        params_frame = ctk.CTkFrame(main_frame)
        params_frame.pack(fill="x", pady=5)
        
        # Reorder input
        self.pipeline_reorder_frame = ctk.CTkFrame(params_frame)
        self.pipeline_reorder_frame.pack(fill="x", padx=5)
        
        ctk.CTkLabel(self.pipeline_reorder_frame, text="Orden (ej: 3,1,2):").pack(side="left", padx=5)
        self.pipeline_reorder_input = ctk.CTkEntry(self.pipeline_reorder_frame, width=150)
        self.pipeline_reorder_input.pack(side="left", padx=5)
        
        # Watermark input
        self.pipeline_wm_frame = ctk.CTkFrame(params_frame)
        
        ctk.CTkLabel(self.pipeline_wm_frame, text="Texto:").pack(side="left", padx=5)
        self.pipeline_wm_text = ctk.CTkEntry(self.pipeline_wm_frame, width=150)
        self.pipeline_wm_text.insert(0, "DRAFT")
        self.pipeline_wm_text.pack(side="left", padx=5)
        
        # Rotate input
        self.pipeline_rotate_frame = ctk.CTkFrame(params_frame)
        
        ctk.CTkLabel(self.pipeline_rotate_frame, text="Grados:").pack(side="left", padx=5)
        self.pipeline_rotate_deg = ctk.CTkOptionMenu(
            self.pipeline_rotate_frame,
            values=["90", "180", "270"],
            width=80
        )
        self.pipeline_rotate_deg.set("90")
        self.pipeline_rotate_deg.pack(side="left", padx=5)
        
        # Extract input
        self.pipeline_extract_frame = ctk.CTkFrame(params_frame)
        
        ctk.CTkLabel(self.pipeline_extract_frame, text="Páginas (ej: 1,3,5):").pack(side="left", padx=5)
        self.pipeline_extract_input = ctk.CTkEntry(self.pipeline_extract_frame, width=150)
        self.pipeline_extract_input.pack(side="left", padx=5)
        
        # Botón agregar
        ctk.CTkButton(
            main_frame,
            text="Agregar a Pipeline",
            command=self._add_to_pipeline,
            height=35
        ).pack(pady=10, fill="x")
        
        # Lista de operaciones
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(list_frame, text="Operaciones acumuladas:").pack(anchor="w", pady=5)
        
        self.pipeline_listbox = ctk.CTkTextbox(list_frame, height=150)
        self.pipeline_listbox.pack(padx=10, pady=5, fill="both", expand=True)
        
        # Botones de acción
        action_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        action_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(
            action_frame,
            text="Limpiar",
            command=self._clear_pipeline,
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            action_frame,
            text="Ejecutar Pipeline",
            command=self._execute_pipeline,
            width=150,
            fg_color="#2CC985"
        ).pack(side="left", padx=5, fill="x", expand=True)
        
        # Actualizar inputs visibles
        self._update_pipeline_inputs()
    
    def _update_pipeline_inputs(self) -> None:
        """Actualiza los inputs según el tipo de operación seleccionada."""
        # Ocultar todos
        self.pipeline_reorder_frame.pack_forget()
        self.pipeline_wm_frame.pack_forget()
        self.pipeline_rotate_frame.pack_forget()
        self.pipeline_extract_frame.pack_forget()
        
        op_type = self.pipeline_op_type.get()
        
        if op_type == "reorder":
            self.pipeline_reorder_frame.pack(fill="x", padx=5)
        elif op_type == "watermark":
            self.pipeline_wm_frame.pack(fill="x", padx=5)
        elif op_type == "rotate":
            self.pipeline_rotate_frame.pack(fill="x", padx=5)
        elif op_type == "extract":
            self.pipeline_extract_frame.pack(fill="x", padx=5)
    
    def _add_to_pipeline(self) -> None:
        """Agrega una operación al pipeline."""
        if not self._check_files():
            self.status_label.configure(
                text="Seleccione un PDF primero",
                text_color="#FFA500"
            )
            return
        
        op_type = self.pipeline_op_type.get()
        params = {}
        
        if op_type == "reorder":
            order_str = self.pipeline_reorder_input.get().strip()
            if not order_str:
                self.status_label.configure(
                    text="Ingrese el orden de páginas",
                    text_color="#FFA500"
                )
                return
            try:
                params['new_order'] = [int(p) for p in order_str.split(',')]
            except ValueError:
                self.status_label.configure(
                    text="Orden inválido",
                    text_color="red"
                )
                return
        
        elif op_type == "watermark":
            text = self.pipeline_wm_text.get().strip()
            if not text:
                text = "DRAFT"
            params['text'] = text
        
        elif op_type == "rotate":
            params['degrees'] = int(self.pipeline_rotate_deg.get())
        
        elif op_type == "extract":
            pages_str = self.pipeline_extract_input.get().strip()
            if not pages_str:
                self.status_label.configure(
                    text="Ingrese las páginas",
                    text_color="#FFA500"
                )
                return
            try:
                params['pages'] = [int(p.strip()) for p in pages_str.split(',')]
            except ValueError:
                self.status_label.configure(
                    text="Páginas inválidas",
                    text_color="red"
                )
                return
        
        # Agregar a la lista
        self.pipeline_operations.append({
            'type': op_type,
            'params': params
        })
        
        # Actualizar listbox
        self._refresh_pipeline_list()
        
        self.status_label.configure(
            text=f"Operación '{op_type}' añadida al pipeline",
            text_color="green"
        )
        
        # Limpiar inputs
        if op_type == "reorder":
            self.pipeline_reorder_input.delete(0, tk.END)
        elif op_type == "watermark":
            self.pipeline_wm_text.delete(0, tk.END)
            self.pipeline_wm_text.insert(0, "DRAFT")
        elif op_type == "extract":
            self.pipeline_extract_input.delete(0, tk.END)
    
    def _refresh_pipeline_list(self) -> None:
        """Actualiza la lista de operaciones en el listbox."""
        self.pipeline_listbox.delete("1.0", tk.END)
        
        for i, op in enumerate(self.pipeline_operations):
            op_type = op['type']
            params = op['params']
            
            if op_type == "reorder":
                desc = f"{i+1}. Reorder: {params.get('new_order', [])}"
            elif op_type == "watermark":
                desc = f"{i+1}. Watermark: {params.get('text', '')}"
            elif op_type == "rotate":
                desc = f"{i+1}. Rotate: {params.get('degrees', 0)}°"
            elif op_type == "extract":
                desc = f"{i+1}. Extract: {params.get('pages', [])}"
            else:
                desc = f"{i+1}. {op_type}"
            
            self.pipeline_listbox.insert(tk.END, desc + "\n")
        
        # Mostrar total
        if self.pipeline_operations:
            self.pipeline_listbox.insert(tk.END, f"\nTotal: {len(self.pipeline_operations)} operaciones")
    
    def _clear_pipeline(self) -> None:
        """Limpia las operaciones acumuladas."""
        self.pipeline_operations.clear()
        self._refresh_pipeline_list()
        
        self.status_label.configure(
            text="Pipeline limpiado",
            text_color="gray"
        )
    
    def _execute_pipeline(self) -> None:
        """Ejecuta todas las operaciones del pipeline."""
        if not self._check_files():
            self.status_label.configure(
                text="Seleccione un PDF primero",
                text_color="#FFA500"
            )
            return
        
        if not self.pipeline_operations:
            self.status_label.configure(
                text="No hay operaciones en el pipeline",
                text_color="#FFA500"
            )
            return
        
        self.status_label.configure(
            text="Ejecutando pipeline...",
            text_color="blue"
        )
        
        # Ejecutar pipeline
        from tools.pdf_tool.modules.pipeline import execute_pipeline_operations
        
        result = execute_pipeline_operations(
            self.files[0],
            self.pipeline_operations
        )
        
        if result.get('success'):
            output_file = result.get('output_file')
            self.status_label.configure(
                text=f"Pipeline completado: {result.get('message', '')}",
                text_color="green"
            )
            
            # Limpiar y actualizar archivos
            self.pipeline_operations.clear()
            self._refresh_pipeline_list()
            
            # Agregar output al selector si existe
            if output_file and os.path.exists(output_file):
                # Actualizar file list con el resultado
                self.files = [output_file]
                self._update_file_list()
        else:
            self.status_label.configure(
                text=f"Error: {result.get('error', 'Error desconocido')}",
                text_color="red"
            )
    
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
            self.status_label.configure(text="Seleccione un PDF", text_color="#FFA500")
            return
        
        from tools.pdf_tool.processor import get_pdf_info
        
        self.info_text.delete("1.0", tk.END)
        
        # Procesar TODOS los archivos
        for file_path in self.files:
            info = get_pdf_info(file_path)
            
            if info.get('success'):
                self.info_text.insert(tk.END, f"""Información del PDF:
─────────────────────────────────────
Archivo: {info.get('file_name', 'N/A')}
Tamaño: {info.get('file_size', 0)} bytes
Páginas: {info.get('num_pages', 0)}
Encriptado: {'Sí' if info.get('is_encrypted') else 'No'}

Metadatos:
─────────────────────────────────────
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
                
                self.info_text.insert(tk.END, "\n" + "="*35 + "\n\n")
            else:
                self.info_text.insert(tk.END, f"Error con {info.get('file_name', file_path)}: {info.get('error', 'Error desconocido')}\n\n")
    
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