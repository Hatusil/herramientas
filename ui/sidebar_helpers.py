"""
Helper functions para Sidebar.
Cumple máxima A1 (una responsabilidad).
"""
import sys
from pathlib import Path
from typing import Callable, Optional

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