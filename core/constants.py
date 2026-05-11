"""
Constantes y configuración del proyecto.
Cumple con máxima A1 (una sola responsabilidad).
"""
import platform
from pathlib import Path

# Re-exportar theme system para compatibilidad
from core.theme import (
    get_theme,
    set_theme,
    apply_theme_to_widget,
    THEMES,
    COLORS,
    CURRENT_THEME,
    APPEARANCE_MODE,
    init_theme,
)

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

# ============ APP CONFIG ============
APP_NAME = "Herramientas"
APP_WIDTH = 1100
APP_HEIGHT = 700
SIDEBAR_WIDTH = 240

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


# Nota: init_theme() NO se llama aquí para evitar side effects durante el import.
# El theme se inicializa desde app.py o el punto de entrada de la UI.

__all__ = [
    # Theme (re-exportado)
    'get_theme',
    'set_theme',
    'apply_theme_to_widget',
    'THEMES',
    'COLORS',
    'CURRENT_THEME',
    'APPEARANCE_MODE',
    'init_theme',
    # Constantes reales
    'PROJECT_ROOT',
    'CORE_DIR',
    'UI_DIR',
    'TOOLS_DIR',
    'OUTPUT_DIR',
    'APP_NAME',
    'APP_WIDTH',
    'APP_HEIGHT',
    'SIDEBAR_WIDTH',
    'DEFAULT_LUFS',
    'LRA',
    'TP',
    'TOOL_STATUS_OK',
    'TOOL_STATUS_ERROR',
    'TOOL_STATUS_LOADING',
    'FONT_FAMILY',
    'FONT_SIZE_SMALL',
    'FONT_SIZE_NORMAL',
    'FONT_SIZE_LARGE',
    'FONT_SIZE_TITLE',
    'font',
    'CTK_AVAILABLE',
]