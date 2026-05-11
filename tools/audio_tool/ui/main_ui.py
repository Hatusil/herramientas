"""
AudioToolUI Main - Esqueleto principal de la UI de Audio.

La clase AudioToolUI orchestra los tabs especializados.
"""

import logging
from typing import Callable

import customtkinter as ctk

from core.base_tool_ui import BaseToolUI
from core.tool_builder import create_standard_tool_ui

logger = logging.getLogger(__name__)


class AudioToolUI(BaseToolUI):
    """UI para procesamiento de archivos de audio."""

    def __init__(self, master, on_process: Callable, **kwargs):
        super().__init__(master, on_process, **kwargs)
        self.is_processing = False
        self._setup_progress_bar()

    def _setup_ui(self):
        r = create_standard_tool_ui(
            self, ("\U0001F3B5", "Procesamiento de Audio"),
            "",
            selector_type="file",
            tab_configs=[
                {"name": "Normalizar"}, {"name": "Limpiar"},
                {"name": "Editar Metadatos"}, {"name": "Convertir"},
                {"name": "Reparar"}, {"name": "Info"}, {"name": "Verificar"},
            ],
            file_types=[
                ("Audio files", "*.mp3 *.wav *.flac *.ogg *.m4a *.aac"),
                ("MP3", "*.mp3"),
                ("Todos", "*.*"),
            ],
            help_config={
                "description": "🎵 Normaliza, limpia metadatos y convierte archivos de audio",
                "file_label": "Archivos de audio:",
                "usage": [
                    "1. 📥 Agregar archivos (+)",
                    "2. ☑️ Seleccionar con Ctrl+click o botones 'Todos'/'Ninguno'",
                    "3. 📑 Elegir operación (Normalizar/Limpiar/Convertir/Reparar/Info)",
                    "4. ⚙️ Configurar opciones LUFS o calidad (192k default)",
                    "5. ▶️ Click en ejecutar (procesa solo los seleccionados)",
                ],
                "tips": [
                    "💡 LUFS -16 es el estándar para streaming",
                    "💡 192kbps da buen balance calidad/tamaño",
                    "💡 Verificá archivos antes de repararlos",
                ],
                "warnings": [
                    "⚠️ mp3→mp3 con calidad 192k se omite (ya en formato)",
                    "⚠️ Cambiar calidad para forzar conversión",
                    "⚠️ Normalización alta puede afectar calidad",
                    "⚠️ Conversión siempre crea nuevo archivo",
                    "⚠️ Reparar archivos severos puede dejar artefactos",
                ],
            },
        )
        self.files = r["files"]
        self.file_listbox = r["listbox"]
        self.status_label = r["status_label"]
        self.tab_normalize = r["tabs"]["Normalizar"]
        self.tab_clean = r["tabs"]["Limpiar"]
        self.tab_edit_meta = r["tabs"]["Editar Metadatos"]
        self.tab_convert = r["tabs"]["Convertir"]
        self.tab_repair = r["tabs"]["Reparar"]
        self.tab_info = r["tabs"]["Info"]
        self.tab_verify = r["tabs"]["Verificar"]

        # Importar y ejecutar setup de cada tab
        from tools.audio_tool.ui import (
            normalize_tab, clean_tab, edit_meta_tab,
            convert_tab, repair_tab, info_tab, verify_tab
        )

        self._setup_normalize_tab = lambda: normalize_tab.setup_tab(self)
        self._setup_clean_tab = lambda: clean_tab.setup_tab(self)
        self._setup_edit_meta_tab = lambda: edit_meta_tab.setup_tab(self)
        self._setup_convert_tab = lambda: convert_tab.setup_tab(self)
        self._setup_repair_tab = lambda: repair_tab.setup_tab(self)
        self._setup_info_tab = lambda: info_tab.setup_tab(self)
        self._setup_verify_tab = lambda: verify_tab.setup_tab(self)

        self._setup_normalize_tab()
        self._setup_clean_tab()
        self._setup_edit_meta_tab()
        self._setup_convert_tab()
        self._setup_repair_tab()
        self._setup_info_tab()
        self._setup_verify_tab()


# Importar handlers de cada tab
from tools.audio_tool.ui import (
    normalize_tab, clean_tab, edit_meta_tab,
    convert_tab, repair_tab, info_tab, verify_tab
)

# Asignar métodos a la clase
AudioToolUI._normalize = normalize_tab.normalize
AudioToolUI._clean_metadata = clean_tab.clean_metadata
AudioToolUI._edit_metadata = edit_meta_tab.edit_metadata
AudioToolUI._convert = convert_tab.convert
AudioToolUI._verify_before_repair = repair_tab.verify_before_repair
AudioToolUI._do_repair = repair_tab.do_repair
AudioToolUI._repair = repair_tab.do_repair
AudioToolUI._show_info = info_tab.show_info
AudioToolUI._verify_audio = verify_tab.verify_audio
AudioToolUI._verify = verify_tab.verify_audio