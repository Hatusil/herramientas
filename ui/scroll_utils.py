"""
Utilidades para manejar scroll de forma independiente por widget.
El mouse DEBE estar sobre el widget para que funcione el scroll.

Cumple máxima A3 (acoplamiento bajo) y A1 (SRP).

Uso:
    from ui.scroll_utils import bind_scrollable, setup_scrollable_frame
    
    # Para un frame existente:
    bind_scrollable(scroll_frame, canvas, on_wheel_callback)
    
    # O para configurar un scrollable frame automáticamente:
    setup_scrollable_frame(scroll_frame)
"""
import logging

logger = logging.getLogger(__name__)


def _get_canvas(scroll_frame):
    """Encuentra el canvas interno de un ScrollableFrame."""
    # CTkScrollableFrame usa _parent_canvas internamente
    canvas = getattr(scroll_frame, '_parent_canvas', None)
    if canvas:
        return canvas
    
    # Fallback: buscar en children
    for child in scroll_frame.winfo_children():
        if hasattr(child, 'yview'):
            return child
    
    return None


def get_scroll_direction(event):
    """Determina la dirección del scroll basándose en el evento.
    
    Args:
        event: Evento de mouse (MouseWheel, Button-4, Button-5)
    
    Returns:
        int: -1 para arriba, 1 para abajo
    """
    if hasattr(event, 'delta') and event.delta:
        # MouseWheel (Windows/Linux)
        return -1 if event.delta < 0 else 1
    elif hasattr(event, 'num'):
        # Button-4 (scroll up) / Button-5 (scroll down) en Linux/Mac
        return -1 if event.num == 4 else 1
    return 0


def is_mouse_over(widget, x, y):
    """Verifica si el mouse está sobre el widget dado.
    
    Args:
        widget: Widget a verificar
        x, y: Coordenadas del mouse (del evento)
    
    Returns:
        bool: True si el mouse está sobre el widget
    """
    try:
        # Obtener el widget que está bajo el mouse
        widget_under = widget.winfo_containing(x, y)
        
        # Verificar si es el mismo widget o un hijo
        current = widget_under
        while current:
            if current == widget:
                return True
            current = current.master
        return False
    except Exception:
        return False


def create_scroll_handler(widget, canvas):
    """Crea un handler de scroll que solo funciona si el mouse está sobre el widget.
    
    Args:
        widget: Widget que tiene el scroll ( ScrollableFrame )
        canvas: Canvas interno que hace el scroll real
    
    Returns:
        Callable: Función handler para bindear
    """
    def on_scroll(event):
        # Verificar que el mouse esté sobre ESTE widget
        # Las coordenadas del evento son relativas al widget que recibió el evento
        x = event.x
        y = event.y
        
        if not is_mouse_over(widget, x, y):
            return "break"  # Ignorar, otro widget debe manejarlo
        
        # Determinar dirección
        direction = get_scroll_direction(event)
        if direction == 0:
            return "break"
        
        # Hacer scroll
        if canvas:
            # Multiplicar para scroll más rápido (3 unidades como antes)
            for _ in range(3):
                canvas.yview("scroll", direction, "units")
        
        return "break"
    
    return on_scroll


def bind_scrollable(scroll_frame, canvas=None, on_wheel_callback=None):
    """Bindea scroll de forma que solo afecta a ese widget.
    El mouse DEBE estar sobre el widget para que funcione.
    
    Args:
        scroll_frame: CTkScrollableFrame o similar
        canvas: Canvas interno (opcional, se detecta si no se pasa)
        on_wheel_callback: Callback adicional (opcional)
    
    Returns:
        Callable: El handler creado (por si se necesita)
    """
    if canvas is None:
        canvas = _get_canvas(scroll_frame)
    
    if not canvas:
        logger.warning(f"No se encontró canvas para scroll_frame: {scroll_frame}")
        return None
    
    # Crear handler
    handler = create_scroll_handler(scroll_frame, canvas)
    
    # Bindear eventos de scroll
    scroll_frame.bind("<MouseWheel>", handler)
    scroll_frame.bind("<Button-4>", handler)
    scroll_frame.bind("<Button-5>", handler)
    
    # Si hay callback adicional, ejecutarlo también
    if on_wheel_callback:
        def combined_handler(event):
            handler(event)
            on_wheel_callback(event)
        scroll_frame.bind("<MouseWheel>", combined_handler)
        scroll_frame.bind("<Button-4>", combined_handler)
        scroll_frame.bind("<Button-5>", combined_handler)
    
    return handler


def setup_scrollable_frame(scroll_frame, on_wheel_callback=None):
    """Configura un frame como scrolleable de forma independiente.
    
    Detecta automáticamente el canvas interno y bindea los eventos.
    
    Args:
        scroll_frame: CTkScrollableFrame
        on_wheel_callback: Callback adicional opcional
    
    Returns:
        Callable: El handler creado
    """
    canvas = _get_canvas(scroll_frame)
    return bind_scrollable(scroll_frame, canvas, on_wheel_callback)


def unbind_scrollable(scroll_frame):
    """Quita los bindings de scroll de un frame.
    
    Args:
        scroll_frame: Widget con bindings
    """
    scroll_frame.unbind("<MouseWheel>")
    scroll_frame.unbind("<Button-4>")
    scroll_frame.unbind("<Button-5>")


# Alias para compatibilidad
setup_scroll_binding = setup_scrollable_frame
on_mousewheel = get_scroll_direction