"""
Aplicación principal con CustomTkinter.
Dashboard unificado para navegar entre herramientas.
"""
import logging
from typing import Any
import customtkinter as ctk
from pathlib import Path

from core import constants
from core.constants import font, TOOL_ICONS, TOOL_DESCRIPTIONS
from core import config
from core.plugin_manager import PluginManager
from ui.sidebar import Sidebar
from ui.status_bar import StatusBar
from ui.welcome_screen import create_welcome_screen
from ui.scroll_utils import setup_scrollable_frame


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class App(ctk.CTk):
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        super().__init__()
        
        # ============ INICIALIZAR TEMA ============
        # Cargar tema desde config y aplicar
        saved_theme = config.load_theme()
        constants.set_theme(saved_theme)
        
        # Configuración de ventana
        self.title(constants.APP_NAME)
        self.geometry(f"{constants.APP_WIDTH}x{constants.APP_HEIGHT}")
        self.minsize(800, 500)
        
        # Centrar ventana en pantalla
        self._center_window()
        
        # Estilo de ventana - usar color del tema actual
        self.configure(fg_color=constants.COLORS["bg_dark"])
        
        # Permitir maximizar
        self.resizable(True, True)
        
        # Bind para manejar resize
        self.bind("<Configure>", self._on_resize)
        
        # Inicializar plugin manager
        self.plugin_manager = PluginManager()
        
        # UI
        self.sidebar = None
        self.content_frame = None
        self.status_bar = None
        self.current_tool = None
        
        self._setup_ui()
        self._setup_status_bar()
        self._load_tools()
        
        # Protocolo para cerrar con X
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _center_window(self) -> None:
        """Centra la ventana en la pantalla."""
        self.update_idletasks()
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        window_width = constants.APP_WIDTH
        window_height = constants.APP_HEIGHT
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2 - 30  # Un poco más arriba
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def _on_resize(self, event: Any) -> None:
        """Maneja cuando se redimensiona la ventana."""
        # Actualizar el sidebar width según alto de ventana
        pass  # Por ahora solo mantener
    
    def _on_closing(self) -> None:
        """Cierra la app cuando se presiona X o Salir."""
        # Bug conocido de CustomTkinter CTkButton con _font attribute
        # Usar try/except directo para evitar múltiples warnings
        try:
            self.destroy()
        except (AttributeError, RuntimeError):
            # RuntimeError puede ocurrir si el widget ya fue destruido
            # Bug conocido de CustomTkinter CTkButton - forzar salida
            import sys
            sys.exit(0)
    
    def refresh_theme(self) -> None:
        """Actualiza todos los widgets cuando cambia el tema."""
        # Actualizar ventana principal
        self.configure(fg_color=constants.COLORS.get("bg_dark"))

        # Actualizar content frame
        if self.content_frame:
            self.content_frame.configure(fg_color=constants.COLORS.get("bg_medium"))

        # NO recorrer recursivamente — rompe estilos específicos de widgets hijos
        # Solo actualizar sidebar (maneja sus propios estilos internamente)

        # Actualizar sidebar
        if self.sidebar:
            tools = self.plugin_manager.get_tools_list()
            self.sidebar.set_tools(tools)
            if hasattr(self.sidebar, 'update_theme'):
                self.sidebar.update_theme()

        # Recargar pantalla actual si hay una tool activa
        if self.current_tool:
            tool = self.plugin_manager.get_tools().get(self.current_tool)
            if tool:
                self._on_tool_selected(self.current_tool)
        else:
            # Recargar pantalla de bienvenida - limpiar todo antes
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            self.content_frame.configure(fg_color=constants.COLORS.get("bg_medium"))
            self.update()
            tools = self.plugin_manager.get_tools_list()
            self._show_welcome_screen(tools)
    
    def _setup_ui(self) -> None:
        """Configura la interfaz de usuario."""
        # Grid layout: sidebar + content + status
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        
        # Sidebar
        self.sidebar = Sidebar(self, self._on_tool_selected)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.grid_columnconfigure(0, weight=0)  # Sidebar fijo
        self.grid_columnconfigure(1, weight=1)   # Content expandible
        
        # Content area (scrollable)
        self.content_frame = ctk.CTkScrollableFrame(
            self,
            label_text="",
            fg_color=constants.COLORS["bg_medium"]
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Setup scroll binding
        self._setup_scroll()
    
    def _setup_scroll(self) -> None:
        """Configura scroll con mouse wheel de forma independiente."""
        setup_scrollable_frame(self.content_frame)
    
    def _on_wheel(self, event) -> str:
        """Handler legacy - ya no se usa, reemplazado por scroll_utils."""
        return "break"
    
    def _setup_status_bar(self) -> None:
        """Crea el status bar."""
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
    
    def _load_tools(self) -> None:
        """Carga las herramientas disponibles."""
        logger.info("Descubriendo herramientas...")
        self.plugin_manager.discover_tools()
        
        # Actualizar sidebar con tools encontradas
        tools = self.plugin_manager.get_tools_list()
        self.sidebar.set_tools(tools)
        
        # Actualizar status bar
        for tool in tools:
            self.status_bar.set_tool_status(
                tool['name'], 
                tool['status']
            )
        
        # Mostrar pantalla de bienvenida en lugar de auto-seleccionar
        if tools:
            self._show_welcome_screen(tools)
        
        logger.info(f"Cargadas {len(tools)} herramientas")
    
    def _show_welcome_screen(self, tools: list) -> None:
        """Muestra pantalla de bienvenida con todas las herramientas."""
        # Limpiar content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Usar módulo separado (welcome_screen.py) - pasar tools ya cargadas
        create_welcome_screen(self.content_frame, tools, self._on_tool_selected)
    
    def _on_tool_selected(self, tool_name: str) -> None:
        """
        Maneja la selección de una herramienta.
        
        Args:
            tool_name: Nombre de la tool seleccionada
        """
        # Caso especial: volver a pantalla de bienvenida
        if tool_name == "__welcome__":
            self.sidebar._highlight_tool(None)
            tools = self.plugin_manager.get_tools_list()
            self._show_welcome_screen(tools)
            self.current_tool = None
            return
        
        if tool_name == self.current_tool:
            return
        
        self.current_tool = tool_name
        tool = self.plugin_manager.get_tools().get(tool_name)
        
        if tool is None:
            logger.warning(f"Tool no encontrada: {tool_name}")
            return
        
        # Actualizar highlight en sidebar
        self.sidebar._highlight_tool(tool_name)
        
        # Destruir y recrear content frame completamente
        self._rebuild_content_frame()
        
        # Construir UI de la tool
        try:
            tool.build_ui(self.content_frame)
        except Exception as e:
            logger.error(f"Error construyendo UI de {tool_name}: {e}")
    
    def _clear_content_frame(self) -> None:
        """Limpia los hijos del content frame para CTkScrollableFrame."""
        import logging
        logger = logging.getLogger(__name__)
        
        def clean_all_children(widget):
            """Limpia todos los descendientes de un widget."""
            try:
                children = widget.winfo_children()
                for child in children:
                    clean_all_children(child)
                    try:
                        child.destroy()
                    except Exception:
                        pass
            except Exception:
                pass
        
        try:
            # Buscar cualquier atributo que parezca un frame interno
            for attr_name in dir(self.content_frame):
                if 'interior' in attr_name.lower() or attr_name == 'frame':
                    try:
                        inner = getattr(self.content_frame, attr_name, None)
                        if inner and hasattr(inner, 'winfo_children'):
                            clean_all_children(inner)
                            logger.info(f"Limpio {attr_name}")
                    except Exception:
                        pass
            
            # También limpiar hijos directos
            clean_all_children(self.content_frame)
                
        except Exception as e:
            logger.warning(f"Error limpiar content frame: {e}")
    
    def _rebuild_content_frame(self) -> None:
        """Destruye y recreate el content frame para evitar problemas de limpieza."""
        try:
            # Destruir el content_frame existente
            self.content_frame.destroy()
        except Exception:
            pass
        
        # Recrear el content frame
        self.content_frame = ctk.CTkScrollableFrame(
            self,
            label_text="",
            fg_color=constants.COLORS["bg_medium"]
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Setup scroll binding
        self._setup_scroll()
    
    def _on_content_wheel(self, event, canvas) -> None:
        """Maneja scroll en content - ahora sin usar canvas."""
        pass  # Deprecated


def main():
    """Punto de entrada de la aplicación."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()