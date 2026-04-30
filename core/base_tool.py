"""
BaseTool: Interfaz abstracta para herramientas del sistema.
Todas las tools deben heredar de esta clase y implementar los métodos requeridos.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseTool(ABC):
    """
    Clase base abstracta que define el contract para todas las herramientas.
    
    Cada tool debe implementar:
    - get_name(): nombre para mostrar en la sidebar
    - get_icon(): nombre del ícono (lucide o emoji)
    - get_description(): descripción breve de la tool
    - build_ui(parent_frame): construye la UI en el frame recibido
    - process(files, options): procesa los archivos
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Retorna el nombre de la herramienta para mostrar en la sidebar.
        
        Returns:
            str: Nombre corto (ej: "Audio", "PDF", "Imagenes")
        """
        pass
    
    @abstractmethod
    def get_icon(self) -> str:
        """
        Retorna el nombre del ícono para mostrar en la sidebar.
        
        Returns:
            str: Nombre de ícono (lucide: "music", "file-text", etc.) o emoji
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Retorna una descripción breve de la herramienta.
        
        Returns:
            str: Descripción de una línea
        """
        pass
    
    @abstractmethod
    def build_ui(self, parent_frame: Any) -> None:
        """
        Construye la interfaz de usuario de la herramienta en el frame recibido.
        
        Args:
            parent_frame: CTkFrame donde se deben agregar los widgets
        """
        pass
    
    @abstractmethod
    def process(self, files: List[str], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa los archivos seleccionados.
        
        Args:
            files: Lista de rutas de archivos a procesar
            options: Diccionario con opciones de procesamiento
            
        Returns:
            dict: Resultado con claves 'success', 'output_files', 'message', 'error'
        """
        pass