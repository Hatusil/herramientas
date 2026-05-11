"""
Edit Tab - Anotación, censura, extraer páginas.

Funciones:
- setup_edit_tab: configura la UI del tab
- add_annotation: agrega anotación
- redact_area: censura área
- extract_range: extrae rango de páginas
"""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.pdf_tool.ui.main_ui import PDFToolUI


def setup_edit_tab(ui: 'PDFToolUI') -> None:
    """Configura el tab de Editar."""
    frame = ui.tab_edit

    # Anotación
    ann_frame = ctk.CTkFrame(frame)
    ann_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(ann_frame, text="Agregar Anotación:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)

    pos_frame = ctk.CTkFrame(ann_frame, fg_color="transparent")
    pos_frame.pack(fill="x", padx=5)

    ctk.CTkLabel(pos_frame, text="Texto:").pack(side="left", padx=5)
    ui.annot_text = ctk.CTkEntry(pos_frame, width=150)
    ui.annot_text.pack(side="left", padx=5)

    ctk.CTkLabel(pos_frame, text="Página:").pack(side="left", padx=5)
    ui.annot_page = ctk.CTkEntry(pos_frame, width=50)
    ui.annot_page.insert(0, "0")
    ui.annot_page.pack(side="left", padx=5)

    ctk.CTkLabel(pos_frame, text="X:").pack(side="left", padx=5)
    ui.annot_x = ctk.CTkEntry(pos_frame, width=50)
    ui.annot_x.insert(0, "100")
    ui.annot_x.pack(side="left", padx=5)

    ctk.CTkLabel(pos_frame, text="Y:").pack(side="left", padx=5)
    ui.annot_y = ctk.CTkEntry(pos_frame, width=50)
    ui.annot_y.insert(0, "100")
    ui.annot_y.pack(side="left", padx=5)

    ctk.CTkButton(
        ann_frame,
        text="Agregar Anotación",
        command=lambda: ui._add_annotation()
    ).pack(pady=5)

    # Censurar
    redact_frame = ctk.CTkFrame(frame)
    redact_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(redact_frame, text="Censurar Área:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)

    redact_pos = ctk.CTkFrame(redact_frame, fg_color="transparent")
    redact_pos.pack(fill="x", padx=5)

    ctk.CTkLabel(redact_pos, text="Página:").pack(side="left", padx=5)
    ui.redact_page = ctk.CTkEntry(redact_pos, width=50)
    ui.redact_page.insert(0, "0")
    ui.redact_page.pack(side="left", padx=5)

    ctk.CTkLabel(redact_pos, text="X:").pack(side="left", padx=5)
    ui.redact_x = ctk.CTkEntry(redact_pos, width=50)
    ui.redact_x.insert(0, "100")
    ui.redact_x.pack(side="left", padx=5)

    ctk.CTkLabel(redact_pos, text="Y:").pack(side="left", padx=5)
    ui.redact_y = ctk.CTkEntry(redact_pos, width=50)
    ui.redact_y.insert(0, "100")
    ui.redact_y.pack(side="left", padx=5)

    ctk.CTkLabel(redact_pos, text="Ancho:").pack(side="left", padx=5)
    ui.redact_w = ctk.CTkEntry(redact_pos, width=50)
    ui.redact_w.insert(0, "100")
    ui.redact_w.pack(side="left", padx=5)

    ctk.CTkLabel(redact_pos, text="Alto:").pack(side="left", padx=5)
    ui.redact_h = ctk.CTkEntry(redact_pos, width=50)
    ui.redact_h.insert(0, "30")
    ui.redact_h.pack(side="left", padx=5)

    ctk.CTkButton(
        redact_frame,
        text="Censurar",
        command=lambda: ui._redact_area()
    ).pack(pady=5)

    # Extraer rango de páginas
    extract_frame = ctk.CTkFrame(frame)
    extract_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(extract_frame, text="Extraer páginas:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)

    range_frame = ctk.CTkFrame(extract_frame, fg_color="transparent")
    range_frame.pack(fill="x", padx=5)

    ctk.CTkLabel(range_frame, text="Desde:").pack(side="left", padx=5)
    ui.extract_start = ctk.CTkEntry(range_frame, width=50)
    ui.extract_start.insert(0, "1")
    ui.extract_start.pack(side="left", padx=5)

    ctk.CTkLabel(range_frame, text="Hasta:").pack(side="left", padx=5)
    ui.extract_end = ctk.CTkEntry(range_frame, width=50)
    ui.extract_end.insert(0, "1")
    ui.extract_end.pack(side="left", padx=5)

    ctk.CTkButton(
        extract_frame,
        text="Extraer Rango",
        command=lambda: ui._extract_range()
    ).pack(pady=5)


# Handlers

def add_annotation(ui: 'PDFToolUI') -> None:
    """Agrega una anotación al PDF."""
    if not ui._check_files():
        return

    ui.status_label.configure(text="Procesando...", text_color="blue")

    result = ui.process_async('add_annotation', ui.files, {
        'text': ui.annot_text.get(),
        'page': int(ui.annot_page.get() or 0),
        'x': float(ui.annot_x.get() or 100),
        'y': float(ui.annot_y.get() or 100),
    })

    ui._show_result(result)


def redact_area(ui: 'PDFToolUI') -> None:
    """Censura un área del PDF."""
    if not ui._check_files():
        return

    ui.status_label.configure(text="Procesando...", text_color="blue")

    result = ui.process_async('redact', ui.files, {
        'page': int(ui.redact_page.get() or 0),
        'x': float(ui.redact_x.get() or 100),
        'y': float(ui.redact_y.get() or 100),
        'width': float(ui.redact_w.get() or 100),
        'height': float(ui.redact_h.get() or 30),
    })

    ui._show_result(result)


def extract_range(ui: 'PDFToolUI') -> None:
    """Extrae un rango de páginas."""
    if not ui._check_files():
        return

    try:
        start = int(ui.extract_start.get())
        end = int(ui.extract_end.get())
    except ValueError:
        ui.status_label.configure(text="Números de página inválidos", text_color="red")
        return

    if start < 1 or end < 1:
        ui.status_label.configure(text="Los números deben ser >= 1", text_color="red")
        return

    if start > end:
        ui.status_label.configure(text="Inicio debe ser menor que fin", text_color="red")
        return

    ui.status_label.configure(text="Procesando...", text_color="blue")

    result = ui.process_async('extract_range', ui.files, {
        'start': start,
        'end': end,
    })

    ui._show_result(result)