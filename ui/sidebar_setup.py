"""
Setup functions para Sidebar.
Cumple máxima A1 (una responsabilidad).
"""
import customtkinter as ctk
from core import constants
from core.constants import font, FONT_SIZE_TITLE
from ui.sidebar_helpers import find_logo_path, make_circle_image


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
    ctk.CTkButton(
        parent,
        text="🏠 Inicio",
        command=on_inicio,
        fg_color=constants.COLORS.get("bg_medium", "#252525"),
        hover_color=constants.COLORS.get("primary", "#3b82f6"),
        text_color=constants.COLORS.get("text_primary", "#e0e0e0"),
        height=30
    ).pack(fill="x", padx=10, pady=(8, 5))
    
    # Botón Acerca de
    btn = ctk.CTkButton(
        parent,
        text="ℹ️ Acerca de",
        command=on_acerca_de,
        fg_color=constants.COLORS.get("bg_medium", "#252525"),
        text_color=constants.COLORS.get("text_primary", "#e0e0e0"),
        border_width=1,
        border_color=constants.COLORS.get("border", "#404040"),
        hover_color=constants.COLORS.get("primary", "#3b82f6"),
        height=36,
        font=font("small")
    )
    btn.pack(fill="x", padx=10, pady=(8, 0))


def setup_theme_switch(parent, on_toggle, current_theme) -> ctk.CTkSwitch:
    """Configura el switch de cambio de tema."""
    theme_var = ctk.StringVar(value=current_theme)
    
    switch = ctk.CTkSwitch(
        parent,
        text="",
        variable=theme_var,
        command=on_toggle,
        onvalue="light",
        offvalue="dark"
    )
    switch.pack(padx=12, pady=5)
    return switch


def setup_theme_label(parent, current_theme) -> ctk.CTkLabel:
    """Configura la etiqueta del tema actual."""
    label = ctk.CTkLabel(
        parent,
        text=f"Modo: {'Claro' if current_theme == 'light' else 'Oscuro'}",
        text_color=constants.COLORS.get("text_secondary", "#9ca3af"),
        font=font("xsmall")
    )
    label.pack(padx=12, pady=(0, 5))
    return label