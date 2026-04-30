"""
StatusBar: Barra de estado profesional.
"""
import customtkinter as ctk
from typing import Dict

from core import constants


class StatusBar(ctk.CTkFrame):
    """Barra inferior profesional."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, height=28, **kwargs)
        
        # Estilo profesional
        self.configure(fg_color=constants.COLORS["bg_medium"])
        
        # Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
# Label de estado
        self.status_label = ctk.CTkLabel(
            self,
            text="Listo",
            anchor="w",
            font=ctk.CTkFont(size=14),
            text_color=constants.COLORS["text_secondary"]
        )
        self.status_label.grid(row=0, column=0, padx=15, pady=0, sticky="w")

        # Indicadores compactos
        self.tool_indicators: Dict[str, ctk.CTkLabel] = {}
    
    def set_tool_status(self, tool_name: str, status: str) -> None:
        """Actualiza el estado de una herramienta."""
        if tool_name not in self.tool_indicators:
            label = ctk.CTkLabel(
                self.tools_frame if hasattr(self, 'tools_frame') else self,
                text=f"{tool_name}",
                font=ctk.CTkFont(size=14),
                anchor="e"
            )
            label.grid(row=0, column=1, padx=(5, 15), pady=0, sticky="e")
            self.tool_indicators[tool_name] = label
        
        label = self.tool_indicators[tool_name]
        label.configure(text=f"{tool_name}")
        
        # Color según estado
        if status == constants.TOOL_STATUS_OK:
            label.configure(text_color=constants.COLORS["success"])
        elif status == constants.TOOL_STATUS_ERROR:
            label.configure(text_color=constants.COLORS["error"])
        else:
            label.configure(text_color=constants.COLORS["warning"])
    
    def set_status(self, message: str) -> None:
        """Establece el mensaje de estado."""
        self.status_label.configure(text=message)