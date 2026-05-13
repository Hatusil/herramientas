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
                {"name": "Transcribir"},
            ],
            file_types=[
                ("Audio files", "*.mp3 *.wav *.flac *.ogg *.m4a *.aac"),
                ("MP3", "*.mp3"),
                ("Todos", "*.*"),
            ],
            help_config={
                "description": "🎵 Normaliza, limpia metadatos, convierte y transcribe audio",
                "file_label": "Archivos de audio:",
                "usage": [
                    "1. 📥 Agregar archivos (+)",
                    "2. ☑️ Seleccionar con Ctrl+click o botones 'Todos'/'Ninguno'",
                    "3. 📑 Elegir operación (Normalizar/Limpiar/Convertir/Transcribir...)",
                    "4. ⚙️ Configurar opciones (LUFS, calidad, modelo)",
                    "5. ▶️ Click en ejecutar (procesa solo los seleccionados)",
                ],
                "tips": [
                    "💡 LUFS -16 es el estándar para streaming",
                    "💡 192kbps da buen balance calidad/tamaño",
                    "💡 Transcribir usa OLMoASR (rival de Whisper)",
                    "💡 Modelo 'tiny' es rápido, 'small' más preciso",
                ],
                "warnings": [
                    "⚠️ mp3→mp3 con calidad 192k se omite (ya en formato)",
                    "⚠️ Transcribir requiere ~2GB RAM (modelo base)",
                    "⚠️ Primera vez tarda en descargar modelo",
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
        self.tab_transcribe = r["tabs"]["Transcribir"]

        # Importar y ejecutar setup de cada tab
        from tools.audio_tool.ui import (
            normalize_tab, clean_tab, edit_meta_tab,
            convert_tab, repair_tab, info_tab, verify_tab,
            transcribe_tab
        )

        self._setup_normalize_tab = lambda: normalize_tab.setup_tab(self)
        self._setup_clean_tab = lambda: clean_tab.setup_tab(self)
        self._setup_edit_meta_tab = lambda: edit_meta_tab.setup_tab(self)
        self._setup_convert_tab = lambda: convert_tab.setup_tab(self)
        self._setup_repair_tab = lambda: repair_tab.setup_tab(self)
        self._setup_info_tab = lambda: info_tab.setup_tab(self)
        self._setup_verify_tab = lambda: verify_tab.setup_tab(self)
        self._setup_transcribe_tab = lambda: transcribe_tab.setup_tab(self)

        self._setup_normalize_tab()
        self._setup_clean_tab()
        self._setup_edit_meta_tab()
        self._setup_convert_tab()
        self._setup_repair_tab()
        self._setup_info_tab()
        self._setup_verify_tab()
        self._setup_transcribe_tab()


# Importar handlers de cada tab
from tools.audio_tool.ui import (
    normalize_tab, clean_tab, edit_meta_tab,
    convert_tab, repair_tab, info_tab, verify_tab,
    transcribe_tab
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
AudioToolUI._transcribe = transcribe_tab.transcribe
AudioToolUI._verify = verify_tab.verify_audio