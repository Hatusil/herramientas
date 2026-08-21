"""
Theme Factory - Centralized widget creation with theme applied.
Cumple con máxima A3 (acoplamiento bajo) y A1 (SRP).

Uso:
    from ui.theme_factory import create_button, create_label, create_frame
    create_button(parent, "Click me", callback)

Convención: los colores del tema son SIEMPRE defaults; cualquier kwarg del
caller tiene prioridad (nunca hay colisión de kwargs duplicados en CTk*).
"""
import customtkinter as ctk
from core.constants import COLORS

# Mapeo de nombres de color a claves de COLORS
_COLOR_MAP = {
    # Text colors
    "primary": "text_primary",
    "secondary": "text_secondary",
    "muted": "text_muted",
    # Background colors
    "bg_dark": "bg_dark",
    "bg_medium": "bg_medium",
    "bg_light": "bg_light",
    # Others
    "border": "border",
    "button_fg": "button_fg",
    "button_hover": "button_hover",
}


def _get_color(color: str) -> str:
    """Convierte nombre de color a valor real de COLORS."""
    if color in _COLOR_MAP:
        return COLORS.get(_COLOR_MAP[color], color)
    return color  # Si no está en el mapa, usa el valor tal cual


# ============================================================================
# BOTONES
# ============================================================================

def create_button(parent, text: str, command, **kwargs):
    """Botón con colores del tema actual."""
    theme = {
        "fg_color": COLORS.get("button_fg"),
        "hover_color": COLORS.get("button_hover"),
        "text_color": COLORS.get("text_primary"),
    }
    return ctk.CTkButton(parent, text=text, command=command, **{**theme, **kwargs})


def create_primary_button(parent, text: str, command, **kwargs):
    """Botón primario (color de acento)."""
    theme = {
        "fg_color": COLORS.get("primary"),
        "hover_color": COLORS.get("primary_hover"),
        "text_color": "white",
    }
    return ctk.CTkButton(parent, text=text, command=command, **{**theme, **kwargs})


def create_tool_button(parent, text: str, command, **kwargs):
    """Botón de tool (estilo sidebar)."""
    theme = {
        "fg_color": COLORS.get("bg_medium"),
        "text_color": COLORS.get("text_primary"),
        "hover_color": COLORS.get("primary"),
    }
    return ctk.CTkButton(parent, text=text, command=command, **{**theme, **kwargs})


def create_bordered_button(parent, text: str, command, **kwargs):
    """Botón con borde (estilo sidebar secondary)."""
    theme = {
        "fg_color": COLORS.get("bg_medium"),
        "text_color": COLORS.get("text_primary"),
        "border_width": 1,
        "border_color": COLORS.get("border"),
        "hover_color": COLORS.get("primary"),
    }
    return ctk.CTkButton(parent, text=text, command=command, **{**theme, **kwargs})


def create_danger_button(parent, text: str, command, **kwargs):
    """Botón de peligro (rojo, para acciones destructivas)."""
    theme = {
        "fg_color": COLORS.get("error"),
        "hover_color": COLORS.get("warning"),
        "text_color": "white",
    }
    return ctk.CTkButton(parent, text=text, command=command, **{**theme, **kwargs})


# ============================================================================
# LABELS
# ============================================================================

def create_label(parent, text: str = "", text_color: str = "primary", **kwargs):
    """Label con colores del tema actual.

    Args:
        text_color: "primary", "secondary", "muted" o color directo
    """
    return ctk.CTkLabel(
        parent,
        text=text,
        text_color=_get_color(text_color),
        **kwargs
    )


def create_secondary_label(parent, text: str = "", **kwargs):
    """Label secundario (texto más suave)."""
    defaults = {"text_color": COLORS.get("text_secondary")}
    return ctk.CTkLabel(parent, text=text, **{**defaults, **kwargs})


def create_muted_label(parent, text: str = "", **kwargs):
    """Label muted (texto deshabilitado o info menor)."""
    defaults = {"text_color": COLORS.get("text_muted")}
    return ctk.CTkLabel(parent, text=text, **{**defaults, **kwargs})


# ============================================================================
# FRAMES
# ============================================================================

def create_frame(parent, **kwargs):
    """Frame con colores del tema actual."""
    return ctk.CTkFrame(parent, **{"fg_color": COLORS.get("bg_light"), **kwargs})


def create_panel(parent, **kwargs):
    """Panel más oscuro para secciones."""
    return ctk.CTkFrame(parent, **{"fg_color": COLORS.get("bg_medium"), **kwargs})


def create_border_frame(parent, **kwargs):
    """Frame con borde visible."""
    theme = {
        "fg_color": COLORS.get("bg_light"),
        "border_color": COLORS.get("border"),
        "border_width": 1,
    }
    return ctk.CTkFrame(parent, **{**theme, **kwargs})


