"""
Image Tool UI - Módulos especializados por tab.

Este paquete contiene los tabs de la UI de Image Processing organizados por responsabilidad:
- main_ui: esqueleto principal de ImageToolUI
- adquisicion_tab: carga de imágenes (archivo, URL)
- geometria_tab: transformaciones (escala de grises, HSV, crop, resize, rotate)
- mejora_tab: histograma, brillo, contraste, gamma
- filtros_tab: Gaussiano, Mediana, Media, Deconvolución
- morfologia_tab: Erosión, Dilatación, Apertura, Cierre
- bordes_tab: Sobel, Prewitt, Laplaciano, Canny, Contornos
- analisis_tab: Template matching, Pseudocolor, Haar detection
- helpers: funciones auxiliares (resize, show_in_tab, etc.)

Backward compatibility: ImageToolUI también se importa desde ui.py
"""

from tools.image_tool.ui.main_ui import ImageToolUI

__all__ = ['ImageToolUI']