"""
Módulo de configuración y persistencia de preferencias.
"""
import json
import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Nombre del archivo de configuración
CONFIG_FILENAME = "config.json"


def get_config_path() -> Path:
    """
    Retorna la ruta al directorio de datos del usuario.
    - Windows: %APPDATA%/herramientas/
    - Linux: ~/.config/herramientas/
    
    Returns:
        Path al directorio de configuración
    """
    if os.name == "nt":  # Windows
        base_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:  # Linux/Mac
        base_dir = Path.home() / ".config"
    
    config_dir = base_dir / "herramientas"
    
    # Crear directorio si no existe
    config_dir.mkdir(parents=True, exist_ok=True)
    
    return config_dir


def load_theme() -> str:
    """
    Carga el tema desde config.json.
    Retorna 'dark' por defecto si no existe, está corrupto, o tiene valor inválido.
    
    Returns:
        Theme actual ('dark' o 'light')
    """
    config_path = get_config_path() / CONFIG_FILENAME
    
    default_theme = "dark"
    
    # Si no existe el archivo, retornar default
    if not config_path.exists():
        logger.info(f"Config no existe, usando tema por defecto: {default_theme}")
        # Crear archivo válido con tema por defecto
        save_theme(default_theme)
        return default_theme
    
    # Intentar leer el archivo
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Validar que sea un tema válido
        theme = data.get("theme", default_theme)
        
        if theme in ("dark", "light"):
            logger.info(f"Tema cargado: {theme}")
            return theme
        else:
            logger.warning(f"Tema inválido '{theme}', usando: {default_theme}")
            # Regenerar con tema válido
            save_theme(default_theme)
            return default_theme
            
    except json.JSONDecodeError as e:
        # JSON inválido - usar default y regenerar
        logger.warning(f"Config corrupto (JSON inválido): {e}. Usando tema por defecto.")
        save_theme(default_theme)
        return default_theme
    except Exception as e:
        logger.error(f"Error leyendo config: {e}. Usando tema por defecto.")
        save_theme(default_theme)
        return default_theme


def save_theme(theme: str) -> None:
    """
    Guarda el tema en config.json.
    
    Args:
        theme: Tema a guardar ('dark' o 'light')
    """
    if theme not in ("dark", "light"):
        logger.warning(f"Tema inválido '{theme}', no se guardará")
        return
    
    config_path = get_config_path() / CONFIG_FILENAME
    
    try:
        data = {"theme": theme}
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Tema guardado: {theme}")
    except Exception as e:
        logger.error(f"Error guardando tema: {e}")


def get_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Obtiene un valor de configuración.
    
    Args:
        key: Clave a buscar
        default: Valor por defecto si no existe
        
    Returns:
        Valor de la clave o default
    """
    config_path = get_config_path() / CONFIG_FILENAME
    
    if not config_path.exists():
        return default
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(key, default)
    except Exception:
        return default


def set_config_value(key: str, value: str) -> None:
    """
    Establece un valor de configuración.
    
    Args:
        key: Clave a establecer
        value: Valor a guardar
    """
    config_path = get_config_path() / CONFIG_FILENAME
    
    try:
        # Cargar config existente o crear nuevo
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}
        
        data[key] = value
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error guardando config {key}: {e}")