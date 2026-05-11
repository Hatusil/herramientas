"""
HelpPanel: Componente reutilizable para mostrar ayuda/descripción en las herramientas.
Muestra la ayuda como un popup flotante (CTkToplevel) que no desplaza el contenido.
"""
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
        
        # Bloquear scroll propagation a la ventana de atrás
        # grab_set() no siempre captura mousewheel, hay que cortarlo explícitamente
        self._block_scroll(self.window)
        
        # Frame principal - usar colores del tema
        main_frame = ctk.CTkFrame(
            self.window,
            fg_color=constants.COLORS.get("bg_dark", "#1a1a1a")
        )
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        self._block_scroll(main_frame)
        
        # Usar CTkScrollableFrame que maneja el scroll correctamente
        scrollable = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=constants.COLORS.get("bg_dark", "#1a1a1a"),
            label_text="",
            label_fg_color=constants.COLORS.get("bg_dark", "#1a1a1a")
        )
        scrollable.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Contenido con wraplength - colores del tema
        if description:
            desc_label = ctk.CTkLabel(
                scrollable,
                text=description,
                font=font("small"),
                justify="left",
                anchor="w",
                wraplength=450,
                text_color=constants.COLORS.get("text_primary", "#e0e0e0")
            )
            desc_label.pack(anchor="w", padx=10, pady=(5, 10), fill="x")
        
        if self._usage:
            ctk.CTkLabel(
                scrollable,
                text="📌 Uso:",
                font=font("small", "bold"),
                text_color=constants.COLORS.get("primary", "#3b82f6")
            ).pack(anchor="w", padx=10, pady=(10, 0))
            
            for item in self._usage:
                ctk.CTkLabel(
                    scrollable,
                    text=f"• {item}",
                    font=font("small"),
                    text_color=constants.COLORS.get("text_secondary", "#9ca3af"),
                    justify="left",
                    anchor="w",
                    wraplength=420
                ).pack(anchor="w", padx=20, pady=1, fill="x")
        
        if self._tips:
            ctk.CTkLabel(
                scrollable,
                text="💡 Tips:",
                font=font("small", "bold"),
                text_color=constants.COLORS.get("primary", "#3b82f6")
            ).pack(anchor="w", padx=10, pady=(15, 0))
            
            for tip in self._tips:
                ctk.CTkLabel(
                    scrollable,
                    text=f"• {tip}",
                    font=font("small"),
                    text_color=constants.COLORS.get("success", "#22c55e"),
                    justify="left",
                    anchor="w",
                    wraplength=420
                ).pack(anchor="w", padx=20, pady=1, fill="x")
        
        if self._warnings:
            ctk.CTkLabel(
                scrollable,
                text="⚠️ Advertencias:",
                font=font("small", "bold"),
                text_color=constants.COLORS.get("primary", "#3b82f6")
            ).pack(anchor="w", padx=10, pady=(15, 0))
            
            for warn in self._warnings:
                ctk.CTkLabel(
                    scrollable,
                    text=f"• {warn}",
                    font=font("small"),
                    text_color=constants.COLORS.get("warning", "#f59e0b"),
                    justify="left",
                    anchor="w",
                    wraplength=420
                ).pack(anchor="w", padx=20, pady=1, fill="x")
        
        # Botón cerrar - con margen
        close_btn = ctk.CTkButton(
            self.window,
            text="Cerrar",
            command=self.close,
            width=100,
            fg_color=constants.COLORS.get("primary", "#3b82f6"),
            hover_color=constants.COLORS.get("primary_hover", "#2563eb")
        )
        close_btn.pack(pady=(15, 20))
        
        # Cerrar con Escape
        self.window.bind("<Escape>", lambda e: self.close())
    
    def _block_scroll(self, widget):
        """Bloquea scroll propagation a ventanas padre.
        
        grab_set() no siempre captura mousewheel events, así que
        matamos la propagación explícitamente en la ventana y frames
        contenedores. El CTkScrollableFrame interno sigue funcionando.
        """
        widget.bind("<MouseWheel>", lambda e: "break", add="+")
        widget.bind("<Button-4>", lambda e: "break", add="+")
        widget.bind("<Button-5>", lambda e: "break", add="+")
    
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