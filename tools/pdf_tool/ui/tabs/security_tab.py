"""Security tab for PDF Tool."""
from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from tools.pdf_tool.ui.tabs.base_tab import PDFBaseTab
from ui.theme_factory import create_frame, create_label, create_button, create_entry

if TYPE_CHECKING:
    from tools.pdf_tool.ui.callbacks import PDFCallbacks


class SecurityTab(PDFBaseTab):
    def __init__(self, parent: ctk.CTkFrame, callbacks: PDFCallbacks, main_ui=None):
        super().__init__(parent, callbacks, main_ui)

    def _setup_frame(self) -> None:
        self._frame = create_frame(self._parent, fg_color="transparent")
        lock_frame = create_frame(self._frame)
        lock_frame.pack(fill="x", padx=10, pady=5)
        create_label(
            lock_frame, text="Bloquear PDF:", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=5)
        pwd_frame = create_frame(lock_frame, fg_color="transparent")
        pwd_frame.pack(fill="x", padx=5)
        create_label(pwd_frame, text="Contrasena:").pack(side="left", padx=5)
        self._lock_password = create_entry(pwd_frame, show="*", width=150)
        self._lock_password.pack(side="left", padx=5)
        create_button(
            lock_frame, text="Bloquear", command=self._encrypt, height=40,
        ).pack(pady=5)

        unlock_frame = create_frame(self._frame)
        unlock_frame.pack(fill="x", padx=10, pady=5)
        create_label(
            unlock_frame, text="Desbloquear PDF:", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=5)
        unlock_pwd = create_frame(unlock_frame, fg_color="transparent")
        unlock_pwd.pack(fill="x", padx=5)
        create_label(unlock_pwd, text="Contrasena:").pack(side="left", padx=5)
        self._unlock_password = create_entry(unlock_pwd, show="*", width=150)
        self._unlock_password.pack(side="left", padx=5)
        create_button(
            unlock_frame, text="Desbloquear", command=self._decrypt, height=40,
        ).pack(pady=5)

    def get_frame(self) -> ctk.CTkFrame:
        return self._frame

    def _encrypt(self) -> None:
        from tools.pdf_tool.ui.handlers.security_handler import encrypt_pdf
        self._main_ui.lock_password = self._lock_password
        encrypt_pdf(self._main_ui)

    def _decrypt(self) -> None:
        from tools.pdf_tool.ui.handlers.security_handler import decrypt_pdf
        self._main_ui.unlock_password = self._unlock_password
        decrypt_pdf(self._main_ui)
