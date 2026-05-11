"""
Security Tab - Encriptar y desencriptar PDFs.

Funciones:
- setup_security_tab: configura la UI del tab
- encrypt_pdf: encripta el PDF
- decrypt_pdf: desencripta el PDF
"""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.pdf_tool.ui.main_ui import PDFToolUI


def setup_security_tab(ui: 'PDFToolUI') -> None:
    """Configura el tab de Seguridad."""
    frame = ui.tab_security

    # Bloquear
    lock_frame = ctk.CTkFrame(frame)
    lock_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(lock_frame, text="Bloquear PDF:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)

    pwd_frame = ctk.CTkFrame(lock_frame, fg_color="transparent")
    pwd_frame.pack(fill="x", padx=5)

    ctk.CTkLabel(pwd_frame, text="Contraseña:").pack(side="left", padx=5)
    ui.lock_password = ctk.CTkEntry(pwd_frame, show="*", width=150)
    ui.lock_password.pack(side="left", padx=5)

    ctk.CTkButton(
        lock_frame,
        text="Bloquear",
        command=lambda: ui._encrypt_pdf(),
        height=40
    ).pack(pady=5)

    # Desbloquear
    unlock_frame = ctk.CTkFrame(frame)
    unlock_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(unlock_frame, text="Desbloquear PDF:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)

    unlock_pwd = ctk.CTkFrame(unlock_frame, fg_color="transparent")
    unlock_pwd.pack(fill="x", padx=5)

    ctk.CTkLabel(unlock_pwd, text="Contraseña:").pack(side="left", padx=5)
    ui.unlock_password = ctk.CTkEntry(unlock_pwd, show="*", width=150)
    ui.unlock_password.pack(side="left", padx=5)

    ctk.CTkButton(
        unlock_frame,
        text="Desbloquear",
        command=lambda: ui._decrypt_pdf(),
        height=40
    ).pack(pady=5)


# Handlers

def encrypt_pdf(ui: 'PDFToolUI') -> None:
    """Encripta el PDF con contraseña."""
    if not ui._check_files():
        return

    password = ui.lock_password.get()
    if not password:
        ui.status_label.configure(text="Ingrese una contraseña", text_color="#FFA500")
        return

    ui.status_label.configure(text="Procesando...", text_color="blue")

    result = ui.process_async('encrypt', ui.files, {'password': password})

    ui._show_result(result)


def decrypt_pdf(ui: 'PDFToolUI') -> None:
    """Desencripta el PDF."""
    if not ui._check_files():
        return

    password = ui.unlock_password.get()
    if not password:
        ui.status_label.configure(text="Ingrese la contraseña", text_color="#FFA500")
        return

    ui.status_label.configure(text="Procesando...", text_color="blue")

    result = ui.process_async('decrypt', ui.files, {'password': password})

    ui._show_result(result)