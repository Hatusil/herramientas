"""
PluginManager: Sistema de carga dinámica de herramientas.
Escanea el directorio tools/ y carga automáticamente las tools disponibles.
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from core.base_tool import BaseTool
from core import constants

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Gestor de plugins que descubre y carga herramientas automáticamente.
    """
    
    def __init__(self):
        self.tools: Dict[str, Any] = {}
        self.tool_instances: Dict[str, BaseTool] = {}
        self.tool_status: Dict[str, str] = {}
    
    def discover_tools(self) -> None:
        """
        Escanea el directorio tools/ y busca plugins válidos.
        """
        tools_path = constants.TOOLS_DIR
        
        if not tools_path.exists():
            logger.warning(f"Directorio de tools no encontrado: {tools_path}")
            return
        
        # Buscar subdirectorios que parecen plugins
        for item in tools_path.iterdir():
            if not item.is_dir():
                continue
            if item.name.startswith('_'):
                continue  # Ignorar carpetas que empiezan con _
            
            self._load_tool(item)
    
    def _load_tool(self, tool_path: Path) -> None:
        """
        Intenta cargar una herramienta desde el directorio dado.
        
        Args:
            tool_path: Path al directorio de la tool
        """
        tool_name = tool_path.name
        
        # Intentar importar el módulo (tools.audio_tool)
        module_name = f"tools.{tool_name}"
        
        try:
            # Importar directamente el paquete
            module = __import__(module_name, fromlist=[tool_name])
            
            # Buscar clase que hereda de BaseTool
            tool_class = self._find_tool_class(module)
            
            if tool_class is None:
                logger.warning(f"No se encontró BaseTool en {tool_name}")
                self.tool_status[tool_name] = constants.TOOL_STATUS_ERROR
                return
            
            # Instanciar la tool
            instance = tool_class()
            self.tool_instances[tool_name] = instance
            self.tool_status[tool_name] = constants.TOOL_STATUS_OK
            
            logger.info(f"Tool '{tool_name}' cargada exitosamente")
            
        except Exception as e:
            logger.error(f"Error cargando tool '{tool_name}': {e}")
            self.tool_status[tool_name] = constants.TOOL_STATUS_ERROR
    
    def _find_tool_class(self, module: Any) -> Optional[type]:
        """
        Busca una clase que hereda de BaseTool en el módulo.
        
        Args:
            module: Módulo importado
            
        Returns:
            Clase que hereda de BaseTool o None
        """
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, BaseTool) and 
                attr is not BaseTool):
                return attr
        return None
    
    def get_tools(self) -> Dict[str, BaseTool]:
        """
        Retorna diccionario de tools cargadas.
        
        Returns:
            Dict[str, BaseTool]: {nombre: instancia}
        """
        return self.tool_instances
    
    def get_tools_list(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de tools con información para la UI.
        Maneja errores para no crashear con plugins rotos.
        
        Returns:
            List[Dict]: [{name, icon, description, status}]
        """
        result = []
        for name, instance in self.tool_instances.items():
            try:
                display_name = instance.get_name()
            except Exception as e:
                logger.error(f"Error en get_name() de '{name}': {e}")
                display_name = f"[Error: {name}]"
                self.tool_status[name] = constants.TOOL_STATUS_ERROR
            
            try:
                icon = instance.get_icon()
            except Exception as e:
                logger.error(f"Error en get_icon() de '{name}': {e}")
                icon = "⚠️"
            
            try:
                description = instance.get_description()
            except Exception as e:
                logger.error(f"Error en get_description() de '{name}': {e}")
                description = "Error al cargar descripción"
            
            result.append({
                'name': name,
                'display_name': display_name,
                'icon': icon,
                'description': description,
                'status': self.tool_status.get(name, constants.TOOL_STATUS_ERROR)
            })
        return result
    
    def get_status(self, tool_name: str) -> str:
        """Retorna el estado de una tool específica."""
        return self.tool_status.get(tool_name, constants.TOOL_STATUS_ERROR)