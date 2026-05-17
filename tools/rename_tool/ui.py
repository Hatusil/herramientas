from ui.radiobutton import RadioButton
import customtkinter as ctk
import tkinter as tk
from typing import Callable, Dict
from core.base_tool_ui import BaseToolUI
from core.tool_builder import create_standard_tool_ui
from core.constants import COLORS


class RenameToolUI(BaseToolUI):
    """UI para renombrar archivos en masa."""

    def __init__(self, master, on_process: Callable, **kwargs):
        super().__init__(master, on_process, **kwargs)
        self.is_processing = False

    def _setup_ui(self):
        r = create_standard_tool_ui(
            self, ("\U0001F524", "Renombrador de Archivos"),
            "",  # description moved to help_config
            selector_type="file",
            tab_configs=[
                {"name": "Prefijo"}, {"name": "Sufijo"},
                {"name": "Reemplazar"}, {"name": "Números"},
                {"name": "May/Min"},
            ],
            help_config={
                "description": "🔤 Renombra archivos: prefijos, sufijos, buscar/reemplazar, números, mayúsculas/minúsculas",
                "usage": [
                    "1. 📥 Agregar archivos (+)",
                    "2. ☑️ Seleccionar con Ctrl+click o botones",
                    "3. 📑 Elegir operación (Prefijo/Sufijo/Reemplazar/Números/May-Min)",
                    "4. ⚙️ Ingresar parámetros según operación",
                    "5. ▶️ Click en ejecutar (procesa seleccionados)",
                ],
                "tips": [
                    "💡 Usá {name} y {n} en el patrón de números",
                    "💡 Mayúsculas/minúsculas es reversible, prefijo/sufijo no",
                    "💡 Podés combinar operaciones (primero números, luego prefijo)",
                ],
                "warnings": [
                    "⚠️ Operación DESTRUCTIVA sin deshacer",
                    "⚠️ Verificar nombres ANTES de cerrar",
                    "⚠️ Números pueden sobrescribir existentes",
                ],
            },
        )
        self.files = r["files"]
        self.file_listbox = r["listbox"]
        self.status_label = r["status_label"]
        self.tab_prefix = r["tabs"]["Prefijo"]
        self.tab_suffix = r["tabs"]["Sufijo"]
        self.tab_replace = r["tabs"]["Reemplazar"]
        self.tab_numbers = r["tabs"]["N\u00fameros"]
        self.tab_case = r["tabs"]["May/Min"]

        self._setup_prefix_tab()
        self._setup_suffix_tab()
        self._setup_replace_tab()
        self._setup_numbers_tab()
        self._setup_case_tab()

    def _setup_prefix_tab(self) -> None:
        frame = self.tab_prefix

        ctk.CTkLabel(frame, text="Agregar prefijo al nombre:", font=ctk.CTkFont(weight="bold")).pack(pady=10)

        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(pady=10)

        ctk.CTkLabel(input_frame, text="Prefijo:").pack(side="left", padx=5)
        self.prefix_entry = ctk.CTkEntry(input_frame, width=200)
        self.prefix_entry.pack(side="left", padx=5)

        ctk.CTkButton(frame, text="\U0001F516 Agregar Prefijo", command=self._add_prefix, height=40).pack(pady=20)

    def _add_prefix(self) -> None:
        if not self._check_files():
            return
        prefix = self.prefix_entry.get()
        if not prefix:
            self.status_label.configure(text="Ingrese un prefijo", text_color=COLORS.get("warning"))
            return
        from tools.rename_tool.processor import rename_with_prefix
        result = rename_with_prefix(self.files, prefix)
        self._handle_result(result)

    def _setup_suffix_tab(self) -> None:
        frame = self.tab_suffix

        ctk.CTkLabel(frame, text="Agregar sufijo antes de la extensi\u00f3n:", font=ctk.CTkFont(weight="bold")).pack(pady=10)

        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(pady=10)

        ctk.CTkLabel(input_frame, text="Sufijo:").pack(side="left", padx=5)
        self.suffix_entry = ctk.CTkEntry(input_frame, width=200)
        self.suffix_entry.pack(side="left", padx=5)

        ctk.CTkButton(frame, text="\U0001F516 Agregar Sufijo", command=self._add_suffix, height=40).pack(pady=20)

    def _add_suffix(self) -> None:
        if not self._check_files():
            return
        suffix = self.suffix_entry.get()
        from tools.rename_tool.processor import rename_with_suffix
        result = rename_with_suffix(self.files, suffix)
        self._handle_result(result)

    def _setup_replace_tab(self) -> None:
        frame = self.tab_replace

        ctk.CTkLabel(frame, text="Reemplazar texto en los nombres:", font=ctk.CTkFont(weight="bold")).pack(pady=10)

        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(pady=5)

        ctk.CTkLabel(input_frame, text="Buscar:").pack(side="left", padx=5)
        self.find_entry = ctk.CTkEntry(input_frame, width=150)
        self.find_entry.pack(side="left", padx=5)

        input_frame2 = ctk.CTkFrame(frame)
        input_frame2.pack(pady=5)

        ctk.CTkLabel(input_frame2, text="Reemplazar con:").pack(side="left", padx=5)
        self.replace_entry = ctk.CTkEntry(input_frame2, width=150)
        self.replace_entry.pack(side="left", padx=5)

        ctk.CTkButton(frame, text="\U0001F504 Reemplazar", command=self._do_replace, height=40).pack(pady=10)

    def _do_replace(self) -> None:
        if not self._check_files():
            return
        find = self.find_entry.get()
        if not find:
            self.status_label.configure(text="Ingrese texto a buscar", text_color=COLORS.get("warning"))
            return
        # Permitir string vacío para eliminar texto
        replace = self.replace_entry.get() or ""
        from tools.rename_tool.processor import rename_replace
        result = rename_replace(self.files, find, replace)
        self._handle_result(result)

    def _setup_numbers_tab(self) -> None:
        frame = self.tab_numbers

        ctk.CTkLabel(frame, text="Renombrar con n\u00fameros secuenciales:", font=ctk.CTkFont(weight="bold")).pack(pady=10)

        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(pady=5)

        ctk.CTkLabel(input_frame, text="Iniciar desde:").pack(side="left", padx=5)
        self.start_entry = ctk.CTkEntry(input_frame, width=60)
        self.start_entry.insert(0, "1")
        self.start_entry.pack(side="left", padx=5)

        ctk.CTkLabel(input_frame, text="Patr\u00f3n:").pack(side="left", padx=5)
        self.pattern_entry = ctk.CTkEntry(input_frame, width=120)
        self.pattern_entry.insert(0, "{name}_{n}")
        self.pattern_entry.pack(side="left", padx=5)

        ctk.CTkLabel(
            frame, text="(Usa {name} para nombre original y {n} para n\u00famero)",
            text_color="gray", font=ctk.CTkFont(size=13)
        ).pack(pady=2)

        ctk.CTkButton(frame, text="\U0001F522 Numerar", command=self._do_number, height=40).pack(pady=10)

    def _do_number(self) -> None:
        if not self._check_files():
            return
        start = int(self.start_entry.get() or 1)
        pattern = self.pattern_entry.get() or "{name}_{n}"
        from tools.rename_tool.processor import rename_numbered
        result = rename_numbered(self.files, start=start, pattern=pattern)
        self._handle_result(result)

    def _setup_case_tab(self) -> None:
        frame = self.tab_case

        ctk.CTkLabel(frame, text="Cambiar may\u00fasculas/min\u00fasculas:", font=ctk.CTkFont(weight="bold")).pack(pady=10)

        self.case_var = ctk.StringVar(value="lower")

        RadioButton(frame, text="min\u00fasculas", variable=self.case_var, value="lower").pack(pady=5)
        RadioButton(frame, text="MAY\u00daSCULAS", variable=self.case_var, value="upper").pack(pady=5)
        RadioButton(frame, text="T\u00edtulo (Capital)", variable=self.case_var, value="title").pack(pady=5)

        ctk.CTkButton(frame, text="\U0001F504 Convertir", command=self._do_case, height=40).pack(pady=20)

    def _do_case(self) -> None:
        if not self._check_files():
            return
        case = self.case_var.get()
        from tools.rename_tool.processor import rename_case
        result = rename_case(self.files, case)
        self._handle_result(result)

    def _handle_result(self, result: Dict) -> None:
        if result.get("success"):
            self.status_label.configure(text=result["message"], text_color=COLORS.get("success"))
            if result.get("errors"):
                self.status_label.configure(text=f"{result['message']} - {len(result['errors'])} errores", text_color=COLORS.get("warning"))
            self._clear_files()
        else:
            # Mostrar message aunque sea False, no solo "Error"
            self.status_label.configure(text=result.get("message", "Error desconocido"), text_color=COLORS.get("error"))
