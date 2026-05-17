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


def rebuild_content_frame(parent, old_frame) -> ctk.CTkScrollableFrame:
    """
    Destruye y recrea el content frame para evitar problemas de limpieza.
    CTkScrollableFrame maneja scroll internamente - no necesita setup adicional.
    
    Args:
        parent: Widget padre
        old_frame: Frame existente a destruir
        
    Returns:
        Nuevo CTkScrollableFrame
    """
    # Destruir frame anterior completamente
    if old_frame is not None:
        try:
            # Destruir todos los hijos primero
            for child in old_frame.winfo_children():
                try:
                    child.destroy()
                except Exception:
                    pass
            # Luego destruir el frame principal
            old_frame.destroy()
        except Exception:
            pass
    
    # Forzar procesamiento de eventos para asegurar limpieza
    try:
        parent.update_idletasks()
    except Exception:
        pass
    
    # Crear nuevo frame
    new_frame = create_content_frame(parent)
    
    # Grid el nuevo frame
    new_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    
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