def create_control_frame(parent, **kwargs):
    """Frame de control (sidebar) con borde y colors."""
    theme = {
        "fg_color": COLORS.get("bg_medium"),
        "border_color": COLORS.get("border"),
        "border_width": 1,
    }
    return ctk.CTkFrame(parent, **{**theme, **kwargs})


def create_divider(parent, height: int = 1, **kwargs):
    """Divisor horizontal."""
    return ctk.CTkFrame(
        parent, height=height, **{"fg_color": COLORS.get("border"), **kwargs}
    )


def create_card(parent, corner_radius: int = 10, **kwargs):
    """Card con bordes redondeados."""
    return ctk.CTkFrame(
        parent, corner_radius=corner_radius,
        **{"fg_color": COLORS.get("bg_light"), **kwargs}
    )


# ============================================================================
# INPUTS
# ============================================================================

def create_entry(parent, **kwargs):
    """Entry con colores del tema actual."""
    theme = {
        "fg_color": COLORS.get("bg_input"),
        "text_color": COLORS.get("text_primary"),
        "border_color": COLORS.get("border"),
    }
    return ctk.CTkEntry(parent, **{**theme, **kwargs})


def create_textbox(parent, **kwargs):
    """Textbox con colores del tema actual."""
    theme = {
        "fg_color": COLORS.get("bg_input"),
        "text_color": COLORS.get("text_primary"),
        "border_color": COLORS.get("border"),
    }
    return ctk.CTkTextbox(parent, **{**theme, **kwargs})


def create_switch(parent, **kwargs):
    """Switch con colores del tema."""
    theme = {
        "fg_color": COLORS.get("bg_hover"),
        "progress_color": COLORS.get("primary"),
        "text_color": COLORS.get("text_primary"),
    }
    kwargs.setdefault("text", "")
    return ctk.CTkSwitch(parent, **{**theme, **kwargs})


def create_checkbox(parent, **kwargs):
    """Checkbox con colores del tema."""
    theme = {
        "fg_color": COLORS.get("primary"),
        "hover_color": COLORS.get("primary_hover"),
        "text_color": COLORS.get("text_primary"),
    }
    kwargs.setdefault("text", "")
    return ctk.CTkCheckBox(parent, **{**theme, **kwargs})


def create_radiobutton(parent, **kwargs):
    """RadioButton con colores del tema."""
    theme = {
        "fg_color": COLORS.get("primary"),
        "hover_color": COLORS.get("primary_hover"),
        "text_color": COLORS.get("text_primary"),
    }
    kwargs.setdefault("text", "")
    return ctk.CTkRadioButton(parent, **{**theme, **kwargs})


# ============================================================================
# PROGRESS & SLIDERS
# ============================================================================

def create_progress_bar(parent, **kwargs):
    """Progress bar con colores del tema."""
    theme = {
        "progress_color": COLORS.get("primary"),
        "fg_color": COLORS.get("bg_hover"),
    }
    return ctk.CTkProgressBar(parent, **{**theme, **kwargs})


def create_slider(parent, **kwargs):
    """Slider con colores del tema."""
    theme = {
        "fg_color": COLORS.get("bg_hover"),
        "progress_color": COLORS.get("primary"),
        "button_color": COLORS.get("primary"),
        "button_hover_color": COLORS.get("primary_hover"),
    }
    return ctk.CTkSlider(parent, **{**theme, **kwargs})


# ============================================================================
# SCROLLABLE
# ============================================================================

def create_scrollable_frame(parent, **kwargs):
    """Scrollable frame con colores del tema."""
    theme = {
        "fg_color": COLORS.get("bg_light"),
        "label_fg_color": COLORS.get("bg_medium"),
        "label_text_color": COLORS.get("text_primary"),
    }
    return ctk.CTkScrollableFrame(parent, **{**theme, **kwargs})


# ============================================================================
# TABS
# ============================================================================

def create_tabview(parent, **kwargs):
    """Tabview con colores del tema."""
    return ctk.CTkTabview(parent, **{"fg_color": COLORS.get("bg_light"), **kwargs})


def create_option_menu(parent, **kwargs):
    """Option menu con colores del tema."""
    theme = {
        "fg_color": COLORS.get("bg_input"),
        "button_color": COLORS.get("button_fg"),
        "button_hover_color": COLORS.get("button_hover"),
        "text_color": COLORS.get("text_primary"),
    }
    return ctk.CTkOptionMenu(parent, **{**theme, **kwargs})


def create_combo_box(parent, **kwargs):
    """Combo box con colores del tema."""
    theme = {
        "fg_color": COLORS.get("bg_input"),
        "border_color": COLORS.get("border"),
        "button_color": COLORS.get("button_fg"),
        "button_hover_color": COLORS.get("button_hover"),
        "text_color": COLORS.get("text_primary"),
    }
    return ctk.CTkComboBox(parent, **{**theme, **kwargs})
