"""Pipeline tab for PDF Tool."""
from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
import tkinter as tk
from tools.pdf_tool.ui.tabs.base_tab import PDFBaseTab
from core.constants import COLORS
from ui.theme_factory import create_frame, create_label, create_button, create_entry, create_option_menu, create_textbox

if TYPE_CHECKING:
    from tools.pdf_tool.ui.callbacks import PDFCallbacks


class PipelineTab(PDFBaseTab):
    def __init__(self, parent: ctk.CTkFrame, callbacks: PDFCallbacks, main_ui=None):
        super().__init__(parent, callbacks, main_ui)
        self._operations = []

    def _setup_frame(self) -> None:
        self._frame = create_frame(self._parent, fg_color="transparent")
        main_frame = create_frame(self._frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        create_label(
            main_frame, text="Pipeline de Operaciones",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(0, 10))

        add_frame = create_frame(main_frame)
        add_frame.pack(fill="x", pady=5)
        create_label(add_frame, text="Operacion:").pack(side="left", padx=5)
        self._op_type = create_option_menu(
            add_frame,
            values=["reorder", "watermark", "rotate", "extract"],
            width=100,
            command=self._update_inputs,
        )
        self._op_type.set("reorder")
        self._op_type.pack(side="left", padx=5)

        params_frame = create_frame(main_frame)
        params_frame.pack(fill="x", pady=5)

        self._reorder_frame = create_frame(params_frame)
        create_label(self._reorder_frame, text="Orden (ej: 3,1,2):").pack(side="left", padx=5)
        self._reorder_input = create_entry(self._reorder_frame, width=150)
        self._reorder_input.pack(side="left", padx=5)
        self._reorder_frame.pack(fill="x", padx=5)

        self._wm_frame = create_frame(params_frame)
        create_label(self._wm_frame, text="Texto:").pack(side="left", padx=5)
        self._wm_text = create_entry(self._wm_frame, width=150)
        self._wm_text.insert(0, "DRAFT")
        self._wm_text.pack(side="left", padx=5)

        self._rotate_frame = create_frame(params_frame)
        create_label(self._rotate_frame, text="Grados:").pack(side="left", padx=5)
        self._rotate_deg = create_option_menu(
            self._rotate_frame, values=["90", "180", "270"], width=80,
        )
        self._rotate_deg.set("90")
        self._rotate_deg.pack(side="left", padx=5)

        self._extract_frame = create_frame(params_frame)
        create_label(self._extract_frame, text="Paginas (ej: 1,3,5):").pack(side="left", padx=5)
        self._extract_input = create_entry(self._extract_frame, width=150)
        self._extract_input.pack(side="left", padx=5)

        create_button(
            main_frame, text="Agregar a Pipeline",
            command=self._add_to_pipeline, height=35,
        ).pack(pady=10, fill="x")

        list_frame = create_frame(main_frame)
        list_frame.pack(fill="both", expand=True, pady=10)
        create_label(list_frame, text="Operaciones acumuladas:").pack(anchor="w", pady=5)
        self._listbox = create_textbox(
            list_frame, height=150,
        )
        self._listbox.pack(padx=10, pady=5, fill="both", expand=True)

        action_frame = create_frame(main_frame, fg_color="transparent")
        action_frame.pack(fill="x", pady=5)
        create_button(
            action_frame, text="Limpiar", command=self._clear, width=100,
        ).pack(side="left", padx=5)
        create_button(
            action_frame, text="Ejecutar Pipeline", command=self._execute,
            width=150, fg_color=COLORS.get("success"),
        ).pack(side="left", padx=5, fill="x", expand=True)

    def get_frame(self) -> ctk.CTkFrame:
        return self._frame

    def _update_inputs(self, _=None) -> None:
        self._reorder_frame.pack_forget()
        self._wm_frame.pack_forget()
        self._rotate_frame.pack_forget()
        self._extract_frame.pack_forget()
        op_type = self._op_type.get()
        targets = {
            "reorder": self._reorder_frame,
            "watermark": self._wm_frame,
            "rotate": self._rotate_frame,
            "extract": self._extract_frame,
        }
        frame = targets.get(op_type)
        if frame:
            frame.pack(fill="x", padx=5)

    def _add_to_pipeline(self) -> None:
        if not self._main_ui.files:
            self.update_status("Seleccione un PDF primero", COLORS.get("warning", "orange"))
            return
        op_type = self._op_type.get()
        params = {}
        try:
            if op_type == "reorder":
                order_str = self._reorder_input.get().strip()
                if not order_str:
                    self.update_status("Ingrese el orden de paginas", COLORS.get("warning", "orange"))
                    return
                params["new_order"] = [int(p) for p in order_str.split(",")]
            elif op_type == "watermark":
                params["text"] = self._wm_text.get().strip() or "DRAFT"
            elif op_type == "rotate":
                params["degrees"] = int(self._rotate_deg.get())
            elif op_type == "extract":
                pages_str = self._extract_input.get().strip()
                if not pages_str:
                    self.update_status("Ingrese las paginas", COLORS.get("warning", "orange"))
                    return
                params["pages"] = [int(p.strip()) for p in pages_str.split(",")]
        except ValueError:
            self.update_status("Parametros invalidos", "red")
            return

        self._operations.append({"type": op_type, "params": params})
        self._refresh_list()
        self.update_status(f"Operacion '{op_type}' anadida al pipeline", "green")
        if op_type == "reorder":
            self._reorder_input.delete(0, tk.END)
        elif op_type == "watermark":
            self._wm_text.delete(0, tk.END)
            self._wm_text.insert(0, "DRAFT")
        elif op_type == "extract":
            self._extract_input.delete(0, tk.END)

    def _refresh_list(self) -> None:
        self._listbox.delete("1.0", tk.END)
        for i, op in enumerate(self._operations):
            op_type = op["type"]
            params = op["params"]
            descs = {
                "reorder": f"Reorder: {params.get('new_order', [])}",
                "watermark": f"Watermark: {params.get('text', '')}",
                "rotate": f"Rotate: {params.get('degrees', 0)}deg",
                "extract": f"Extract: {params.get('pages', [])}",
            }
            desc = descs.get(op_type, op_type)
            self._listbox.insert(tk.END, f"{i+1}. {desc}\n")
        if self._operations:
            self._listbox.insert(tk.END, f"\nTotal: {len(self._operations)} operaciones")

    def _clear(self) -> None:
        self._operations.clear()
        self._refresh_list()
        self.update_status("Pipeline limpiado", "gray")

    def _execute(self) -> None:
        self._main_ui.pipeline_operations = self._operations
        from tools.pdf_tool.ui.handlers.pipeline_handler import execute_pipeline
        execute_pipeline(self._main_ui)
        self._refresh_list()
