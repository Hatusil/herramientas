"""
HelpPanel: Componente reutilizable para mostrar ayuda/descripción en las herramientas.
Muestra la ayuda como un popup flotante (CTkToplevel) que no desplaza el contenido.
"""
import customtkinter as ctk


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
        
        # Centrar respecto al padre
        self.window.transient(parent)
        parent.update_idletasks()
        
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        
        win_w = 500
        win_h = 450
        
        x = parent_x + (parent_w - win_w) // 2
        y = parent_y + (parent_h - win_h) // 2
        
        self.window.geometry(f"+{x}+{y}")
        
        # Bloquear interacción con la ventana padre
        self.window.grab_set()
        
        # Frame principal - fondo oscuro
        main_frame = ctk.CTkFrame(self.window, fg_color="#1a1a1a")
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Usar CTkScrollableFrame que maneja el scroll correctamente
        scrollable = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="#1a1a1a",
            label_text="",
            label_fg_color="#1a1a1a"
        )
        scrollable.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Contenido con wraplength - colores contrasts
        if description:
            desc_label = ctk.CTkLabel(
                scrollable,
                text=description,
                font=ctk.CTkFont(size=14),
                justify="left",
                anchor="w",
                wraplength=450,
                text_color="white"
            )
            desc_label.pack(anchor="w", padx=10, pady=(5, 10), fill="x")
        
        if self._usage:
            ctk.CTkLabel(
                scrollable,
                text="📌 Uso:",
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color="#4A90D9"
            ).pack(anchor="w", padx=10, pady=(10, 0))
            
            for item in self._usage:
                ctk.CTkLabel(
                    scrollable,
                    text=f"• {item}",
                    font=ctk.CTkFont(size=14),
                    text_color="#BBBBBB",
                    justify="left",
                    anchor="w",
                    wraplength=420
                ).pack(anchor="w", padx=20, pady=1, fill="x")
        
        if self._tips:
            ctk.CTkLabel(
                scrollable,
                text="💡 Tips:",
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color="#4A90D9"
            ).pack(anchor="w", padx=10, pady=(15, 0))
            
            for tip in self._tips:
                ctk.CTkLabel(
                    scrollable,
                    text=f"• {tip}",
                    font=ctk.CTkFont(size=14),
                    text_color="#7CFC00",
                    justify="left",
                    anchor="w",
                    wraplength=420
                ).pack(anchor="w", padx=20, pady=1, fill="x")
        
        if self._warnings:
            ctk.CTkLabel(
                scrollable,
                text="⚠️ Advertencias:",
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color="#4A90D9"
            ).pack(anchor="w", padx=10, pady=(15, 0))
            
            for warn in self._warnings:
                ctk.CTkLabel(
                    scrollable,
                    text=f"• {warn}",
                    font=ctk.CTkFont(size=14),
                    text_color="#FFA500",
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
            fg_color="#4A90D9",
            hover_color="#6BA8E0"
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
            fg_color="gray",
            hover_color="darkgray",
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