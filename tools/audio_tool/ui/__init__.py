"""
Audio Tool UI - Módulos especializados por tab.

Este paquete contiene los tabs de la UI de Audio organizados por responsabilidad:
- main_ui: esqueleto principal de AudioToolUI
- normalize_tab: normalización de volumen
- clean_tab: limpieza de metadatos
- edit_meta_tab: edición de metadatos
- convert_tab: conversión de formato
- repair_tab: reparación de archivos
- info_tab: información del archivo
- verify_tab: verificación de archivos

Backward compatibility: AudioToolUI también se importa desde ui.py
"""

from tools.audio_tool.ui.main_ui import AudioToolUI

__all__ = ['AudioToolUI']