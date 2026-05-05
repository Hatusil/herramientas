"""
Constantes y configuración del proyecto.
"""
import platform
from pathlib import Path

try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
except ImportError:
    CTK_AVAILABLE = False
    ctk = None

# Raíz del proyecto (parent de core/)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Directorios
CORE_DIR = PROJECT_ROOT / "core"
UI_DIR = PROJECT_ROOT / "ui"
TOOLS_DIR = PROJECT_ROOT / "tools"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Crear directorios si no existen
OUTPUT_DIR.mkdir(exist_ok=True)

# ============ TEMA PROFESIONAL MODERNO ============
APP_NAME = "Herramientas"
APP_WIDTH = 1100
APP_HEIGHT = 700
SIDEBAR_WIDTH = 240

# ============ SISTEMA DE TEMAS ============
# Paletas de colores para tema oscuro y claro
THEMES = {
    "dark": {
        # Fondos
        "bg_dark": "#1a1a1a",      # Fondo app
        "bg_medium": "#252525",
        "bg_light": "#2d2d2d",     # Fondo panel
        "bg_hover": "#3d3d3d",    # Fondo input
        "bg_input": "#3d3d3d",
        
        # Sidebar
        "sidebar_bg": "#1e1e1e",
        "sidebar_hover": "#2a2a2a",
        
        # Acentos
        "primary": "#3b82f6",      # Azul acento
        "primary_hover": "#2563eb",
        "primary_light": "#1976d2",
        
        # Estados
        "success": "#22c55e",      # Verde éxito
        "error": "#ef4444",       # Rojo error
        "warning": "#f59e0b",     # Amarillo warning
        "info": "#0277d2",
        
        # Texto
        "text_primary": "#e0e0e0", # Texto primario
        "text_secondary": "#9ca3af", # Texto secundario
        "text_muted": "#707070",
        
        # Bordes
        "border": "#404040",
        "border_light": "#505050",
        
        # UI Elements
        "button_fg": "#3d3d3d",        # Gris oscuro
        "button_hover": "#525252",     # Gris más claro
    },
    "light": {
        # Fondos
        "bg_dark": "#f5f5f5",     # Fondo app
        "bg_medium": "#ebebeb",
        "bg_light": "#ffffff",     # Fondo panel
        "bg_hover": "#e8e8e8",    # Fondo input
        "bg_input": "#e8e8e8",
        
        # Sidebar
        "sidebar_bg": "#fafafa",
        "sidebar_hover": "#f0f0f0",
        
        # Acentos
        "primary": "#2563eb",      # Azul acento (más oscuro para contrastar)
        "primary_hover": "#1d4ed8",
        "primary_light": "#3b82f6",
        
        # Estados
        "success": "#16a34a",      # Verde éxito
        "error": "#dc2626",       # Rojo error
        "warning": "#d97706",     # Amarillo warning
        "info": "#0284c7",
        
        # Texto
        "text_primary": "#1f1f1f", # Texto primario
        "text_secondary": "#6b7280", # Texto secundario
        "text_muted": "#9ca3af",
        
        # Bordes
        "border": "#d1d5db",
        "border_light": "#e5e7eb",
        
        # UI Elements
        "button_fg": "#4b5563",       # Gris neutro profesional
        "button_hover": "#374151",    # Gris más oscuro
    }
}

# Variable global para tema activo (apunta al diccionario de temas)
COLORS = THEMES["dark"].copy()
CURRENT_THEME = "dark"
APPEARANCE_MODE = "dark"


def get_theme() -> str:
    """
    Retorna el tema actual.
    
    Returns:
        Tema actual ('dark' o 'light')
    """
    return CURRENT_THEME


def set_theme(theme: str) -> None:
    """
    Establece el tema y actualiza COLORS.
    
    Args:
        theme: Tema a establecer ('dark' o 'light')
    """
    global COLORS, CURRENT_THEME, APPEARANCE_MODE
    
    if theme not in ("dark", "light"):
        theme = "dark"
    
    # Actualizar COLORS con la paleta del tema
    COLORS = THEMES[theme].copy()
    CURRENT_THEME = theme
    APPEARANCE_MODE = theme
    
    # Aplicar modo nativo de CustomTkinter
    ctk.set_appearance_mode(theme)


def apply_theme_to_widget(widget) -> None:
    """
    Aplica los colores del tema actual a un widget.
    Soporta CTkFrame, CTkButton, CTkLabel, CTkEntry, CTkTextbox, CTkScrollableFrame.
    
    Args:
        widget: Widget de CustomTkinter a configurar
    """
    widget_type = type(widget).__name__
    
    if widget_type in ("CTkFrame", "CTkScrollableFrame"):
        widget.configure(fg_color=COLORS["bg_light"])
    elif widget_type == "CTkButton":
        widget.configure(fg_color=COLORS.get("button_fg", COLORS["bg_light"]))
    elif widget_type == "CTkLabel":
        widget.configure(text_color=COLORS["text_primary"])
    elif widget_type == "CTkEntry":
        widget.configure(fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"])
    elif widget_type == "CTkTextbox":
        widget.configure(fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"])
    # Para otros widgets, no hacer nada especial


# Inicializar con tema oscuro por defecto (solo si CTK disponible)
if CTK_AVAILABLE:
    set_theme("dark")
    try:
        ctk.set_default_color_theme("dark-blue")
    except Exception:
        pass  # Theme puede no estar disponible en algunos entornos

# Configuración de Audio
DEFAULT_LUFS = -16  # EBU R128 target loudness
LRA = 11       # Loudness Range
TP = -1         # True Peak

# Estados de Tools
TOOL_STATUS_OK = "OK"
TOOL_STATUS_ERROR = "ERROR"
TOOL_STATUS_LOADING = "LOADING"

# Configuración de fuentes - optimizadas para mejor legibilidad
# Cross-platform: Segoe UI en Windows, DejaVu Sans en Linux
if platform.system() == "Windows":
    FONT_FAMILY = "Segoe UI"
else:
    FONT_FAMILY = "DejaVu Sans"
    
FONT_SIZE_SMALL = 14    # Antes 12
FONT_SIZE_NORMAL = 16    # Antes 14
FONT_SIZE_LARGE = 18    # Antes 16
FONT_SIZE_TITLE = 24    # Antes 20

def font(size: str = "normal", weight: str = "normal"):
    """Retorna font con el tamaño especificado.
    
    Args:
        size: Tamaño de fuente (small, normal, large, title)
        weight: Peso de fuente (normal, bold)
        
    Returns:
        CTkFont configurado (o None si CTK no disponible)
    """
    if not CTK_AVAILABLE:
        return None
    from customtkinter import CTkFont
    sizes = {
        "small": FONT_SIZE_SMALL,
        "normal": FONT_SIZE_NORMAL,
        "large": FONT_SIZE_LARGE,
        "title": FONT_SIZE_TITLE,
    }
    return CTkFont(size=sizes.get(size, FONT_SIZE_NORMAL), weight=weight)