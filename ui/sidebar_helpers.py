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


def update_sidebar_theme(sidebar, scroll_frame, tool_buttons, selected_tool):
    """Actualiza todos los colores del sidebar cuando cambia el tema."""
    # Sidebar principal
    if hasattr(sidebar, 'master'):
        try:
            sidebar.configure(fg_color=constants.COLORS.get("bg_medium", "#252525"))
        except Exception:
            pass
    
    # Scroll frame
    if scroll_frame:
        try:
            scroll_frame.configure(fg_color="transparent")
        except Exception:
            pass
    
    # Tool buttons
    update_tool_buttons(tool_buttons, selected_tool)
    
    # Control frame
    if hasattr(sidebar, 'control_frame'):
        sidebar.control_frame.configure(
            fg_color=constants.COLORS.get("bg_medium", "#252525"),
            border_color=constants.COLORS.get("border", "#404040")
        )
    
    # Theme label
    if hasattr(sidebar, '_theme_label'):
        sidebar._theme_label.configure(
            text=f"Modo: {'Claro' if constants.get_theme() == 'light' else 'Oscuro'}",
            text_color=constants.COLORS.get("text_secondary", "#9ca3af")
        )
    
    # Botón inicio
    if hasattr(sidebar, 'inicio_btn'):
        sidebar.inicio_btn.configure(
            fg_color=constants.COLORS.get("bg_medium", "#252525"),
            hover_color=constants.COLORS.get("primary", "#3b82f6"),
            text_color=constants.COLORS.get("text_primary", "#e0e0e0")
        )


def highlight_tool(tool_buttons: Dict[str, ctk.CTkButton], tool_name: str = None) -> None:
    """Resalta el botón seleccionado."""
    selected_color = constants.COLORS["primary"]
    normal_color = constants.COLORS["bg_light"]
    
    for name, btn in tool_buttons.items():
        if tool_name is not None and name == tool_name:
            btn.configure(fg_color=selected_color, text_color="white")
        else:
            btn.configure(fg_color=normal_color, text_color=constants.COLORS["text_secondary"])


def on_mousewheel(event, canvas) -> str:
    """Maneja scroll con mouse wheel."""
    if not canvas:
        return "break"
    
    try:
        direction = -1 if (event.delta < 0 or event.num == 4) else 1
        for _ in range(3):
            canvas.yview("scroll", direction, "units")
    except Exception:
        pass
    return "break"


def setup_scroll_binding(scroll_frame, on_wheel_callback=None) -> None:
    """Configura bindings de scroll de forma independiente.
    
    El scroll solo funciona si el mouse está sobre el widget.
    Usa ui.scroll_utils para la implementación.
    """
    from ui.scroll_utils import setup_scrollable_frame
    setup_scrollable_frame(scroll_frame, on_wheel_callback)


def create_tool_buttons(scroll_frame, tools, on_tool_select):
    """Crea botones de herramientas en el scroll frame."""
    tool_buttons = {}
    for tool in tools:
        name = tool['name']
        callback = create_tool_callback(name, on_tool_select)
        btn = ctk.CTkButton(
            scroll_frame,
            text=f"{tool['icon']}  {tool['display_name']}",
            anchor="w",
            command=callback,
            height=50,
            fg_color=constants.COLORS["bg_light"],
            border_width=0,
            hover_color=constants.COLORS["primary_hover"],
            text_color=constants.COLORS["text_secondary"],
            font=ctk.CTkFont(size=constants.FONT_SIZE_LARGE)
        )
        btn.pack(fill="x", pady=4, padx=2)
        tool_buttons[name] = btn
    return tool_buttons


def update_acerca_button(parent, exclude_btn):
    """Actualiza botón Acerca de cuando cambia el tema."""
    for child in parent.winfo_children():
        if isinstance(child, ctk.CTkButton) and child != exclude_btn:
            try:
                child.configure(
                    fg_color=constants.COLORS.get("bg_medium", "#252525"),
                    text_color=constants.COLORS.get("text_primary", "#e0e0e0"),
                    border_color=constants.COLORS.get("border", "#404040"),
                    hover_color=constants.COLORS.get("primary", "#3b82f6")
                )
            except Exception:
                pass