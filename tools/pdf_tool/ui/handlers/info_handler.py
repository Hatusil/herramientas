"""PDF info handler. R0: <80 lines."""
from __future__ import annotations
from typing import TYPE_CHECKING
import tkinter as tk

if TYPE_CHECKING:
    from tools.pdf_tool.ui.main_ui import PDFToolUI


def get_pdf_info(ui: PDFToolUI) -> None:
    """Show PDF metadata in the info text box."""
    if not ui._check_files():
        return
    from tools.pdf_tool.processor import get_pdf_info as _get_info

    ui.info_text.delete("1.0", tk.END)
    for file_path in ui.files:
        info = _get_info(file_path)
        if info.get("success"):
            ui.info_text.insert(tk.END, _format_info(info))
        else:
            ui.info_text.insert(
                tk.END,
                f"Error con {info.get('file_name', file_path)}: {info.get('error', 'Error desconocido')}\n\n",
            )


def _format_info(info: dict) -> str:
    lines = [
        f"Informacion del PDF:",
        f"Archivo: {info.get('file_name', 'N/A')}",
        f"Tamano: {info.get('file_size', 0)} bytes",
        f"Paginas: {info.get('num_pages', 0)}",
        f"Encriptado: {'Si' if info.get('is_encrypted') else 'No'}",
        "",
        "Metadatos:",
        f"Titulo: {info.get('title', 'N/A')}",
        f"Autor: {info.get('author', 'N/A')}",
        f"Creador: {info.get('creator', 'N/A')}",
        f"Productor: {info.get('producer', 'N/A')}",
        f"Fecha creacion: {info.get('creation_date', 'N/A')}",
        "",
    ]
    pages = info.get("pages", [])
    if pages:
        lines.append("Paginas:")
        for p in pages[:10]:
            lines.append(f"Pagina {p['page_num']}: Rotacion={p['rotation']}deg")
    lines.append("")
    return "\n".join(lines)


def get_page_count(ui: PDFToolUI) -> None:
    """Get page count for current file."""
    if not ui._check_files():
        return
    from tools.pdf_tool.processor import get_pdf_info as _get_info

    info = _get_info(ui.files[0])
    count = info.get("num_pages", 0)
    ui.status_label.configure(text=f"Paginas: {count}", text_color="blue")
