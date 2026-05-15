"""
Sidebar: Panel lateral de navegación de herramientas.
"""
import logging
import customtkinter as ctk
from typing import List, Dict, Callable, Any
from core import constants
from core.constants import font, FONT_SIZE_TITLE, FONT_SIZE_LARGE
from core import config
from ui.sidebar_helpers import create_tool_callback, make_circle_image, find_logo_path
from ui.sidebar_helpers import create_tool_button, update_tool_buttons, highlight_tool
from ui.sidebar_helpers import create_tool_buttons, update_acerca_button
from ui.sidebar_dialogs import show_acerca_de, show_salir
from ui.sidebar_setup import setup_logo, setup_title, setup_buttons
from ui.theme_factory import (
    create_danger_button, create_secondary_label, create_control_frame,
    create_divider, create_switch
)

logger = logging.getLogger(__name__)


class Sidebar(ctk.CTkFrame):
    """Panel lateral con lista de herramientas."""
    
    def __init__(self, master, on_tool_select: Callable[[str], None], **kwargs):
        super().__init__(master, **kwargs)
        
        self.on_tool_select = on_tool_select
        self.tool_buttons: Dict[str, ctk.CTkButton] = {}
        
        # Usar pack todo
        self.pack_propagate(False)
        
        # Logo y título
        logo_label = setup_logo(self)
        if logo_label:
            logo_label.pack(pady=(5, 0))
            setup_title(self)
        else:
            setup_title(self)
        
        # Botones
        setup_buttons(self, self._on_inicio, self._on_acerca_de)
        
        # Scrollable frame para tools
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="", fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=2, pady=2)
        self._setup_scroll_binding(self.scroll_frame)
        
        # Botón de control (Salir + Theme Switch)
        self.control_frame = create_control_frame(self)
        self.control_frame.pack(fill="x", padx=10, pady=10)
        
        # Título de sección
        config_label = create_secondary_label(
            self.control_frame,
            text="CONFIGURACIÓN",
            font=font("xsmall", "bold")
        )
        config_label.pack(fill="x", padx=12, pady=(10, 8))
        
        # Switch para cambio de tema
        self._theme_var = ctk.StringVar(value=constants.get_theme())
        self.theme_switch = create_switch(
            self.control_frame,
            command=self._on_toggle_theme,
            onvalue="light",
            offvalue="dark",
            variable=self._theme_var
        )
        self.theme_switch.pack(fill="x", padx=12, pady=(0, 8))
        
        # Label que muestra el estado actual
        self._theme_label = create_secondary_label(
            self.control_frame,
            text=f"Modo: {'Claro' if constants.get_theme() == 'light' else 'Oscuro'}",
            font=font("xsmall")
        )
        self._theme_label.pack(fill="x", padx=12, pady=(0, 8))
        
        # Divisor
        divisor = create_divider(self.control_frame)
        divisor.pack(fill="x", padx=12, pady=8)
        
        # Botón Salir
        salir_btn = create_danger_button(
            self.control_frame,
            text="Salir de la Aplicación",
            command=self._on_salir,
            height=36,
            font=font("small", "bold")
        )
        salir_btn.pack(fill="x", padx=12, pady=(8, 12))
    
    def _setup_scroll_binding(self, scroll_frame) -> None:
        """Configura bindings de scroll."""
        from ui.sidebar_helpers import setup_scroll_binding
        setup_scroll_binding(scroll_frame, self._on_mousewheel)
    
    def _on_mousewheel(self, event) -> str:
        """Maneja scroll con mouse wheel."""
        from ui.sidebar_helpers import on_mousewheel
        canvas = None
        if hasattr(self.scroll_frame, '_parent_canvas'):
            canvas = self.scroll_frame._parent_canvas
        if not canvas:
            for child in self.scroll_frame.winfo_children():
                if hasattr(child, 'yview'):
                    canvas = child
                    break
        return on_mousewheel(event, canvas)
    
    def set_tools(self, tools: List[Dict[str, Any]]) -> None:
        """Configura las herramientas a mostrar."""
        for btn in self.tool_buttons.values():
            btn.destroy()
        self.tool_buttons.clear()
        
        self.tool_buttons = create_tool_buttons(self.scroll_frame, tools, self.on_tool_select)
        
        if tools:
            self._highlight_tool(tools[0]['name'])
    
    def update_theme(self) -> None:
        """Actualiza los colores del sidebar cuando cambia el tema."""
        from ui.sidebar_helpers import update_sidebar_theme, update_acerca_button
        update_sidebar_theme(self, self.scroll_frame, self.tool_buttons, getattr(self, '_selected_tool', None))
        update_acerca_button(self, None)
    
    def _highlight_tool(self, tool_name: str = None) -> None:
        """Resalta el botón seleccionado."""
        highlight_tool(self.tool_buttons, tool_name)
    
    def _on_salir(self) -> None:
        """Cierra la aplicación."""
        show_salir(self)
    
    def _on_inicio(self) -> None:
        """Vuelve a la pantalla de bienvenida."""
        # Notificar al app para que muestre la pantalla de inicio
        self.on_tool_select("__welcome__")
    
    def _on_toggle_theme(self) -> None:
        """Cambia entre tema oscuro y claro usando el switch."""
        new_theme = self.theme_switch.get()
        
        # Guardar en config (persistencia)
        config.save_theme(new_theme)
        
        # Actualizar constants
        constants.set_theme(new_theme)
        
        # Actualizar label con el modo actual
        self._theme_label.configure(
            text=f"Modo: {'Claro' if new_theme == 'light' else 'Oscuro'}",
            text_color=constants.COLORS.get("text_secondary", "#9ca3af")
        )
        
        # Notificar a la app principal para que refresque todos los widgets
        if hasattr(self.master, 'refresh_theme'):
            self.master.refresh_theme()
        
        # Forzar redibujado de la ventana
        self.master.update()
        
        logger.info(f"Tema cambiado a: {new_theme}")
    
    def _on_acerca_de(self) -> None:
        """Muestra diálogo Acerca de."""
        show_acerca_de(self)