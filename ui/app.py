"""
Aplicación principal con CustomTkinter.
Dashboard unificado para navegar entre herramientas.
"""
import sys
import logging
import customtkinter as ctk
from pathlib import Path

# Agregar project root al path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import constants
from core.plugin_manager import PluginManager
from ui.sidebar import Sidebar
from ui.status_bar import StatusBar


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
        
        # Configuración de ventana
        self.title(constants.APP_NAME)
        self.geometry(f"{constants.APP_WIDTH}x{constants.APP_HEIGHT}")
        self.minsize(800, 500)
        
        # Estilo de ventana
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
    
    def _on_resize(self, event) -> None:
        """Maneja cuando se redimensiona la ventana."""
        # Actualizar el sidebar width según alto de ventana
        pass  # Por ahora solo mantener
    
    def _on_closing(self) -> None:
        """Cierra la app cuando se presiona X o Salir."""
        # Usar destroy() normal, pero capturar excepciones del bug de CTkButton
        try:
            self.quit()
            self.destroy()
        except AttributeError:
            # Bug conocido de CustomTkinter CTkButton - forzar salida
            import sys
            sys.exit(0)
    
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
        """Configura scroll con mouse wheel."""
        # Binding directo al widget
        try:
            self.content_frame.bind("<MouseWheel>", self._on_wheel)
            self.content_frame.bind("<Button-4>", self._on_wheel)
            self.content_frame.bind("<Button-5>", self._on_wheel)
        except Exception:
            pass
    
    def _on_wheel(self, event) -> str:
        """Maneja scroll con la rueda del mouse."""
        try:
            canvas = getattr(self.content_frame, '_parent_canvas', None)
            if canvas:
                if hasattr(event, 'delta'):
                    direction = -1 if event.delta < 0 else 1
                else:
                    direction = -1 if event.num == 4 else 1
                # Scroll más rápido (3 líneas)
                for _ in range(3):
                    canvas.yview("scroll", direction, "units")
        except Exception:
            pass
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
        
        # Seleccionar primera tool si hay alguna
        if tools:
            self._on_tool_selected(tools[0]['name'])
        
        logger.info(f"Cargadas {len(tools)} herramientas")
    
    def _on_tool_selected(self, tool_name: str) -> None:
        """
        Maneja la selección de una herramienta.
        
        Args:
            tool_name: Nombre de la tool seleccionada
        """
        if tool_name == self.current_tool:
            return
        
        self.current_tool = tool_name
        tool = self.plugin_manager.get_tools().get(tool_name)
        
        if tool is None:
            logger.warning(f"Tool no encontrada: {tool_name}")
            return
        
        # Actualizar highlight en sidebar
        self.sidebar._highlight_tool(tool_name)
        
        # Limpiar content frame - usar pack_forget primero para evitar bug de CTkButton
        for widget in self.content_frame.winfo_children():
            try:
                widget.pack_forget()
            except Exception as e:
                logger.warning(f"Error in pack_forget: {e}")
            try:
                widget.grid_forget()
            except Exception as e:
                logger.warning(f"Error in grid_forget: {e}")
            try:
                widget.destroy()
            except Exception as e:
                logger.warning(f"Error en destroy (CTkButton bug): {e}")
        
        # Construir UI de la tool
        try:
            tool.build_ui(self.content_frame)
        except Exception as e:
            logger.error(f"Error construyendo UI de {tool_name}: {e}")
    
    def _on_content_wheel(self, event, canvas) -> None:
        """Maneja scroll en content - ahora sin usar canvas."""
        pass  # Deprecated


def main():
    """Punto de entrada de la aplicación."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()