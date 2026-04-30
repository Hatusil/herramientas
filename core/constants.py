"""
Constantes y configuración del proyecto.
"""
from pathlib import Path
import customtkinter as ctk

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

# Paleta de colores profesional
COLORS = {
    # Fondos
    "bg_dark": "#1a1a1a",
    "bg_medium": "#252525",
    "bg_light": "#2d2d2d",
    "bg_hover": "#3d3d3d",
    
    # Sidebar
    "sidebar_bg": "#1e1e1e",
    "sidebar_hover": "#2a2a2a",
    
    # Acentos
    "primary": "#0d47a0",      # Azul oscuro
    "primary_hover": "#1565c0",
    "primary_light": "#1976d2",
    
    # Estados
    "success": "#2e7d32",     # Verde
    "error": "#c62828",        # Rojo
    "warning": "#f9a825",     # Amarillo
    "info": "#0277d2",       # Info
    
    # Texto
    "text_primary": "#ffffff",
    "text_secondary": "#b0b0b0",
    "text_muted": "#707070",
    
    # Bordes
    "border": "#404040",
    "border_light": "#505050",
}

# Aplicar tema oscuro
ctk.set_appearance_mode("dark")
APPEARANCE_MODE = "dark"

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
FONT_FAMILY = "Segoe UI"
FONT_SIZE_SMALL = 14    # Antes 12
FONT_SIZE_NORMAL = 16    # Antes 14
FONT_SIZE_LARGE = 18    # Antes 16
FONT_SIZE_TITLE = 24    # Antes 20

def font(size: str = "normal", weight: str = "normal") -> ctk.CTkFont:
    """Retorna font con el tamaño especificado.
    
    Args:
        size: Tamaño de fuente (small, normal, large, title)
        weight: Peso de fuente (normal, bold)
        
    Returns:
        CTkFont configurado
    """
    from customtkinter import CTkFont
    sizes = {
        "small": FONT_SIZE_SMALL,
        "normal": FONT_SIZE_NORMAL,
        "large": FONT_SIZE_LARGE,
        "title": FONT_SIZE_TITLE,
    }
    return CTkFont(size=sizes.get(size, FONT_SIZE_NORMAL), weight=weight)