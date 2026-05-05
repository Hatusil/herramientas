"""
Tooltip: Ayuda contextual flotante.
"""
import logging
import customtkinter as ctk

logger = logging.getLogger(__name__)


class ToolTip:
    """Tooltip flotante que aparece al hover."""
    
    def __init__(self, widget, text: str, delay: int = 500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip = None
        self.timer = None
        
        # Bind events
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
        self.widget.bind("<Motion>", self._on_motion)
    
    def _on_enter(self, event=None):
        """Inicia timer para mostrar tooltip."""
        self.timer = self.widget.after(self.delay, self._show_tooltip)
    
    def _on_leave(self, event=None):
        """Oculta tooltip."""
        self._hide_tooltip()
    
    def _on_motion(self, event=None):
        """Si hay timer, lo cancela y reinicia."""
        if self.timer:
            self.widget.after_cancel(self.timer)
            self.timer = None
    
    def _show_tooltip(self):
        """Muestra el tooltip."""
        if self.tooltip:
            return
        
        # Check if widget still exists before showing tooltip
        # Prevents race condition when widget is destroyed while timer is pending
        try:
            if not self.widget.winfo_exists():
                return
        except Exception:
            return
        
        # Obtener posición del widget
        try:
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        except Exception:
            return
        
        # Crear tooltip window
        self.tooltip = ctk.CTkToplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # No mostrar en taskbar
        self.tooltip.attributes('-topmost', True)
        
        # Frame con el texto
        frame = ctk.CTkFrame(
            self.tooltip,
            corner_radius=6,
            fg_color=("#2a2a2a", "#1a1a1a"),
            border_width=1,
            border_color=("#3a3a3a", "#2a2a2a")
        )
        frame.pack(fill="both", expand=True, padx=8, pady=4)
        
        label = ctk.CTkLabel(
            frame,
            text=self.text,
            font=ctk.CTkFont(size=14),
            justify="left",
            anchor="w"
        )
        label.pack()
    
    def _hide_tooltip(self):
        """Oculta y destruye el tooltip."""
        if self.timer:
            self.widget.after_cancel(self.timer)
            self.timer = None
        
        if self.tooltip:
            try:
                self.tooltip.destroy()
            except Exception as e:
                logger.warning(f"Error destroying tooltip: {e}")
            self.tooltip = None


def add_tooltip(widget, text: str, delay: int = 500):
    """Función helper para agregar tooltip a un widget."""
    return ToolTip(widget, text, delay)