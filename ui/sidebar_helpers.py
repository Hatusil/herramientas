"""
Helper functions para Sidebar.
Cumple máxima A1 (una responsabilidad).
"""
import sys
from pathlib import Path
from typing import Callable, Optional, Dict, Any, List
import customtkinter as ctk
from core import constants

# Check for PIL availability
try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None
    ImageDraw = None


def create_tool_callback(tool_name: str, callback: Callable[[str], None]) -> Callable[[], None]:
    """Crea un callback que captura el nombre de la herramienta."""
    return lambda: callback(tool_name)


def make_circle_image(image_path: str, size: int = 80):
    """Convierte una imagen a círculo con fondo transparente."""
    if not PIL_AVAILABLE or Image is None or ImageDraw is None:
        raise ImportError("PIL (Pillow) is not available")
    
    img = Image.open(image_path).convert("RGBA")
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    
    output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    output.paste(img, (0, 0), mask)
    
    return output


def find_logo_path() -> Optional[str]:
    """Busca el logo en varias ubicaciones posibles (PyInstaller compatible)."""
    base_paths = [
        Path(__file__).parent.parent / "assets",
        Path(__file__).parent.parent / "ui" / "assets",
        Path.cwd() / "assets",
    ]
    
    # PyInstaller compatibility
    if hasattr(sys, '_MEIPASS'):
        base_paths.insert(0, Path(sys._MEIPASS))
    base_paths.insert(0, Path(sys.executable).parent)
    
    possible_names = ["logo.png", "logo.jpg", "icon.png", "app.png"]
    
    for base in base_paths:
        if not base.exists():
            continue
        for name in possible_names:
            logo_path = base / name
            if logo_path.exists():
                return str(logo_path)
    
    return None


def create_tool_button(parent, tool: Dict[str, Any], callback: Callable) -> ctk.CTkButton:
    """Crea un botón de herramienta con estilo estándar."""
    from core.constants import font
    
    btn = ctk.CTkButton(
        parent,
        text=f"{tool.get('icon', '🔧')} {tool.get('display_name', tool['name'])}",
        font=font("normal"),
        fg_color=constants.COLORS.get("bg_light", "#2d2d2d"),
        hover_color=constants.COLORS.get("primary", "#3b82f6"),
        text_color=constants.COLORS.get("text_secondary", "#9ca3af"),
        height=40,
        command=callback
    )
    return btn


def update_tool_buttons(tool_buttons: Dict[str, ctk.CTkButton], selected_tool: Optional[str]) -> None:
    """Actualiza el estado visual de los botones de herramientas."""
    for name, btn in tool_buttons.items():
        try:
            selected_color = constants.COLORS["primary"]
            normal_color = constants.COLORS["bg_light"]
            if name == selected_tool:
                btn.configure(fg_color=selected_color, text_color="white")
            else:
                btn.configure(fg_color=normal_color, text_color=constants.COLORS["text_secondary"])
        except Exception:
            pass