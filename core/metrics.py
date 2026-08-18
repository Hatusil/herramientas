"""
Módulo de métricas para herramientas.
Proporciona clases para contar, gauge y temporizadores.
"""
import logging
import time
import os
from typing import Optional, Dict, Union

logger = logging.getLogger(__name__)

# Configuración global - controlado por variable de entorno
_METRICS_ENABLED = os.environ.get('METRICS_ENABLED', 'false').lower() == 'true'

# Registry global para métricas persistentes
_metrics_registry: Dict[str, Union['Counter', 'Gauge']] = {}


class Counter:
    """Contador de métricas con incremento simple."""
    
    def __init__(self, name: str, auto_register: bool = True):
        """
        Inicializa un contador.
        
        Args:
            name: Nombre identificador del contador
            auto_register: Si True, registra automáticamente en el registry global
        """
        self.name = name
        self._value = 0
        if auto_register:
            _metrics_registry[name] = self
    
    def increment(self, value: int = 1) -> None:
        """
        Incrementa el contador.
        
        Args:
            value: Cantidad a incrementar (default: 1)
        """
        self._value += value
        if _METRICS_ENABLED:
            logger.info(f"[METRIC] Counter '{self.name}' incremented by {value} -> {self._value}")
    
    @property
    def value(self) -> int:
        """Retorna el valor actual del contador."""
        return self._value
    
    def reset(self) -> None:
        """Reinicia el contador a cero."""
        self._value = 0
        if _METRICS_ENABLED:
            logger.info(f"[METRIC] Counter '{self.name}' reset")


class Gauge:
    """Métrica de gauge - valor actual instantáneo."""
    
    def __init__(self, name: str, auto_register: bool = True):
        """
        Inicializa un gauge.
        
        Args:
            name: Nombre identificador del gauge
            auto_register: Si True, registra automáticamente en el registry global
        """
        self.name = name
        self._value = 0.0
        if auto_register:
            _metrics_registry[name] = self
    
    def set(self, value: float) -> None:
        """
        Establece el valor del gauge.
        
        Args:
            value: Nuevo valor para el gauge
        """
        self._value = value
        if _METRICS_ENABLED:
            logger.info(f"[METRIC] Gauge '{self.name}' set to {value}")
    
    @property
    def value(self) -> float:
        """Retorna el valor actual del gauge."""
        return self._value
    
    def reset(self) -> None:
        """Reinicia el gauge a cero."""
        self._value = 0.0
        if _METRICS_ENABLED:
            logger.info(f"[METRIC] Gauge '{self.name}' reset")


class Timer:
    """Temporizador - mide duración de operaciones usando context manager."""
    
    def __init__(self, name: str):
        """
        Inicializa un temporizador.
        
        Args:
            name: Nombre identificador del temporizador
        """
        self.name = name
        self._start_time: Optional[float] = None
        self._elapsed: float = 0.0
    
    def __enter__(self):
        """Inicia el temporizador."""
        self._start_time = time.time()
        return self
    
    def __exit__(self, *args):
        """Finaliza el temporizador y registra la duración."""
        if self._start_time is not None:
            self._elapsed = time.time() - self._start_time
            if _METRICS_ENABLED:
                logger.info(f"[METRIC] Timer '{self.name}' finished: {self._elapsed:.4f}s")
    
    @property
    def elapsed(self) -> float:
        """Retorna el tiempo transcurrido en segundos."""
        return self._elapsed


# ============================================================================
# Funciones helper de conveniencia
# ============================================================================

def increment(name: str, value: int = 1) -> None:
    if name in _metrics_registry:
        _metrics_registry[name].increment(value)
    else:
        Counter(name).increment(value)


def gauge_set(name: str, value: float) -> None:
    if name in _metrics_registry:
        _metrics_registry[name].set(value)
    else:
        Gauge(name).set(value)


def timer(name: str) -> Timer:
    """
    Función de conveniencia para crear un temporizador.
    
    Args:
        name: Nombre del temporizador
        
    Returns:
        Timer: Instancia de temporizador lista para usar como context manager
    """
    return Timer(name)


def get_metric(name: str) -> Union[Counter, Gauge]:
    """
    Obtiene una métrica existente del registry o crea una nueva.
    
    Args:
        name: Nombre de la métrica a obtener
        
    Returns:
        Counter o Gauge según corresponda (crea Counter por defecto si no existe)
    """
    if name in _metrics_registry:
        return _metrics_registry[name]
    # Por defecto crea un Counter si no existe
    return Counter(name)


def get_all_metrics() -> Dict[str, Union[Counter, Gauge]]:
    """
    Retorna todas las métricas registradas.
    
    Returns:
        Dict con todas las métricas del registry
    """
    return _metrics_registry.copy()


def reset_all_metrics() -> None:
    """Reinicia todas las métricas del registry."""
    for metric in _metrics_registry.values():
        metric.reset()
    if _METRICS_ENABLED:
        logger.info("[METRIC] All metrics reset")