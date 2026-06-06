"""Security handler. R0: <80 lines."""
from __future__ import annotations
from typing import TYPE_CHECKING

from core.constants import COLORS

if TYPE_CHECKING:
    from tools.pdf_tool.ui.state import PDFState


def encrypt_pdf(state: "PDFState") -> None:
    """Encrypt PDF with password."""
    if not state.ctx.files:
        if state.ctx.status_label is not None:
            state.ctx.status_label.configure(
                text="Seleccione un PDF primero",
                text_color=COLORS.get("warning", "orange"),
            )
        return
    lock_pwd = state.lock_password
    password = lock_pwd.get() if lock_pwd is not None else ""
    if not password:
        if state.ctx.status_label is not None:
            state.ctx.status_label.configure(
                text="Ingrese una contrasena",
                text_color=COLORS.get("warning", "orange"),
            )
        return
    if state.ctx.status_label is not None:
        state.ctx.status_label.configure(text="Procesando...", text_color="blue")
    if state.ctx.process_async is not None:
        state.ctx.process_async("encrypt", state.ctx.files, {"password": password})


def decrypt_pdf(state: "PDFState") -> None:
    """Decrypt PDF."""
    if not state.ctx.files:
        if state.ctx.status_label is not None:
            state.ctx.status_label.configure(
                text="Seleccione un PDF primero",
                text_color=COLORS.get("warning", "orange"),
            )
        return
    unlock_pwd = state.unlock_password
    password = unlock_pwd.get() if unlock_pwd is not None else ""
    if not password:
        if state.ctx.status_label is not None:
            state.ctx.status_label.configure(
                text="Ingrese la contrasena",
                text_color=COLORS.get("warning", "orange"),
            )
        return
    if state.ctx.status_label is not None:
        state.ctx.status_label.configure(text="Procesando...", text_color="blue")
    if state.ctx.process_async is not None:
        state.ctx.process_async("decrypt", state.ctx.files, {"password": password})
