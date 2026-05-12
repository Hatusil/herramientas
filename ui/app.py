"""
Aplicación principal con CustomTkinter.
Dashboard unificado para navegar entre herramientas.
"""
import logging
from typing import Any
import customtkinter as ctk
from pathlib import Path

from core import constants
from core.constants import font
from core import config
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
        self.configure(fg_color=constants.COLORS["bg_dark"])

        # Actualizar content frame
        if self.content_frame:
            self.content_frame.configure(fg_color=constants.COLORS["bg_medium"])

        # Recorrer todos los widgets recursivamente y aplicar tema
        self._apply_theme_recursive(self)

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
            # Recargar pantalla de bienvenida
            tools = self.plugin_manager.get_tools_list()
            self._show_welcome_screen(tools)
    
    def _apply_theme_recursive(self, widget) -> None:
        """Aplica colores del tema actual a widget y sus hijos."""
        try:
            widget_type = type(widget).__name__
            
            if widget_type in ("CTkFrame", "CTkScrollableFrame"):
                widget.configure(fg_color=constants.COLORS.get("bg_light", "#2d2d2d"))
            elif widget_type == "CTkButton":
                widget.configure(
                    fg_color=constants.COLORS.get("button_fg", "#3d3d3d"),
                    hover_color=constants.COLORS.get("button_hover", "#525252"),
                    text_color=constants.COLORS.get("text_primary", "#e0e0e0")
                )
            elif widget_type == "CTkLabel":
                widget.configure(text_color=constants.COLORS.get("text_primary", "#e0e0e0"))
            elif widget_type == "CTkEntry":
                widget.configure(
                    fg_color=constants.COLORS.get("bg_input", "#3d3d3d"),
                    text_color=constants.COLORS.get("text_primary", "#e0e0e0")
                )
            elif widget_type == "CTkSwitch":
                widget.configure(
                    text_color=constants.COLORS.get("text_primary", "#e0e0e0"),
                    fg_color=constants.COLORS.get("bg_hover", "#3d3d3d"),
                    progress_color=constants.COLORS.get("primary", "#3b82f6")
                )
        except Exception:
            pass
        
        # Recursivo para hijos
        try:
            for child in widget.winfo_children():
                self._apply_theme_recursive(child)
        except Exception:
            pass
    
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
            # Intentar obtener canvas de forma robusta para CTkinter 4.x y 5.x
            canvas = None
            
            # Método 1: try attribute directo (CTkinter 4.x)
            canvas = getattr(self.content_frame, '_parent_canvas', None)
            
            # Método 2: buscar en children (CTkinter 5.x compatibility)
            if not canvas:
                for child in self.content_frame.winfo_children():
                    # Buscar canvas con scrollbar
                    if hasattr(child, 'yview'):
                        canvas = child
                        break
            
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
        
        # Mostrar pantalla de bienvenida en lugar de auto-seleccionar
        if tools:
            self._show_welcome_screen(tools)
        
        logger.info(f"Cargadas {len(tools)} herramientas")
    
    def _show_welcome_screen(self, tools: list) -> None:
        """Muestra pantalla de bienvenida con todas las herramientas."""
        # Limpiar content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Crear frame de bienvenida
        welcome_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=constants.COLORS.get("bg_medium", "#252525")
        )
        welcome_frame.pack(fill="both", expand=True)
        
        # Título de bienvenida
        title = ctk.CTkLabel(
            welcome_frame,
            text="🔧 Herramientas",
            font=font("title", "bold"),
            text_color=constants.COLORS.get("text_primary", "#e0e0e0")
        )
        title.pack(pady=(30, 10))
        
        subtitle = ctk.CTkLabel(
            welcome_frame,
            text="Seleccioná una herramienta para comenzar",
            font=font("normal"),
            text_color=constants.COLORS.get("text_secondary", "#9ca3af")
        )
        subtitle.pack(pady=(0, 30))
        
        # Grilla de herramientas
        tools_frame = ctk.CTkFrame(welcome_frame, fg_color="transparent")
        tools_frame.pack(fill="both", expand=True, padx=20)
        
        # Obtener iconos para cada tool
        tool_icons = {
            'text_tool': '📊',
            'duplicate_tool': '📁',
            'hash_tool': '#️⃣',
            'compress_tool': '📦',
            'audio_tool': '🎵',
            'gif_tool': '🎞️',
            'pdf_tool': '📄',
            'video_tool': '🎬',
            'rename_tool': '✏️',
            'search_tool': '🔍',
            'scrubber': '🧹'
        }
        
        tool_descriptions = {
            'text_tool': 'Análisis de texto, WordCloud, estadísticas',
            'duplicate_tool': 'Encuentra y elimina archivos duplicados',
            'hash_tool': 'Calcula hashes MD5/SHA para verificar archivos',
            'compress_tool': 'Comprime archivos y carpetas',
            'audio_tool': 'Procesa y convierte archivos de audio',
            'gif_tool': 'Crea y edita imágenes GIF animadas',
            'pdf_tool': 'Manipula documentos PDF',
            'video_tool': 'Procesa y convierte archivos de video',
            'rename_tool': 'Renombra archivos en lote',
            'search_tool': 'Busca archivos por contenido',
            'scrubber': 'Limpia metadatos de archivos'
        }
        
        # Crear grid de botones (3 columnas)
        for i, tool in enumerate(tools):
            row = i // 3
            col = i % 3
            
            tool_name = tool['name']
            icon = tool_icons.get(tool_name, '🔧')
            description = tool_descriptions.get(tool_name, '')
            
            # Card de tool
            card = ctk.CTkFrame(
                tools_frame,
                fg_color=constants.COLORS.get("bg_light", "#2d2d2d"),
                corner_radius=10
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Configurar grid
            tools_frame.grid_columnconfigure(col, weight=1)
            tools_frame.grid_rowconfigure(row, weight=1)
            
            # Botón con icono
            btn = ctk.CTkButton(
                card,
                text=f"{icon} {tool.get('display_name', tool_name)}",
                font=font("normal", "bold"),
                fg_color=constants.COLORS.get("button_fg", "#3d3d3d"),
                hover_color=constants.COLORS.get("button_hover", "#525252"),
                text_color="white",
                height=50,
                command=lambda t=tool_name: self._on_tool_selected(t)
            )
            btn.pack(fill="x", padx=10, pady=(10, 5))
            
            # Descripción
            if description:
                desc_label = ctk.CTkLabel(
                    card,
                    text=description,
                    font=font("xsmall"),
                    text_color=constants.COLORS.get("text_secondary", "#9ca3af"),
                    wraplength=150
                )
                desc_label.pack(padx=10, pady=(0, 10))
    
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