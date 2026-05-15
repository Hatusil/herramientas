"""
BaseToolUI - UI base para herramientas con selector de archivos.

Combina los mixins en una clase coherente para mantener compatibilidad.
"""
import customtkinter as ctk
import logging
from typing import Callable, Optional, List, Dict, Any

from core.constants import font, COLORS

logger = logging.getLogger(__name__)

# Importar mixins
from .file_selector import FileSelectorMixin
from .progress import ProgressMixin
from .theme import ThemeMixin


class BaseToolUI(ThemeMixin, FileSelectorMixin, ProgressMixin, ctk.CTkFrame):
    """
    Clase base para UI de herramientas con selector de archivos.
    
    Combina:
    - ThemeMixin: Actualización de tema
    - FileSelectorMixin: Selector de archivos con listbox
    - ProgressMixin: Barra de progreso y procesamiento async
    
    Args:
        master: Frame padre donde se construirá la UI
        on_process: Callback que se llama cuando se procesan archivos
        **kwargs: Argumentos adicionales para CTkFrame
    """
    
    def __init__(self, master, on_process: Callable, **kwargs):
        super().__init__(master, **kwargs)
        
        self.on_process = on_process
        self.files: List[str] = []
        self._processing = False
        self.is_processing = False
        
        self._setup_ui()
    
    # === Override hooks ===
    
    def _get_file_dialog_filters(self) -> list:
        """Override: Filtros para el diálogo de archivos."""
        return [("Todos los archivos", "*.*")]
    
    def _get_file_label(self) -> str:
        """Override: Texto de la etiqueta para archivos."""
        return "Archivos:"
    
    def _get_custom_buttons(self) -> list:
        """Override: Botones adicionales."""
        return []
    
    def _add_folder_custom(self) -> bool:
        """Override: Implementación personalizada para agregar carpetas."""
        return False
    
    def _add_files_custom(self) -> bool:
        """Override: Implementación personalizada para agregar archivos."""
        return False
    
    # === Main UI setup ===
    
    def _setup_ui(self) -> None:
        """Construye la UI. Override para customize completa."""
        # Delegar al mixin de file selector
        self._setup_file_selector()


# Alias para compatibilidad con código existente
# El archivo original base_tool_ui.py sigue existiendo
# Esta clase nueva puede importarse como:
# from core.base_tool_ui import BaseToolUI


# ============================================================================
# BaseToolUIWithTabs - UI base con soporte para tabs
# ============================================================================

class BaseToolUIWithTabs(BaseToolUI):
    """
    Clase base para UI de herramientas con tabs.
    
    Extiende BaseToolUI con soporte integrado para CTkTabview.
    Las subclases definen sus tabs en _get_tabs() y configuran cada uno
    en los métodos _setup_tab_{name}().
    
    Uso:
        class MiToolUI(BaseToolUIWithTabs):
            def _get_tabs(self):
                return ["Info", "Procesar", "Resultados"]
            
            def _setup_tab_info(self, tab):
                # Configurar tab Info
                pass
    """
    
    def __init__(self, master, on_process: Callable, **kwargs):
        # No llamar a _setup_ui del padre (que crea file selector)
        # Las tools con tabs probablemente no necesitan el selector básico
        ctk.CTkFrame.__init__(self, master, **kwargs)
        
        self.on_process = on_process
        self.files: list = []
        self._processing = False
        self.is_processing = False
        self.tabview = None
        self._tabs = {}
        
        # Configurar progress bar
        self._setup_progress_bar()
        
        # Crear tabs
        self._build_tabs()
    
    def _get_tabs(self) -> list:
        """
        Override: Retorna lista de nombres de tabs.
        
        Returns:
            list: Nombres de los tabs a crear
        """
        return []
    
    def _build_tabs(self) -> None:
        """Crea el tabview y los tabs definidos."""
        tab_names = self._get_tabs()
        if not tab_names:
            return
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        for name in tab_names:
            self._tabs[name] = self.tabview.add(name)
            
            # Llamar al método de setup si existe
            method_name = f"_setup_tab_{name.lower().replace(' ', '_')}"
            if hasattr(self, method_name):
                getattr(self, method_name)(self._tabs[name])
    
    def get_tab(self, name: str):
        """Obtiene un tab por nombre."""
        return self._tabs.get(name)