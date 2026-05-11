"""
ImageToolUI Main - Esqueleto principal de la UI de Image Processing.

La clase ImageToolUI orchestra los tabs especializados.
Los métodos _setup_tab_*() están en módulos separados para SRP.
"""

import os
from pathlib import Path
from typing import List, Dict, Any
import numpy as np

import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk

from core.base_tool_ui import BaseToolUI
from core.tool_builder import create_standard_tool_ui

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

    def _setup_ui(self):
        create_standard_tool_ui(
            self, ("\U0001F5BC\ufe0f", "Procesamiento Digital de Imágenes"),
            "",
            selector_type="none",
            help_config={
                "description": "🖼️ PDI: 7 fases (filtros, geometría, bordes, morfología, histograma, ruido, restauración)",
                "usage": [
                    "1. 📥 Cargar una imagen (archivo o URL)",
                    "2. 📑 Elegir operación en las pestañas",
                    "3. ⚙️ Ajustar parámetros",
                    "4. ▶️ Aplicar y ver preview",
                ],
                "tips": [
                    "💡 El preview aparece en la misma pestaña",
                    "💡 Escape cancela la operación en curso",
                    "💡 Podés encadenar operaciones (resultado pasa a la siguiente)",
                ],
                "warnings": [
                    "⚠️ Algunas operaciones requieren OpenCV",
                    "⚠️ La imagen original se sobrescribe al aplicar",
                ],
            },
        )

        self.tab_view = ctk.CTkTabview(self, fg_color="transparent")
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=5)

        tab_names = [
            "Adquisici\u00f3n", "Geometr\u00eda", "Mejora",
            "Filtros", "Morfolog\u00eda", "Bordes", "An\u00e1lisis",
        ]
        for tab_name in tab_names:
            self.tab_view.add(tab_name)

        self._preview_labels: Dict[str, ctk.CTkLabel] = {}
        self._histogram_label: ctk.CTkLabel = None

        # Importar y ejecutar setup de cada tab
        from tools.image_tool.ui import (
            adquisicion_tab, geometria_tab, mejora_tab,
            filtros_tab, morfologia_tab, bordes_tab, analisis_tab
        )

        self._setup_tab_adquisicion = lambda: adquisicion_tab.setup_tab(self)
        self._setup_tab_geometria = lambda: geometria_tab.setup_tab(self)
        self._setup_tab_mejora = lambda: mejora_tab.setup_tab(self)
        self._setup_tab_filtros = lambda: filtros_tab.setup_tab(self)
        self._setup_tab_morfologia = lambda: morfologia_tab.setup_tab(self)
        self._setup_tab_bordes = lambda: bordes_tab.setup_tab(self)
        self._setup_tab_analisis = lambda: analisis_tab.setup_tab(self)

        self._setup_tab_adquisicion()
        self._setup_tab_geometria()
        self._setup_tab_mejora()
        self._setup_tab_filtros()
        self._setup_tab_morfologia()
        self._setup_tab_bordes()
        self._setup_tab_analisis()

        self.feedback_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.feedback_frame.pack(fill="x", padx=10, pady=(5, 0))

        self.status_label = ctk.CTkLabel(self.feedback_frame, text="Sin imagen cargada", text_color="gray")
        self.status_label.pack()

        self.progress_bar = ctk.CTkProgressBar(self.feedback_frame, mode='indeterminate')
        self.progress_bar.set(0)

    def _resize_for_preview(self, pil_img: Image.Image):
        w, h = pil_img.size
        scale = min(300 / w, 200 / h, 1.0)
        new_w, new_h = int(w * scale), int(h * scale)
        try:
            return ctk.CTkImage(pil_img, size=(new_w, new_h))
        except Exception:
            return ImageTk.PhotoImage(pil_img.resize((new_w, new_h), Image.LANCZOS))

    def _show_in_tab(self, tab_name: str, pil_img: Image.Image) -> None:
        label = self._preview_labels.get(tab_name)
        if label:
            photo = self._resize_for_preview(pil_img)
            label.configure(image=photo, text="")
            label._photo = photo
            label.pack(fill="both", expand=True)

    def _array_to_pil(self, image_array: np.ndarray) -> Image.Image:
        if len(image_array.shape) == 2:
            return Image.fromarray(image_array, mode='L')
        return Image.fromarray(image_array.astype('uint8'))

    def _process_phase(self, phase: str, options: Dict[str, Any]) -> None:
        if not self.current_image_data:
            self._update_status("Carg\u00e1 una imagen primero", "orange")
            return
        image_array = self.current_image_data.get('array')
        if image_array is None:
            self._update_status("Sin datos de imagen", "red")
            return

        self.status_label.configure(text="Procesando...", text_color="blue")
        self.progress_bar.pack(fill="x", padx=10, pady=2)
        self.progress_bar.start()
        self.update()

        result = self._execute_phase(phase, image_array, options)

        self.progress_bar.stop()
        self.progress_bar.pack_forget()

        if result.get('success'):
            self.current_image_data = result.get('image_data')
            self._show_preview_in_current_tab(result)
            output_files = result.get('output_files', [])
            if phase == '_compute_histogram':
                self._show_histogram(output_files)
            msg = f"{result.get('message')}" + (f" - {len(output_files)} archivo(s)" if output_files else "")
            self._update_status(msg, "green")
        else:
            self._update_status(result.get('error', 'Error'), "red")

    def _show_preview_in_current_tab(self, result: Dict[str, Any]) -> None:
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
        hist_file = next((f for f in output_files if 'histogram' in f), None)
        if hist_file and Path(hist_file).exists():
            hist_img = Image.open(hist_file)
            w, h = hist_img.size
            scale = min(300 / w, 100 / h, 1.0)
            new_w, new_h = int(w * scale), int(h * scale)
            hist_img = hist_img.resize((new_w, new_h), Image.LANCZOS)
            photo = self._resize_for_preview(hist_img)
            self._histogram_label.configure(image=photo, text="")
            self._histogram_label._photo = photo
            self._histogram_label.pack(fill="x", pady=5)

    def _execute_phase(self, phase: str, image_array: np.ndarray, options: Dict[str, Any]) -> Dict[str, Any]:
        func = self._get_phase_func(phase)
        if not func:
            return {'success': False, 'error': f"Unknown operation: {phase}"}
        try:
            return func(image_array, **options)
        except Exception as e:
            return {'success': False, 'error': f"Processing error: {str(e)}"}

    def _get_phase_func(self, phase: str):
        from tools.image_tool.processor import (
            _to_grayscale, _to_hsv, _crop_region, _resize, _translate, _rotate,
            _compute_histogram, _equalize_histogram, _adjust_brightness_contrast, _adjust_gamma,
            _filter_gaussian, _filter_median, _filter_mean, _deconvolve,
            _erode, _dilate, _open, _close,
            _edge_sobel, _edge_prewitt, _edge_laplacian, _edge_canny, _find_contours, _bounding_boxes,
            _template_match, _pseudocolor, _haar_detect,
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
        self.status_label.configure(text=message, text_color=color)


# Importar handlers de cada tab
from tools.image_tool.ui import (
    adquisicion_tab, geometria_tab, mejora_tab,
    filtros_tab, morfologia_tab, bordes_tab, analisis_tab
)

# Asignar métodos a la clase
ImageToolUI._on_select_image = adquisicion_tab.on_select_image
ImageToolUI._on_load_url = adquisicion_tab.on_load_url
ImageToolUI._on_clear_image = adquisicion_tab.on_clear_image
ImageToolUI._show_preview_adquisicion = adquisicion_tab.show_preview_adquisicion
ImageToolUI._on_crop = geometria_tab.on_crop

ImageToolUI._on_adjust_bc = mejora_tab.on_adjust_bc
ImageToolUI._on_filter_gaussian = filtros_tab.on_filter_gaussian
ImageToolUI._on_filter_median = filtros_tab.on_filter_median
ImageToolUI._on_filter_mean = filtros_tab.on_filter_mean
ImageToolUI._on_deconvolve = filtros_tab.on_deconvolve
ImageToolUI._on_erode = morfologia_tab.on_erode
ImageToolUI._on_dilate = morfologia_tab.on_dilate
ImageToolUI._on_open = morfologia_tab.on_open
ImageToolUI._on_close = morfologia_tab.on_close
ImageToolUI._on_canny = bordes_tab.on_canny
ImageToolUI._on_bounding_boxes = bordes_tab.on_bounding_boxes
ImageToolUI._on_select_template = analisis_tab.on_select_template
ImageToolUI._on_pseudocolor = analisis_tab.on_pseudocolor
ImageToolUI._on_haar_detect = analisis_tab.on_haar_detect