"""
HelpPanel: Componente reutilizable para mostrar ayuda/descripción en las herramientas.
Muestra la ayuda como un popup flotante (CTkToplevel) que no desplaza el contenido.
"""
import tkinter as tk
import customtkinter as ctk
from pathlib import Path

from core import constants
from core.constants import font


class HelpPopup:
    """
    Popup flotante de ayuda que aparece sobre la herramienta.
    No desplaza el contenido de la herramienta.
    """
    
    def __init__(self, parent, title: str = "Ayuda",
                 description: str = "",
                 usage: list = None,
                 tips: list = None,
                 warnings: list = None):
        self._parent = parent
        self._usage = usage or []
        self._tips = tips or []
        self._warnings = warnings or []
        
        # Crear ventana Toplevel
        self.window = ctk.CTkToplevel(parent)
        self.window.title(title)
        self.window.geometry("500x450")
        self.window.resizable(False, False)
        
        # Centrar en la pantalla (no relativo al padre)
        self.window.transient(parent)
        parent.update_idletasks()
        
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        
        win_w = 500
        win_h = 450
        
        x = (screen_w - win_w) // 2
        y = (screen_h - win_h) // 2
        
        self.window.geometry(f"+{x}+{y}")

        # Bloquear interacción con la ventana padre
        self.window.grab_set()
        
        # Get current theme colors (COLORS is already the current theme dict)
        bg_color = constants.COLORS.get("bg_dark")
        text_color = constants.COLORS.get("text_primary")
        text_secondary = constants.COLORS.get("text_secondary")
        primary = constants.COLORS.get("primary")
        success = constants.COLORS.get("success")
        warning = constants.COLORS.get("warning")

        # Frame principal
        main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # CTkTextbox tiene scrollbar interno
        textbox = ctk.CTkTextbox(
            main_frame,
            font=font("small"),
            text_color=text_color,
            fg_color=bg_color,
            border_width=0,
            wrap="word",
            scrollbar_button_color=constants.COLORS.get("primary"),
            scrollbar_button_hover_color=constants.COLORS.get("primary_hover"),
        )
        textbox.pack(fill="both", expand=True)
        textbox.configure(state="normal")

        # Insert content with colors
        if description:
            textbox.insert("end", description + "\n\n", "desc")

        if self._usage:
            textbox.insert("end", "📌 Uso:\n", "section")
            for item in self._usage:
                textbox.insert("end", f"  • {item}\n", "body")
            textbox.insert("end", "\n")

        if self._tips:
            textbox.insert("end", "💡 Tips:\n", "section")
            for tip in self._tips:
                textbox.insert("end", f"  • {tip}\n", "tip")
            textbox.insert("end", "\n")

        if self._warnings:
            textbox.insert("end", "⚠️ Advertencias:\n", "section")
            for warn in self._warnings:
                textbox.insert("end", f"  • {warn}\n", "warn")

        # Configure tags
        textbox.tag_config("desc", foreground=text_color)
        textbox.tag_config("section", foreground=primary)
        textbox.tag_config("body", foreground=text_secondary)
        textbox.tag_config("tip", foreground=success)
        textbox.tag_config("warn", foreground=warning)

        textbox.configure(state="disabled")

        # Botón cerrar
        close_btn = ctk.CTkButton(
            self.window,
            text="Cerrar",
            command=self.close,
            width=100,
            fg_color=constants.COLORS.get("primary"),
            hover_color=constants.COLORS.get("primary_hover"),
        )
        close_btn.pack(pady=(15, 20))

        # Cerrar con Escape
        self.window.bind("<Escape>", lambda e: self.close())

    def close(self) -> None:
        """Cierra el popup."""
        self.window.grab_release()
        self.window.destroy()


# Botón estático para abrir ayuda
class HelpButton(ctk.CTkButton):
    """Botón que abre un popup de ayuda."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            text="📖 Ayuda",
            command=self._open_help,
            width=80,
            height=28,
            fg_color=constants.COLORS.get("bg_hover", "#3d3d3d"),
            hover_color=constants.COLORS.get("primary", "#3b82f6"),
            text_color=constants.COLORS.get("text_primary", "#e0e0e0"),
            **kwargs
        )
        
        self._parent = parent
        self._title = "Ayuda"
        self._description = ""
        self._usage = []
        self._tips = []
        self._warnings = []
    
    def configure_help(self, title: str = "Ayuda",
                      description: str = "",
                      usage: list = None,
                      tips: list = None,
                      warnings: list = None) -> None:
        """Configura el contenido de la ayuda."""
        self._title = title
        self._description = description
        self._usage = usage or []
        self._tips = tips or []
        self._warnings = warnings or []
    
    def _open_help(self) -> None:
        """Abre el popup de ayuda."""
        HelpPopup(
            self._parent,
            title=self._title,
            description=self._description,
            usage=self._usage,
            tips=self._tips,
            warnings=self._warnings
        )


def add_help(parent, title: str = "Ayuda",
             description: str = "",
             usage: list = None,
             tips: list = None,
             warnings: list = None):
    """
    Helper para agregar un botón de ayuda que abre un popup.
    
    Args:
        parent: Frame padre
        title: Título del popup
        description: Descripción breve
        usage: Lista de pasos de uso
        tips: Lista de tips
        warnings: Lista de advertencias
    
    Returns:
        HelpButton instance (configurable)
    """
    btn = HelpButton(parent)
    btn.configure_help(
        title=title,
        description=description,
        usage=usage,
        tips=tips,
        warnings=warnings
    )
    return btn