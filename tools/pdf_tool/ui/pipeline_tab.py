"""
Pipeline Tab - Pipeline de operaciones encadenadas.

Funciones:
- setup_pipeline_tab: configura la UI del tab
- update_pipeline_inputs: muestra/oculta inputs según tipo
- add_to_pipeline: agrega operación
- refresh_pipeline_list: actualiza la lista
- clear_pipeline: limpia operaciones
- execute_pipeline: ejecuta todas las operaciones
"""

import os
import customtkinter as ctk
import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.pdf_tool.ui.main_ui import PDFToolUI


def setup_pipeline_tab(ui: 'PDFToolUI') -> None:
    """Configura el tab de Pipeline."""
    frame = ui.tab_pipeline
    ui.pipeline_operations = []

    main_frame = ctk.CTkFrame(frame)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    ctk.CTkLabel(
        main_frame,
        text="Pipeline de Operaciones",
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(pady=(0, 10))

    # Agregar operación
    add_frame = ctk.CTkFrame(main_frame)
    add_frame.pack(fill="x", pady=5)

    ctk.CTkLabel(add_frame, text="Operación:").pack(side="left", padx=5)
    ui.pipeline_op_type = ctk.CTkOptionMenu(
        add_frame,
        values=["reorder", "watermark", "rotate", "extract"],
        width=100
    )
    ui.pipeline_op_type.set("reorder")
    ui.pipeline_op_type.pack(side="left", padx=5)

    # Parámetros dinámica
    params_frame = ctk.CTkFrame(main_frame)
    params_frame.pack(fill="x", pady=5)

    # Reorder input
    ui.pipeline_reorder_frame = ctk.CTkFrame(params_frame)
    ui.pipeline_reorder_frame.pack(fill="x", padx=5)

    ctk.CTkLabel(ui.pipeline_reorder_frame, text="Orden (ej: 3,1,2):").pack(side="left", padx=5)
    ui.pipeline_reorder_input = ctk.CTkEntry(ui.pipeline_reorder_frame, width=150)
    ui.pipeline_reorder_input.pack(side="left", padx=5)

    # Watermark input
    ui.pipeline_wm_frame = ctk.CTkFrame(params_frame)

    ctk.CTkLabel(ui.pipeline_wm_frame, text="Texto:").pack(side="left", padx=5)
    ui.pipeline_wm_text = ctk.CTkEntry(ui.pipeline_wm_frame, width=150)
    ui.pipeline_wm_text.insert(0, "DRAFT")
    ui.pipeline_wm_text.pack(side="left", padx=5)

    # Rotate input
    ui.pipeline_rotate_frame = ctk.CTkFrame(params_frame)

    ctk.CTkLabel(ui.pipeline_rotate_frame, text="Grados:").pack(side="left", padx=5)
    ui.pipeline_rotate_deg = ctk.CTkOptionMenu(
        ui.pipeline_rotate_frame,
        values=["90", "180", "270"],
        width=80
    )
    ui.pipeline_rotate_deg.set("90")
    ui.pipeline_rotate_deg.pack(side="left", padx=5)

    # Extract input
    ui.pipeline_extract_frame = ctk.CTkFrame(params_frame)

    ctk.CTkLabel(ui.pipeline_extract_frame, text="Páginas (ej: 1,3,5):").pack(side="left", padx=5)
    ui.pipeline_extract_input = ctk.CTkEntry(ui.pipeline_extract_frame, width=150)
    ui.pipeline_extract_input.pack(side="left", padx=5)

    # Botón agregar
    ctk.CTkButton(
        main_frame,
        text="Agregar a Pipeline",
        command=lambda: ui._add_to_pipeline(),
        height=35
    ).pack(pady=10, fill="x")

    # Lista de operaciones
    list_frame = ctk.CTkFrame(main_frame)
    list_frame.pack(fill="both", expand=True, pady=10)

    ctk.CTkLabel(list_frame, text="Operaciones acumuladas:").pack(anchor="w", pady=5)

    ui.pipeline_listbox = ctk.CTkTextbox(list_frame, height=150)
    ui.pipeline_listbox.pack(padx=10, pady=5, fill="both", expand=True)

    # Botones de acción
    action_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    action_frame.pack(fill="x", pady=5)

    ctk.CTkButton(
        action_frame,
        text="Limpiar",
        command=lambda: ui._clear_pipeline(),
        width=100
    ).pack(side="left", padx=5)

    ctk.CTkButton(
        action_frame,
        text="Ejecutar Pipeline",
        command=lambda: ui._execute_pipeline(),
        width=150,
        fg_color="#2CC985"
    ).pack(side="left", padx=5, fill="x", expand=True)

    # Actualizar inputs visibles
    ui._update_pipeline_inputs()


# Handlers

def update_pipeline_inputs(ui: 'PDFToolUI') -> None:
    """Actualiza los inputs según el tipo de operación."""
    ui.pipeline_reorder_frame.pack_forget()
    ui.pipeline_wm_frame.pack_forget()
    ui.pipeline_rotate_frame.pack_forget()
    ui.pipeline_extract_frame.pack_forget()

    op_type = ui.pipeline_op_type.get()

    if op_type == "reorder":
        ui.pipeline_reorder_frame.pack(fill="x", padx=5)
    elif op_type == "watermark":
        ui.pipeline_wm_frame.pack(fill="x", padx=5)
    elif op_type == "rotate":
        ui.pipeline_rotate_frame.pack(fill="x", padx=5)
    elif op_type == "extract":
        ui.pipeline_extract_frame.pack(fill="x", padx=5)


def add_to_pipeline(ui: 'PDFToolUI') -> None:
    """Agrega una operación al pipeline."""
    if not ui._check_files():
        ui.status_label.configure(text="Seleccione un PDF primero", text_color="#FFA500")
        return

    op_type = ui.pipeline_op_type.get()
    params = {}

    if op_type == "reorder":
        order_str = ui.pipeline_reorder_input.get().strip()
        if not order_str:
            ui.status_label.configure(text="Ingrese el orden de páginas", text_color="#FFA500")
            return
        try:
            params['new_order'] = [int(p) for p in order_str.split(',')]
        except ValueError:
            ui.status_label.configure(text="Orden inválido", text_color="red")
            return

    elif op_type == "watermark":
        text = ui.pipeline_wm_text.get().strip()
        if not text:
            text = "DRAFT"
        params['text'] = text

    elif op_type == "rotate":
        params['degrees'] = int(ui.pipeline_rotate_deg.get())

    elif op_type == "extract":
        pages_str = ui.pipeline_extract_input.get().strip()
        if not pages_str:
            ui.status_label.configure(text="Ingrese las páginas", text_color="#FFA500")
            return
        try:
            params['pages'] = [int(p.strip()) for p in pages_str.split(',')]
        except ValueError:
            ui.status_label.configure(text="Páginas inválidas", text_color="red")
            return

    ui.pipeline_operations.append({
        'type': op_type,
        'params': params
    })

    ui._refresh_pipeline_list()

    ui.status_label.configure(text=f"Operación '{op_type}' añadida al pipeline", text_color="green")

    if op_type == "reorder":
        ui.pipeline_reorder_input.delete(0, tk.END)
    elif op_type == "watermark":
        ui.pipeline_wm_text.delete(0, tk.END)
        ui.pipeline_wm_text.insert(0, "DRAFT")
    elif op_type == "extract":
        ui.pipeline_extract_input.delete(0, tk.END)


def refresh_pipeline_list(ui: 'PDFToolUI') -> None:
    """Actualiza la lista de operaciones."""
    ui.pipeline_listbox.delete("1.0", tk.END)

    for i, op in enumerate(ui.pipeline_operations):
        op_type = op['type']
        params = op['params']

        if op_type == "reorder":
            desc = f"{i+1}. Reorder: {params.get('new_order', [])}"
        elif op_type == "watermark":
            desc = f"{i+1}. Watermark: {params.get('text', '')}"
        elif op_type == "rotate":
            desc = f"{i+1}. Rotate: {params.get('degrees', 0)}°"
        elif op_type == "extract":
            desc = f"{i+1}. Extract: {params.get('pages', [])}"
        else:
            desc = f"{i+1}. {op_type}"

        ui.pipeline_listbox.insert(tk.END, desc + "\n")

    if ui.pipeline_operations:
        ui.pipeline_listbox.insert(tk.END, f"\nTotal: {len(ui.pipeline_operations)} operaciones")


def clear_pipeline(ui: 'PDFToolUI') -> None:
    """Limpia las operaciones acumuladas."""
    ui.pipeline_operations.clear()
    ui._refresh_pipeline_list()
    ui.status_label.configure(text="Pipeline limpiado", text_color="gray")


def execute_pipeline(ui: 'PDFToolUI') -> None:
    """Ejecuta todas las operaciones del pipeline."""
    if not ui._check_files():
        ui.status_label.configure(text="Seleccione un PDF primero", text_color="#FFA500")
        return

    if not ui.pipeline_operations:
        ui.status_label.configure(text="No hay operaciones en el pipeline", text_color="#FFA500")
        return

    ui.status_label.configure(text="Ejecutando pipeline...", text_color="blue")

    from tools.pdf_tool.modules.pipeline import execute_pipeline_operations

    result = execute_pipeline_operations(ui.files[0], ui.pipeline_operations)

    if result.get('success'):
        output_file = result.get('output_file')
        ui.status_label.configure(
            text=f"Pipeline completado: {result.get('message', '')}",
            text_color="green"
        )

        ui.pipeline_operations.clear()
        ui._refresh_pipeline_list()

        if output_file and os.path.exists(output_file):
            ui.files = [output_file]
            ui._update_file_list()
    else:
        ui.status_label.configure(
            text=f"Error: {result.get('error', 'Error desconocido')}",
            text_color="red"
        )