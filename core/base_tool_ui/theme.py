"""
ThemeMixin - Mixin para actualización de tema.
"""
from core.constants import COLORS


class ThemeMixin:
    """Mixin para que todos los widgets actualicen con el tema."""
    
    def refresh_theme(self) -> None:
        """Override en cada subclase para actualizar sus colores."""
        # Por defecto, actualiza el color de fondo
        self.configure(fg_color=COLORS.get("bg_medium"))
        
        # Las subclases que usan COLORS deben override este método
        # y llamar a super().refresh_theme() si quieren actualizar el fondo