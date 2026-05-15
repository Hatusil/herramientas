"""
Welcome Screen - Pantalla de bienvenida con grilla de herramientas.
Cumple máxima A1 (una responsabilidad) y A0 (<30 líneas por función).
"""
import customtkinter as ctk
from core.constants import font, TOOL_ICONS, TOOL_DESCRIPTIONS
from ui.theme_factory import create_frame, create_card, create_label, create_button


def create_welcome_screen(parent_frame, tools: list, on_tool_select) -> ctk.CTkFrame:
    """
    Crea la pantalla de bienvenida.

    Args:
        parent_frame: Frame padre donde se creará la UI
        tools: Lista de tools ya cargadas (del plugin_manager)
        on_tool_select: Callback (tool_name) -> None

    Returns:
        CTkFrame con la pantalla de bienvenida
    """
    welcome_frame = create_frame(parent_frame)
    welcome_frame.pack(fill="both", expand=True)

    _add_title(welcome_frame)
    _add_subtitle(welcome_frame)
    _add_tool_grid(welcome_frame, tools, on_tool_select)

    return welcome_frame


def _add_title(parent: ctk.CTkFrame) -> None:
    """Agrega el título de bienvenida."""
    create_label(
        parent,
        text="🔧 Herramientas",
        font=font("title", "bold")
    ).pack(pady=(30, 10))


def _add_subtitle(parent: ctk.CTkFrame) -> None:
    """Agrega el subtítulo."""
    create_label(
        parent,
        text="Seleccioná una herramienta para comenzar",
        font=font("normal"),
        text_color="secondary"
    ).pack(pady=(0, 30))


def _add_tool_grid(parent: ctk.CTkFrame, tools: list, on_tool_select) -> None:
    """Agrega la grilla de herramientas (3 columnas)."""
    from core.constants import COLORS
    tools_frame = ctk.CTkFrame(parent, fg_color="transparent")
    tools_frame.pack(fill="both", expand=True, padx=20)
    
    for i, tool in enumerate(tools):
        _add_tool_card(tools_frame, tool, i, on_tool_select)


def _add_tool_card(parent: ctk.CTkFrame, tool: dict, index: int, on_select) -> None:
    """Agrega una card de tool a la grilla."""
    from core.constants import COLORS

    row = index // 3
    col = index % 3

    parent.grid_columnconfigure(col, weight=1)
    parent.grid_rowconfigure(row, weight=1)

    tool_name = tool['name']
    icon = TOOL_ICONS.get(tool_name, '🔧')
    description = TOOL_DESCRIPTIONS.get(tool_name, '')

    # Card
    card = create_card(parent)
    card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    # Botón
    create_button(
        card,
        text=f"{icon} {tool.get('display_name', tool_name)}",
        command=lambda t=tool_name: on_select(t),
        font=font("normal", "bold"),
        height=50
    ).pack(fill="x", padx=10, pady=(10, 5))

    # Descripción
    if description:
        create_label(
            card,
            text=description,
            font=font("xsmall"),
            text_color="secondary",
            wraplength=150
        ).pack(padx=10, pady=(0, 10))