"""
HelpPanel: Componente reutilizable para mostrar ayuda/descripción en las herramientas.
"""
import customtkinter as ctk


class HelpPanel(ctk.CTkFrame):
    """
    Panelcollapsible de ayuda paramostrar descripción,uso y advertencias.
    
    El contenido se expande/colapsa sin afectar el scroll de la herramienta.
    """
    
    def __init__(self, parent, title: str = "Ayuda", 
                 description: str = "", 
                 usage: list = None,
                 tips: list = None,
                 warnings: list = None,
                 **kwargs):
        super().__init__(parent, **kwargs)
        
        self._usage = usage or []
        self._tips = tips or []
        self._warnings = warnings or []
        
        # Frame del título (clickeable)
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=5, pady=2)
        
        self.toggle_btn = ctk.CTkButton(
            self.header_frame,
            text="📖 Ayuda",
            command=self._toggle,
            width=80,
            height=28,
            fg_color="gray",
            hover_color="darkgray"
        )
        self.toggle_btn.pack(side="left")
        
        # Frame del contenido (expandible) - sin scroll
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        # Initially hidden
        self._is_expanded = False
        
        # Contenido - todos los textos con wraplength para que no salgan de la pantalla
        if description:
            desc_label = ctk.CTkLabel(
                self.content_frame,
                text=description,
                font=ctk.CTkFont(size=14),
                justify="left",
                anchor="w",
                wraplength=550  # Ancho máximo antes de salto
            )
            desc_label.pack(anchor="w", padx=10, pady=(5, 2), fill="x")
        
        if self._usage:
            ctk.CTkLabel(
                self.content_frame,
                text="📌 Uso:",
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(anchor="w", padx=10, pady=(5, 0))
            
            for item in self._usage:
                item_label = ctk.CTkLabel(
                    self.content_frame,
                    text=f"• {item}",
                    font=ctk.CTkFont(size=14),
                    text_color="gray",
                    justify="left",
                    anchor="w",
                    wraplength=500
                )
                item_label.pack(anchor="w", padx=20, pady=1, fill="x")
        
        if self._tips:
            ctk.CTkLabel(
                self.content_frame,
                text="💡 Tips:",
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(anchor="w", padx=10, pady=(10, 0))
            
            for tip in self._tips:
                tip_label = ctk.CTkLabel(
                    self.content_frame,
                    text=f"• {tip}",
                    font=ctk.CTkFont(size=14),
                    text_color="green",
                    justify="left",
                    anchor="w",
                    wraplength=500
                )
                tip_label.pack(anchor="w", padx=20, pady=1, fill="x")
        
        if self._warnings:
            ctk.CTkLabel(
                self.content_frame,
                text="⚠️ Advertencias:",
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(anchor="w", padx=10, pady=(10, 0))
            
            for warn in self._warnings:
                warn_label = ctk.CTkLabel(
                    self.content_frame,
                    text=f"• {warn}",
                    font=ctk.CTkFont(size=14),
                    text_color="orange",
                    justify="left",
                    anchor="w",
                    wraplength=500
                )
                warn_label.pack(anchor="w", padx=20, pady=1, fill="x")
    
    def _toggle(self) -> None:
        """Expande/colapsa el contenido."""
        if self._is_expanded:
            self.content_frame.pack_forget()
            self.toggle_btn.configure(text="📖 Ayuda")
        else:
            self.content_frame.pack(fill="x", padx=5, pady=2)
            self.toggle_btn.configure(text="🔼 Ocultar")
        
        self._is_expanded = not self._is_expanded


def add_help(parent, title: str = "Ayuda",
             description: str = "",
             usage: list = None,
             tips: list = None,
             warnings: list = None) -> HelpPanel:
    """
    Helper para agregar un panel de ayuda fácilmente.
    El texto se muestra con wrap para evitar que salga de la pantalla.
    
    Args:
        parent: Frame padre
        title: Título del panel  
        description: Descripción breve
        usage: Lista de pasos de uso
        tips: Lista de tips
        warnings: Lista de advertencias
    
    Returns:
        HelpPanel instance
    """
    return HelpPanel(
        parent,
        title=title,
        description=description,
        usage=usage,
        tips=tips,
        warnings=warnings,
        fg_color="transparent"
    )