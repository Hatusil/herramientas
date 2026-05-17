"""
Content frame manager - gestión del área de contenido.
Separado de app.py por SRP (máxima R0: clases <300 líneas).
"""
import logging
import customtkinter as ctk
from core import constants

logger = logging.getLogger(__name__)


def create_content_frame(parent) -> ctk.CTkScrollableFrame:
    """
    Crea un CTkScrollableFrame para el área de contenido.
    
    Args:
        parent: Widget padre
        
    Returns:
        CTkScrollableFrame configurado
    """
    frame = ctk.CTkScrollableFrame(
        parent,
        label_text="",
        fg_color=constants.COLORS["bg_medium"]
    )
    return frame


def rebuild_content_frame(parent, old_frame, setup_scroll_fn) -> ctk.CTkScrollableFrame:
    """
    Destruye y recrea el content frame para evitar problemas de limpieza.
    
    Args:
        parent: Widget padre
        old_frame: Frame existente a destruir
        setup_scroll_fn: Función para configurar scroll
        
    Returns:
        Nuevo CTkScrollableFrame
    """
    try:
        old_frame.destroy()
    except Exception:
        pass
    
    new_frame = create_content_frame(parent)
    setup_scroll_fn()
    
    return new_frame


def clear_content_frame(frame) -> None:
    """
    Limpia los hijos del content frame para CTkScrollableFrame.
    
    Args:
        frame: CTkScrollableFrame a limpiar
    """
    def clean_all_children(widget):
        """Limpia todos los descendientes de un widget."""
        try:
            children = widget.winfo_children()
            for child in children:
                clean_all_children(child)
                try:
                    child.destroy()
                except Exception:
                    pass
        except Exception:
            pass
    
    try:
        # Buscar cualquier atributo que parezca un frame interno
        for attr_name in dir(frame):
            if 'interior' in attr_name.lower() or attr_name == 'frame':
                try:
                    inner = getattr(frame, attr_name, None)
                    if inner and hasattr(inner, 'winfo_children'):
                        clean_all_children(inner)
                        logger.info(f"Limpio {attr_name}")
                except Exception:
                    pass
        
        # También limpiar hijos directos
        clean_all_children(frame)
            
    except Exception as e:
        logger.warning(f"Error limpiar content frame: {e}")