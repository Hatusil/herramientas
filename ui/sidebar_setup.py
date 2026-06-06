"""
Setup functions para Sidebar.
Cumple máxima A1 (una responsabilidad).
"""
import customtkinter as ctk
from core import constants
from core.constants import font, FONT_SIZE_TITLE
from ui.sidebar_helpers import find_logo_path, make_circle_image
from ui.theme_factory import create_secondary_label, create_tool_button, create_bordered_button


def setup_logo(parent) -> ctk.CTkLabel:
    """Configura el logo en el sidebar."""
    logo_path = find_logo_path()
    if not logo_path:
        return None
    
    try:
        circle_img = make_circle_image(logo_path, size=50)
        logo = ctk.CTkImage(light_image=circle_img, dark_image=circle_img, size=(50, 50))
        return ctk.CTkLabel(parent, image=logo, text="")
    except Exception:
        return None


def setup_title(parent) -> None:
    """Configura el título 'Herramientas'."""
    ctk.CTkLabel(
        parent,
        text="Herramientas",
        font=ctk.CTkFont(size=FONT_SIZE_TITLE, weight="bold")
    ).pack(pady=(5, 2))


def setup_buttons(parent, on_inicio, on_acerca_de) -> None:
    """Configura botones de Inicio y Acerca de."""
    # Botón Inicio
    create_tool_button(
        parent,
        text="🏠 Inicio",
        command=on_inicio,
        height=30
    ).pack(fill="x", padx=10, pady=(8, 5))
    
    # Botón Acerca de
    create_bordered_button(
        parent,
        text="ℹ️ Acerca de",
        command=on_acerca_de,
        height=36,
        font=font("small")
    ).pack(fill="x", padx=10, pady=(8, 0))


def setup_theme_label(parent, current_theme) -> ctk.CTkLabel:
    """Configura la etiqueta del tema actual."""
    label = create_secondary_label(
        parent,
        text=f"Modo: {'Claro' if current_theme == 'light' else 'Oscuro'}",
        font=font("xsmall")
    )
    label.pack(padx=12, pady=(0, 5))
    return label