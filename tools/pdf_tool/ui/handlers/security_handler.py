"""Security handler. R0: <80 lines."""
from __future__ import annotations
from typing import TYPE_CHECKING

from core.constants import COLORS

if TYPE_CHECKING:
    from tools.pdf_tool.ui.main_ui import PDFToolUI


def encrypt_pdf(ui: PDFToolUI) -> None:
    """Encrypt PDF with password."""
    if not ui.files:
        ui.status_label.configure(text="Seleccione un PDF primero", text_color=COLORS.get("warning", "orange"))
        return
    lock_pwd = getattr(ui, "lock_password", None)
    password = lock_pwd.get() if lock_pwd and hasattr(lock_pwd, "get") else ""
    if not password:
        ui.status_label.configure(text="Ingrese una contrasena", text_color=COLORS.get("warning", "orange"))
        return
    ui.status_label.configure(text="Procesando...", text_color="blue")
    ui.process_async("encrypt", ui.files, {"password": password})


def decrypt_pdf(ui: PDFToolUI) -> None:
    """Decrypt PDF."""
    if not ui.files:
        ui.status_label.configure(text="Seleccione un PDF primero", text_color=COLORS.get("warning", "orange"))
        return
    unlock_pwd = getattr(ui, "unlock_password", None)
    password = unlock_pwd.get() if unlock_pwd and hasattr(unlock_pwd, "get") else ""
    if not password:
        ui.status_label.configure(text="Ingrese la contrasena", text_color=COLORS.get("warning", "orange"))
        return
    ui.status_label.configure(text="Procesando...", text_color="blue")
    ui.process_async("decrypt", ui.files, {"password": password})
