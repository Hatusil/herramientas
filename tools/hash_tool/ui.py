"""UI: Interfaz para Hash/Checksum tool."""
from ui.radiobutton import RadioButton
import customtkinter as ctk
import tkinter as tk
from typing import Callable
from core.base_tool_ui import BaseToolUI
from core.tool_builder import create_standard_tool_ui


class HashToolUI(BaseToolUI):
    """UI para calcular y verificar checksums."""

    def __init__(self, master, on_process: Callable, **kwargs):
        super().__init__(master, on_process, **kwargs)
        self.is_processing = False

    def _setup_ui(self):
        r = create_standard_tool_ui(
            self, ("\U0001F510", "Hash y Checksums"),
            "\U0001F510 Calcula y verifica hashes (MD5/SHA1/SHA256/SHA512) para verificar integridad",
            selector_type="file",
            tab_configs=[{"name": "Calcular"}, {"name": "Verificar"}, {"name": "Lista de Archivos"}],
            help_config={
                "usage": [
                    "1. \U0001F4E5 Agregar archivos (+)",
                    "2. \u2611\ufe0f Seleccionar con Ctrl+click o botones",
                    "3. \U0001F3AF Seleccionar algoritmo (SHA256 recomendado)",
                    "4. \U0001F522 Click en calcular (procesa seleccionados)",
                    "",
                    "\U0001F4CC \u00bfPARA QU\u00c9 SIRVE?",
                    "\u2022 Verificar descargas: Compara el hash calculado con el del servidor",
                    "\u2022 Detectar cambios: Si hash es diferente, el archivo fue modificado",
                    "\u2022 Identificar duplicados: Mismo hash = mismo archivo",
                ],
                "warnings": [
                    "\u26a0\ufe0f Hash diferente = archivo modificado o corrupto",
                    "\u26a0\ufe0f MD5 no es seguro - solo para verificaci\u00f3n de descarga",
                    "\u26a0\ufe0f Verificaci\u00f3n debe ser exacta (case-sensitive)",
                    "\u26a0\ufe0f Copiar un archivo NO cambia su hash",
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
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=10)

        info = ctk.CTkLabel(
            frame, text="SHA256 = recommended | MD5 = only for old downloads",
            text_color="gray", font=ctk.CTkFont(size=11)
        )
        info.pack(pady=5)

        self.algo_var = ctk.StringVar(value="sha256")

        for algo in [("md5", "MD5"), ("sha1", "SHA1"), ("sha256", "SHA256"), ("sha512", "SHA512")]:
            RadioButton(frame, text=algo[1], variable=self.algo_var, value=algo[0]).pack(pady=2)

        ctk.CTkButton(
            frame, text="\U0001F522 Calcular Hash",
            command=self._calculate, height=40
        ).pack(pady=20)

        self.calc_result = ctk.CTkTextbox(frame, width=400, height=150)
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
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)

        info = ctk.CTkLabel(
            frame, text="Ingresa el hash del servidor o el original para comparar",
            text_color="gray", font=ctk.CTkFont(size=12)
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

        self.verify_result = ctk.CTkTextbox(frame, width=400, height=150)
        self.verify_result.pack(padx=10, pady=10)

    def _verify(self) -> None:
        if not self._check_files():
            return
        expected = self.expected_hash.get().strip()
        if not expected:
            self.status_label.configure(text="Ingrese el hash esperado", text_color="#FFA500")
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
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=10)

        ctk.CTkButton(
            frame, text="\U0001F4CB Calcular Todos los Hashes",
            command=self._calc_all
        ).pack(pady=10)

        self.all_hashes = ctk.CTkTextbox(frame, width=400, height=250)
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
