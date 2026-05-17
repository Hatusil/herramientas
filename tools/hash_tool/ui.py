"""UI: Interfaz para Hash/Checksum tool."""
from ui.radiobutton import RadioButton
import customtkinter as ctk
import tkinter as tk
from typing import Callable
from core.base_tool_ui import BaseToolUI
from core.tool_builder import create_standard_tool_ui
from core.constants import font, COLORS


class HashToolUI(BaseToolUI):
    """UI para calcular y verificar checksums."""

    def __init__(self, master, on_process: Callable, **kwargs):
        super().__init__(master, on_process, **kwargs)
        self.is_processing = False

    def _setup_ui(self):
        r = create_standard_tool_ui(
            self, ("\U0001F510", "Hash y Checksums"),
            "",  # description moved to help_config
            selector_type="file",
            tab_configs=[{"name": "Calcular"}, {"name": "Verificar"}, {"name": "Lista de Archivos"}],
            help_config={
                "description": "🔐 Calcula y verifica hashes (MD5/SHA1/SHA256/SHA512) para verificar integridad de archivos",
                "usage": [
                    "1. 📥 Agregar archivos (+)",
                    "2. ☑️ Seleccionar con Ctrl+click o botones",
                    "3. 🎯 Seleccionar algoritmo (SHA256 recomendado)",
                    "4. ▶️ Click en calcular (procesa seleccionados)",
                ],
                "tips": [
                    "💡 SHA256 es el balance óptimo seguridad/velocidad",
                    "💡 Hash = identidad única del archivo",
                    "💡 Verificá descargas comparando con el hash del servidor",
                ],
                "warnings": [
                    "⚠️ Hash diferente = archivo modificado o corrupto",
                    "⚠️ MD5 no es seguro - solo para verificación de descarga",
                    "⚠️ Verificación debe ser exacta (case-sensitive)",
                    "⚠️ Copiar un archivo NO cambia su hash",
                ],
            },
        )
        self.files = r["files"]
        self.file_listbox = r["listbox"]
        self.status_label = r["status_label"]
        self.tab_calc = r["tabs"]["Calcular"]
        self.tab_verify = r["tabs"]["Verificar"]
        self.tab_list = r["tabs"]["Lista de Archivos"]

        self._setup_calc_tab()
        self._setup_verify_tab()
        self._setup_list_tab()

    def _setup_calc_tab(self) -> None:
        frame = self.tab_calc

        ctk.CTkLabel(
            frame, text="Calcular hash (huella \u00fanica del archivo):",
            font=font("normal", "bold")
        ).pack(pady=10)

        info = ctk.CTkLabel(
            frame, text="SHA256 = recommended | MD5 = only for old downloads",
            text_color="gray", font=font("xsmall")
        )
        info.pack(pady=5)

        self.algo_var = ctk.StringVar(value="sha256")

        for algo in [("md5", "MD5"), ("sha1", "SHA1"), ("sha256", "SHA256"), ("sha512", "SHA512")]:
            RadioButton(frame, text=algo[1], variable=self.algo_var, value=algo[0]).pack(pady=2)

        ctk.CTkButton(
            frame, text="\U0001F522 Calcular Hash",
            command=self._calculate, height=40
        ).pack(pady=20)

        self.calc_result = ctk.CTkTextbox(frame, width=400, height=150, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"])
        self.calc_result.pack(padx=10, pady=10)

    def _calculate(self) -> None:
        if not self._check_files():
            return
        algo = self.algo_var.get()
        self.calc_result.delete("1.0", tk.END)
        self.calc_result.insert("1.0", f"Calculando {algo.upper()}...\n\n")
        from tools.hash_tool.processor import calculate_hash
        for f in self.files:
            result = calculate_hash(f, algo)
            if result["success"]:
                self.calc_result.insert(tk.END, f"{result['file_name']}:\n  {result['hash']}\n\n")
            else:
                self.calc_result.insert(tk.END, f"Error: {result.get('error')}\n")
        self.status_label.configure(text=f"Calculado para {len(self.files)} archivos", text_color="green")

    def _setup_verify_tab(self) -> None:
        frame = self.tab_verify

        ctk.CTkLabel(
            frame, text="Verificar hash (comparar con valor conocido):",
            font=font("normal", "bold")
        ).pack(pady=5)

        info = ctk.CTkLabel(
            frame, text="Ingresa el hash del servidor o el original para comparar",
            text_color="gray", font=font("small")
        )
        info.pack(pady=5)

        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(input_frame, text="Hash esperado:").pack(side="left", padx=5)
        self.expected_hash = ctk.CTkEntry(input_frame, width=300)
        self.expected_hash.pack(side="left", padx=5)

        algo_frame = ctk.CTkFrame(frame)
        algo_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(algo_frame, text="Algoritmo:").pack(side="left", padx=5)
        self.verify_algo = ctk.StringVar(value="sha256")

        for algo in [("md5", "MD5"), ("sha1", "SHA1"), ("sha256", "SHA256")]:
            RadioButton(algo_frame, text=algo[1], variable=self.verify_algo, value=algo[0]).pack(side="left", padx=10)

        ctk.CTkButton(
            frame, text="\u2713 Verificar", command=self._verify, height=40
        ).pack(pady=10)

        self.verify_result = ctk.CTkTextbox(frame, width=400, height=150, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"])
        self.verify_result.pack(padx=10, pady=10)

    def _verify(self) -> None:
        if not self._check_files():
            return
        expected = self.expected_hash.get().strip()
        if not expected:
            self.status_label.configure(text="Ingrese el hash esperado", text_color=COLORS.get("warning"))
            return
        algo = self.verify_algo.get()
        self.verify_result.delete("1.0", tk.END)
        from tools.hash_tool.processor import verify_hash
        for file_path in self.files:
            result = verify_hash(file_path, expected, algo)
            if result["success"]:
                if result["match"]:
                    self.verify_result.insert(tk.END, f"[OK] {result['file_name']}: \u2705 CORRESPONDE\n")
                else:
                    self.verify_result.insert(
                        tk.END,
                        f"[FAIL] {result['file_name']}: \u274c NO CORRESPONDE\n"
                        f"  Esperado: {result['expected'][:20]}...\n"
                        f"  Actual: {result['actual'][:20]}...\n",
                    )

    def _setup_list_tab(self) -> None:
        frame = self.tab_list

        ctk.CTkLabel(
            frame, text="Lista de archivos con todos los hashes:",
            font=font("normal", "bold")
        ).pack(pady=10)

        ctk.CTkButton(
            frame, text="\U0001F4CB Calcular Todos los Hashes",
            command=self._calc_all
        ).pack(pady=10)

        self.all_hashes = ctk.CTkTextbox(frame, width=400, height=250, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"])
        self.all_hashes.pack(padx=10, pady=10)

    def _calc_all(self) -> None:
        if not self._check_files():
            return
        self.all_hashes.delete("1.0", tk.END)
        from tools.hash_tool.processor import calculate_all_hashes
        for f in self.files:
            result = calculate_all_hashes(f)
            if result["success"]:
                self.all_hashes.insert(tk.END, f"\U0001F4C4 {result['file_name']} ({result['file_size']} bytes)\n")
                for algo, h in result["hashes"].items():
                    self.all_hashes.insert(tk.END, f"  {algo}: {h}\n")
                self.all_hashes.insert(tk.END, "\n")
        self.status_label.configure(text="Todos los hashes calculados", text_color="green")
