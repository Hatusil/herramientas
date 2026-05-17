"""
Window utilities - configuración de ventana.
Separado de app.py por SRP (máxima R0: clases <300 líneas).
"""
from core import constants


def center_window(window, app_width: int = None, app_height: int = None) -> None:
    """
    Centra la ventana en la pantalla.
    
    Args:
        window: Ventana de tkinter a centrar
        app_width: Ancho de la app (default desde constants)
        app_height: Alto de la app (default desde constants)
    """
    window.update_idletasks()
    
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    width = app_width or constants.APP_WIDTH
    height = app_height or constants.APP_HEIGHT
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2 - 30
    
    window.geometry(f"{width}x{height}+{x}+{y}")


def on_resize(event) -> str:
    """Maneja cuando se redimensiona la ventana."""
    return "break"  # Por ahora solo mantener