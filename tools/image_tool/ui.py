"""
UI: ImageTool — 7 tabs CTkTabview.
Procesamiento Digital de Imágenes con fases 1-7.
Preview por pestaña - Máxima A0 (<30 líneas), A7 (stateless), A12 (observabilidad).
"""
import os
from pathlib import Path
from typing import List, Dict, Any
import numpy as np

import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk

from core.base_tool_ui import BaseToolUI
from core.help_panel import add_help

# Colormap options for pseudocolor
COLORMAP_OPTIONS = [
    'jet', 'ocean', 'summer', 'winter', 'autumn', 'bone',
    'cool', 'copper', 'flag', 'hsv', 'inferno', 'magma',
    'plasma', 'turbo', 'viridis'
]


class ImageToolUI(BaseToolUI):
    """UI for Image Processing Tool with 7 tabs."""

    def __init__(self, master, on_process, **kwargs):
        self.current_image_path: str = None
        self.current_image_data: Dict[str, Any] = None
        super().__init__(master, on_process, **kwargs)

    def _setup_ui(self) -> None:
        """Setup main UI with title and help."""
        # Title
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=10, pady=(10, 0))

        ctk.CTkLabel(
            title_frame,
            text="Procesamiento Digital de Imágenes",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=5)

        add_help(
            self,
            description="🖼️ PDI: 7 fases de procesamiento digital de imágenes",
            usage=[
                "1. 📥 Carga una imagen (archivo o URL)",
                "2. 📑 Explorá las 7 fases de PDI:",
                "   - Adquisición: cargar imagen",
                "   - Geometría: grayscale, HSV, crop, resize, rotate",
                "   - Mejora: histograma, brillo/contraste, gamma",
                "   - Filtros: gauss, median, mean",
                "   - Morfología: erode, dilate, open, close",
                "   - Bordes: sobel, prewitt, laplacian, canny",
                "   - Análisis: contours, Haar detect",
                "3. 👁️ El preview aparece en la pestaña de cada operación"
            ]
        ).pack(fill="x", padx=10, pady=5)

        # Tab view with 7 tabs
        self.tab_view = ctk.CTkTabview(self, fg_color="transparent")
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=5)

        tab_names = [
            "Adquisición",
            "Geometría",
            "Mejora",
            "Filtros",
            "Morfología",
            "Bordes",
            "Análisis"
        ]

        for tab_name in tab_names:
            self.tab_view.add(tab_name)

        # Preview labels dict - one per tab
        self._preview_labels: Dict[str, ctk.CTkLabel] = {}
        self._histogram_label: ctk.CTkLabel = None  # Solo en Mejora

        # Setup each tab
        self._setup_tab_adquisicion()
        self._setup_tab_geometria()
        self._setup_tab_mejora()
        self._setup_tab_filtros()
        self._setup_tab_morfologia()
        self._setup_tab_bordes()
        self._setup_tab_analisis()

        # Feedback frame (visible en todos los tabs)
        self.feedback_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.feedback_frame.pack(fill="x", padx=10, pady=(5, 0))

        self.status_label = ctk.CTkLabel(self.feedback_frame, text="Sin imagen cargada", text_color="gray")
        self.status_label.pack()

        self.progress_bar = ctk.CTkProgressBar(self.feedback_frame, mode='indeterminate')
        self.progress_bar.set(0)

    # === Helpers ===
    def _resize_for_preview(self, pil_img: Image.Image):
        """Redimensiona imagen para preview (CTkImage o ImageTk.PhotoImage)."""
        w, h = pil_img.size
        scale = min(300 / w, 200 / h, 1.0)
        new_w, new_h = int(w * scale), int(h * scale)
        try:
            return ctk.CTkImage(pil_img, size=(new_w, new_h))
        except Exception:
            return ImageTk.PhotoImage(pil_img.resize((new_w, new_h), Image.LANCZOS))

    def _show_in_tab(self, tab_name: str, pil_img: Image.Image) -> None:
        """Muestra imagen en el label de la pestaña."""
        label = self._preview_labels.get(tab_name)
        if label:
            photo = self._resize_for_preview(pil_img)
            label.configure(image=photo, text="")
            label._photo = photo  # keep reference
            label.pack(fill="both", expand=True)

    # === Tab 1: Adquisición ===
    def _setup_tab_adquisicion(self) -> None:
        """Tab 1: file picker, URL input."""
        tab = self.tab_view.tab("Adquisición")

        # File picker
        ctk.CTkButton(
            tab,
            text="📂 Seleccionar imagen",
            command=self._on_select_image,
            height=40
        ).pack(pady=10)

        # File path display
        self.path_label = ctk.CTkLabel(tab, text="", text_color="gray", font=ctk.CTkFont(size=10))
        self.path_label.pack(pady=2)

        # URL input frame
        url_frame = ctk.CTkFrame(tab, fg_color="transparent")
        url_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(url_frame, text="URL:").pack(side="left", padx=5)
        self.url_entry = ctk.CTkEntry(url_frame, width=250, placeholder_text="https://ejemplo.com/imagen.jpg")
        self.url_entry.pack(side="left", fill="x", expand=True, padx=5)

        ctk.CTkButton(
            url_frame,
            text="Cargar",
            command=self._on_load_url,
            width=80
        ).pack(side="left", padx=5)

        # Clear image button
        ctk.CTkButton(
            tab,
            text="🗑️ Limpiar",
            command=self._on_clear_image,
            fg_color="#dc2626",
            height=30
        ).pack(pady=5)

        # Preview label for Adquisición
        preview_label = ctk.CTkLabel(tab, text="", fg_color="transparent")
        self._preview_labels["Adquisición"] = preview_label

    def _on_select_image(self) -> None:
        """File picker + carga de imagen."""
        files = filedialog.askopenfilenames(
            title="Seleccionar imagen",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.webp"),
                ("Todos los archivos", "*.*")
            ]
        )

        if files:
            self.current_image_path = files[0]
            self.status_label.configure(
                text=f"✅ {Path(self.current_image_path).name}",
                text_color="green"
            )
            self.path_label.configure(text=self.current_image_path)
            from tools.image_tool.processor import _load_from_file
            result = _load_from_file(self.current_image_path)
            if result['success']:
                self.current_image_data = result['image_data']
                self._show_preview_adquisicion()
            else:
                self.status_label.configure(
                    text=f"❌ {result.get('error', 'Error')}",
                    text_color="red"
                )

    def _on_load_url(self) -> None:
        """Load image from URL."""
        url = self.url_entry.get().strip()
        if not url:
            self.status_label.configure(text="Ingrese una URL", text_color="orange")
            return

        self.status_label.configure(text="Cargando...", text_color="blue")

        from tools.image_tool.processor import _load_from_url
        result = _load_from_url(url)

        if result['success']:
            self.current_image_data = result['image_data']
            self._show_preview_adquisicion()
            self.status_label.configure(
                text=f"✅ Cargado desde URL",
                text_color="green"
            )
            self.url_entry.delete(0, 'end')
        else:
            self.status_label.configure(
                text=f"❌ {result.get('error', 'Error')}",
                text_color="red"
            )

    def _on_clear_image(self) -> None:
        """Clear current image."""
        self.current_image_path = None
        self.current_image_data = None
        self.status_label.configure(text="Sin imagen cargada", text_color="gray")
        self.path_label.configure(text="")
        # Limpiar todos los previews
        for label in self._preview_labels.values():
            label.configure(image=None, text="")
        if self._histogram_label:
            self._histogram_label.configure(image=None, text="")

    def _show_preview_adquisicion(self) -> None:
        """Muestra preview en pestaña Adquisición."""
        if not self.current_image_data:
            return
        image_array = self.current_image_data.get('array')
        if image_array is None:
            return
        pil_img = self._array_to_pil(image_array)
        self._show_in_tab("Adquisición", pil_img)

    def _array_to_pil(self, image_array: np.ndarray) -> Image.Image:
        """Convierte array numpy a PIL Image."""
        if len(image_array.shape) == 2:
            return Image.fromarray(image_array, mode='L')
        return Image.fromarray(image_array.astype('uint8'))

    # === Tab 2: Geometría ===
    def _setup_tab_geometria(self) -> None:
        """Tab 2: color space, crop, scale, rotate."""
        tab = self.tab_view.tab("Geometría")

        # Grayscale
        ctk.CTkButton(
            tab,
            text="⬛ Convertir a escala de grises",
            command=lambda: self._process_phase('_to_grayscale', {})
        ).pack(pady=5, padx=10, fill="x")

        # HSV
        ctk.CTkButton(
            tab,
            text="🎨 Convertir a HSV",
            command=lambda: self._process_phase('_to_hsv', {})
        ).pack(pady=5, padx=10, fill="x")

        # Separator
        ctk.CTkLabel(tab, text="--- Transformaciones ---").pack(pady=5)

        # Crop frame
        crop_frame = ctk.CTkFrame(tab, fg_color="transparent")
        crop_frame.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(crop_frame, text="Recortar (x, y, w, h):").pack()

        crop_inputs = ctk.CTkFrame(crop_frame, fg_color="transparent")
        crop_inputs.pack()

        self.crop_x = ctk.CTkEntry(crop_inputs, width=50, placeholder_text="x")
        self.crop_x.pack(side="left", padx=2)
        self.crop_y = ctk.CTkEntry(crop_inputs, width=50, placeholder_text="y")
        self.crop_y.pack(side="left", padx=2)
        self.crop_w = ctk.CTkEntry(crop_inputs, width=50, placeholder_text="w")
        self.crop_w.pack(side="left", padx=2)
        self.crop_h = ctk.CTkEntry(crop_inputs, width=50, placeholder_text="h")
        self.crop_h.pack(side="left", padx=2)

        ctk.CTkButton(
            crop_frame,
            text="✂️ Recortar",
            command=self._on_crop
        ).pack(pady=5)

        # Resize
        resize_frame = ctk.CTkFrame(tab, fg_color="transparent")
        resize_frame.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(resize_frame, text="Escalar (0.1 - 3.0):").pack()
        self.scale_slider = ctk.CTkSlider(resize_frame, from_=0.1, to=3.0, number_of_steps=29)
        self.scale_slider.set(1.0)
        self.scale_slider.pack(fill="x", padx=10)

        ctk.CTkButton(
            resize_frame,
            text="📐 Redimensionar",
            command=lambda: self._process_phase('_resize', {'scale': self.scale_slider.get()})
        ).pack(pady=5)

        # Rotate
        rotate_frame = ctk.CTkFrame(tab, fg_color="transparent")
        rotate_frame.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(rotate_frame, text="Rotar (0-360°):").pack()
        self.rotate_slider = ctk.CTkSlider(rotate_frame, from_=-180, to=180, number_of_steps=36)
        self.rotate_slider.set(0)
        self.rotate_slider.pack(fill="x", padx=10)

        ctk.CTkButton(
            rotate_frame,
            text="🔄 Rotar",
            command=lambda: self._process_phase('_rotate', {'angle': self.rotate_slider.get()})
        ).pack(pady=5)

        # Preview label for Geometría
        preview_label = ctk.CTkLabel(tab, text="", fg_color="transparent")
        self._preview_labels["Geometría"] = preview_label

    def _on_crop(self) -> None:
        """Handle crop button."""
        try:
            x = int(self.crop_x.get()) if self.crop_x.get() else 0
            y = int(self.crop_y.get()) if self.crop_y.get() else 0
            w = int(self.crop_w.get()) if self.crop_w.get() else 100
            h = int(self.crop_h.get()) if self.crop_h.get() else 100
            self._process_phase('_crop_region', {'x': x, 'y': y, 'w': w, 'h': h})
        except ValueError:
            self.status_label.configure(text="Valores inválidos para recorte", text_color="orange")

    # === Tab 3: Mejora ===
    def _setup_tab_mejora(self) -> None:
        """Tab 3: histograma, brillo, contraste, gamma."""
        tab = self.tab_view.tab("Mejora")

        # Histogram
        ctk.CTkButton(
            tab,
            text="📊 Calcular histograma",
            command=lambda: self._process_phase('_compute_histogram', {})
        ).pack(pady=5, padx=10, fill="x")

        # Equalize
        ctk.CTkButton(
            tab,
            text="📈 Ecualizar histograma",
            command=lambda: self._process_phase('_equalize_histogram', {})
        ).pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(tab, text="--- Ajustes ---").pack(pady=5)

        # Brightness/Contrast
        bc_frame = ctk.CTkFrame(tab, fg_color="transparent")
        bc_frame.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(bc_frame, text="Brillo (-1.0 a 1.0):").pack()
        self.brightness_slider = ctk.CTkSlider(bc_frame, from_=-1.0, to=1.0, number_of_steps=20)
        self.brightness_slider.set(0.0)
        self.brightness_slider.pack(fill="x", padx=10)

        ctk.CTkLabel(bc_frame, text="Contraste (0.5 a 2.0):").pack()
        self.contrast_slider = ctk.CTkSlider(bc_frame, from_=0.5, to=2.0, number_of_steps=15)
        self.contrast_slider.set(1.0)
        self.contrast_slider.pack(fill="x", padx=10)

        ctk.CTkButton(
            bc_frame,
            text="☀️ Aplicar brillo/contraste",
            command=self._on_adjust_bc
        ).pack(pady=5)

        # Gamma
        gamma_frame = ctk.CTkFrame(tab, fg_color="transparent")
        gamma_frame.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(gamma_frame, text="Gamma (0.1 a 3.0):").pack()
        self.gamma_slider = ctk.CTkSlider(gamma_frame, from_=0.1, to=3.0, number_of_steps=29)
        self.gamma_slider.set(1.0)
        self.gamma_slider.pack(fill="x", padx=10)

        ctk.CTkButton(
            gamma_frame,
            text="🔆 Aplicar gamma",
            command=lambda: self._process_phase('_adjust_gamma', {'gamma': self.gamma_slider.get()})
        ).pack(pady=5)

        # Preview label for Mejora
        preview_label = ctk.CTkLabel(tab, text="", fg_color="transparent")
        self._preview_labels["Mejora"] = preview_label

        # Histogram label (separate, appears only when calculated)
        self._histogram_label = ctk.CTkLabel(tab, text="", fg_color="transparent")

    def _on_adjust_bc(self) -> None:
        """Apply brightness and contrast."""
        self._process_phase('_adjust_brightness_contrast', {
            'brightness': self.brightness_slider.get(),
            'contrast': self.contrast_slider.get()
        })

    # === Tab 4: Filtros ===
    def _setup_tab_filtros(self) -> None:
        """Tab 4: selector filtro, ksize slider."""
        tab = self.tab_view.tab("Filtros")

        # Kernel size
        ksize_frame = ctk.CTkFrame(tab, fg_color="transparent")
        ksize_frame.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(ksize_frame, text="Kernel size (3-21, impar):").pack()
        self.ksize_slider = ctk.CTkSlider(ksize_frame, from_=3, to=21, number_of_steps=9)
        self.ksize_slider.set(5)
        self.ksize_slider.pack(fill="x", padx=10)

        self.ksize_label = ctk.CTkLabel(ksize_frame, text="ksize: 5")
        self.ksize_label.pack()

        ksize_slider = self.ksize_slider
        ksize_label = self.ksize_label

        def update_ksize(value):
            odd_val = int(value)
            if odd_val % 2 == 0:
                odd_val += 1
            ksize_label.configure(text=f"ksize: {odd_val}")

        self.ksize_slider.configure(command=update_ksize)

        # Filter buttons
        ctk.CTkButton(
            tab,
            text="🔵 Filtro Gaussiano",
            command=self._on_filter_gaussian
        ).pack(pady=5, padx=10, fill="x")

        ctk.CTkButton(
            tab,
            text="⬡ Filtro de Mediana",
            command=self._on_filter_median
        ).pack(pady=5, padx=10, fill="x")

        ctk.CTkButton(
            tab,
            text="🔘 Filtro de Media",
            command=self._on_filter_mean
        ).pack(pady=5, padx=10, fill="x")

        ctk.CTkButton(
            tab,
            text="🔧 Deconvolución",
            command=self._on_deconvolve
        ).pack(pady=5, padx=10, fill="x")

        # Preview label for Filtros
        preview_label = ctk.CTkLabel(tab, text="", fg_color="transparent")
        self._preview_labels["Filtros"] = preview_label

    def _on_filter_gaussian(self) -> None:
        ksize = int(self.ksize_slider.get())
        if ksize % 2 == 0:
            ksize += 1
        self._process_phase('_filter_gaussian', {'ksize': ksize})

    def _on_filter_median(self) -> None:
        ksize = int(self.ksize_slider.get())
        if ksize % 2 == 0:
            ksize += 1
        self._process_phase('_filter_median', {'ksize': ksize})

    def _on_filter_mean(self) -> None:
        ksize = int(self.ksize_slider.get())
        if ksize % 2 == 0:
            ksize += 1
        self._process_phase('_filter_mean', {'ksize': ksize})

    def _on_deconvolve(self) -> None:
        self._process_phase('_deconvolve', {'kernel_type': 'gaussian'})

    # === Tab 5: Morfología ===
    def _setup_tab_morfologia(self) -> None:
        """Tab 5: erosión, dilatación, apertura, cierre."""
        tab = self.tab_view.tab("Morfología")

        # Kernel size
        morph_ksize_frame = ctk.CTkFrame(tab, fg_color="transparent")
        morph_ksize_frame.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(morph_ksize_frame, text="Kernel size (3-15):").pack()
        self.morph_ksize_slider = ctk.CTkSlider(morph_ksize_frame, from_=3, to=15, number_of_steps=6)
        self.morph_ksize_slider.set(3)
        self.morph_ksize_slider.pack(fill="x", padx=10)

        self.morph_ksize_label = ctk.CTkLabel(morph_ksize_frame, text="ksize: 3")
        self.morph_ksize_label.pack()

        morph_ksize_slider = self.morph_ksize_slider
        morph_ksize_label = self.morph_ksize_label

        def update_morph_ksize(value):
            odd_val = int(value)
            if odd_val % 2 == 0:
                odd_val += 1
            morph_ksize_label.configure(text=f"ksize: {odd_val}")

        self.morph_ksize_slider.configure(command=update_morph_ksize)

        # Buttons
        ctk.CTkButton(
            tab,
            text="➖ Erosión",
            command=self._on_erode
        ).pack(pady=5, padx=10, fill="x")

        ctk.CTkButton(
            tab,
            text="➕ Dilatación",
            command=self._on_dilate
        ).pack(pady=5, padx=10, fill="x")

        ctk.CTkButton(
            tab,
            text="🌱 Apertura (erosión+dilatación)",
            command=self._on_open
        ).pack(pady=5, padx=10, fill="x")

        ctk.CTkButton(
            tab,
            text="🔒 Cierre (dilatación+erosión)",
            command=self._on_close
        ).pack(pady=5, padx=10, fill="x")

        # Preview label for Morfología
        preview_label = ctk.CTkLabel(tab, text="", fg_color="transparent")
        self._preview_labels["Morfología"] = preview_label

    def _on_erode(self) -> None:
        ksize = int(self.morph_ksize_slider.get())
        if ksize % 2 == 0:
            ksize += 1
        self._process_phase('_erode', {'kernel_size': ksize})

    def _on_dilate(self) -> None:
        ksize = int(self.morph_ksize_slider.get())
        if ksize % 2 == 0:
            ksize += 1
        self._process_phase('_dilate', {'kernel_size': ksize})

    def _on_open(self) -> None:
        ksize = int(self.morph_ksize_slider.get())
        if ksize % 2 == 0:
            ksize += 1
        self._process_phase('_open', {'kernel_size': ksize})

    def _on_close(self) -> None:
        ksize = int(self.morph_ksize_slider.get())
        if ksize % 2 == 0:
            ksize += 1
        self._process_phase('_close', {'kernel_size': ksize})

    # === Tab 6: Bordes ===
    def _setup_tab_bordes(self) -> None:
        """Tab 6: sobel, prewitt, laplacian, canny."""
        tab = self.tab_view.tab("Bordes")

        # Edge detectors
        ctk.CTkButton(
            tab,
            text="↔️ Sobel",
            command=lambda: self._process_phase('_edge_sobel', {})
        ).pack(pady=5, padx=10, fill="x")

        ctk.CTkButton(
            tab,
            text="↔️ Prewitt",
            command=lambda: self._process_phase('_edge_prewitt', {})
        ).pack(pady=5, padx=10, fill="x")

        ctk.CTkButton(
            tab,
            text="🔺 Laplaciano",
            command=lambda: self._process_phase('_edge_laplacian', {})
        ).pack(pady=5, padx=10, fill="x")

        # Canny with thresholds
        canny_frame = ctk.CTkFrame(tab, fg_color="transparent")
        canny_frame.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(canny_frame, text="Threshold 1 (bajo):").pack()
        self.canny_t1 = ctk.CTkSlider(canny_frame, from_=0, to=255, number_of_steps=25)
        self.canny_t1.set(50)
        self.canny_t1.pack(fill="x", padx=10)

        ctk.CTkLabel(canny_frame, text="Threshold 2 (alto):").pack()
        self.canny_t2 = ctk.CTkSlider(canny_frame, from_=0, to=255, number_of_steps=25)
        self.canny_t2.set(150)
        self.canny_t2.pack(fill="x", padx=10)

        ctk.CTkButton(
            canny_frame,
            text="⭕ Canny",
            command=self._on_canny
        ).pack(pady=5)

        # Contours and bounding boxes
        ctk.CTkLabel(tab, text="--- Análisis de contornos ---").pack(pady=5)

        ctk.CTkButton(
            tab,
            text="🔍 Encontrar contornos",
            command=lambda: self._process_phase('_find_contours', {})
        ).pack(pady=5, padx=10, fill="x")

        bbox_frame = ctk.CTkFrame(tab, fg_color="transparent")
        bbox_frame.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(bbox_frame, text="Área mínima:").pack()
        self.min_area_entry = ctk.CTkEntry(bbox_frame, width=100)
        self.min_area_entry.insert(0, "100")
        self.min_area_entry.pack(pady=2)

        ctk.CTkButton(
            bbox_frame,
            text="📦 Bounding boxes",
            command=self._on_bounding_boxes
        ).pack(pady=5)

        # Preview label for Bordes
        preview_label = ctk.CTkLabel(tab, text="", fg_color="transparent")
        self._preview_labels["Bordes"] = preview_label

    def _on_canny(self) -> None:
        self._process_phase('_edge_canny', {
            'threshold1': int(self.canny_t1.get()),
            'threshold2': int(self.canny_t2.get())
        })

    def _on_bounding_boxes(self) -> None:
        try:
            min_area = int(self.min_area_entry.get()) if self.min_area_entry.get() else 100
            self._process_phase('_bounding_boxes', {'min_area': min_area})
        except ValueError:
            self.status_label.configure(text="Área mínima inválida", text_color="orange")

    # === Tab 7: Análisis ===
    def _setup_tab_analisis(self) -> None:
        """Tab 7: template matching, pseudocolor, haar."""
        tab = self.tab_view.tab("Análisis")

        # Template matching
        template_frame = ctk.CTkFrame(tab, fg_color="transparent")
        template_frame.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(template_frame, text="Template Matching:").pack()

        ctk.CTkButton(
            template_frame,
            text="📁 Seleccionar template",
            command=self._on_select_template
        ).pack(pady=5)

        self.template_path_label = ctk.CTkLabel(template_frame, text="Sin template", text_color="gray", font=ctk.CTkFont(size=10))
        self.template_path_label.pack()

        self.template_path: str = None

        # Pseudocolor
        pseudo_frame = ctk.CTkFrame(tab, fg_color="transparent")
        pseudo_frame.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(pseudo_frame, text="Pseudocolor:").pack()

        self.colormap_var = ctk.StringVar(value="jet")
        colormap_menu = ctk.CTkOptionMenu(
            pseudo_frame,
            values=COLORMAP_OPTIONS,
            variable=self.colormap_var,
            width=200
        )
        colormap_menu.pack(pady=5)

        ctk.CTkButton(
            pseudo_frame,
            text="🌈 Aplicar pseudocolor",
            command=self._on_pseudocolor
        ).pack(pady=5)

        # Haar detection
        haar_frame = ctk.CTkFrame(tab, fg_color="transparent")
        haar_frame.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(haar_frame, text="Detección Haar:").pack()

        self.haar_cascade_var = ctk.StringVar(value="face")
        haar_menu = ctk.CTkOptionMenu(
            haar_frame,
            values=['face', 'eye', 'smile'],
            variable=self.haar_cascade_var,
            width=200
        )
        haar_menu.pack(pady=5)

        ctk.CTkButton(
            haar_frame,
            text="🤖 Detectar objetos",
            command=self._on_haar_detect
        ).pack(pady=5)

        # Preview label for Análisis
        preview_label = ctk.CTkLabel(tab, text="", fg_color="transparent")
        self._preview_labels["Análisis"] = preview_label

    def _on_select_template(self) -> None:
        """Select template image for matching."""
        file = filedialog.askopenfilename(
            title="Seleccionar template",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.bmp"),
                ("Todos los archivos", "*.*")
            ]
        )

        if file:
            self.template_path = file
            self.template_path_label.configure(
                text=Path(file).name,
                text_color="green"
            )

    def _on_pseudocolor(self) -> None:
        """Apply pseudocolor."""
        self._process_phase('_pseudocolor', {'colormap': self.colormap_var.get()})

    def _on_haar_detect(self) -> None:
        """Apply Haar cascade detection."""
        cascade = self.haar_cascade_var.get()
        self._process_phase('_haar_detect', {'cascade_path': cascade})

    # === Common processing ===
    def _process_phase(self, phase: str, options: Dict[str, Any]) -> None:
        """Wrapper que detecta pestaña activa y muestra preview ahí."""
        if not self.current_image_data:
            self._update_status("Cargá una imagen primero", "orange")
            return

        image_array = self.current_image_data.get('array')
        if image_array is None:
            self._update_status("Sin datos de imagen", "red")
            return

        # Mostrar feedback de procesamiento
        self.status_label.configure(text="Procesando...", text_color="blue")
        self.progress_bar.pack(fill="x", padx=10, pady=2)
        self.progress_bar.start()
        self.update()

        # Ejecutar procesamiento
        result = self._execute_phase(phase, image_array, options)

        # Ocultar progress bar
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

        # Actualizar preview en pestaña correcta
        if result.get('success'):
            self.current_image_data = result.get('image_data')
            self._show_preview_in_current_tab(result)
            output_files = result.get('output_files', [])
            # Histograma especial en pestaña Mejora
            if phase == '_compute_histogram':
                self._show_histogram(output_files)
            msg = f"{result.get('message')}" + (f" - {len(output_files)} archivo(s)" if output_files else "")
            self._update_status(msg, "green")
        else:
            self._update_status(result.get('error', 'Error'), "red")

    def _show_preview_in_current_tab(self, result: Dict[str, Any]) -> None:
        """Muestra preview en la pestaña activa según la fase."""
        active_tab = self.tab_view.get()
        image_data = result.get('image_data')
        if not image_data:
            return
        image_array = image_data.get('array')
        if image_array is None:
            return
        pil_img = self._array_to_pil(image_array)
        self._show_in_tab(active_tab, pil_img)

    def _show_histogram(self, output_files: List[str]) -> None:
        """Muestra histograma en pestaña Mejora."""
        hist_file = next((f for f in output_files if 'histogram' in f), None)
        if hist_file and Path(hist_file).exists():
            hist_img = Image.open(hist_file)
            # Redimensionar para preview
            w, h = hist_img.size
            scale = min(300 / w, 100 / h, 1.0)
            new_w, new_h = int(w * scale), int(h * scale)
            hist_img = hist_img.resize((new_w, new_h), Image.LANCZOS)
            photo = self._resize_for_preview(hist_img)
            self._histogram_label.configure(image=photo, text="")
            self._histogram_label._photo = photo
            self._histogram_label.pack(fill="x", pady=5)

    def _execute_phase(self, phase: str, image_array: np.ndarray, options: Dict[str, Any]) -> Dict[str, Any]:
        """Execute processor phase. Returns result dict."""
        func = self._get_phase_func(phase)
        if not func:
            return {'success': False, 'error': f"Unknown operation: {phase}"}

        try:
            result = func(image_array, **options)
            return result
        except Exception as e:
            return {'success': False, 'error': f"Processing error: {str(e)}"}

    def _get_phase_func(self, phase: str):
        """Map phase name to processor function."""
        from tools.image_tool.processor import (
            _to_grayscale, _to_hsv, _crop_region, _resize, _translate, _rotate,
            _compute_histogram, _equalize_histogram, _adjust_brightness_contrast, _adjust_gamma,
            _filter_gaussian, _filter_median, _filter_mean, _deconvolve,
            _erode, _dilate, _open, _close,
            _edge_sobel, _edge_prewitt, _edge_laplacian, _edge_canny, _find_contours, _bounding_boxes,
            _template_match, _pseudocolor, _haar_detect
        )
        phase_funcs = {
            '_to_grayscale': _to_grayscale,
            '_to_hsv': _to_hsv,
            '_crop_region': _crop_region,
            '_resize': _resize,
            '_translate': _translate,
            '_rotate': _rotate,
            '_compute_histogram': _compute_histogram,
            '_equalize_histogram': _equalize_histogram,
            '_adjust_brightness_contrast': _adjust_brightness_contrast,
            '_adjust_gamma': _adjust_gamma,
            '_filter_gaussian': _filter_gaussian,
            '_filter_median': _filter_median,
            '_filter_mean': _filter_mean,
            '_deconvolve': _deconvolve,
            '_erode': _erode,
            '_dilate': _dilate,
            '_open': _open,
            '_close': _close,
            '_edge_sobel': _edge_sobel,
            '_edge_prewitt': _edge_prewitt,
            '_edge_laplacian': _edge_laplacian,
            '_edge_canny': _edge_canny,
            '_find_contours': _find_contours,
            '_bounding_boxes': _bounding_boxes,
            '_template_match': _template_match,
            '_pseudocolor': _pseudocolor,
            '_haar_detect': _haar_detect,
        }
        return phase_funcs.get(phase)

    def _update_status(self, message: str, color: str) -> None:
        """Update status label."""
        self.status_label.configure(text=message, text_color=color)