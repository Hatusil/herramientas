"""
async_utils.py - Utilidades para ejecución en background
"""
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any, Optional


# Threadpool global - 4 workers para no saturar sistema
_executor = ThreadPoolExecutor(max_workers=4)


def run_in_background(
    func: Callable, 
    *args, 
    callback: Optional[Callable] = None,
    **kwargs
) -> Future:
    """
    Ejecuta función en threadpool sin bloquear UI.
    
    Args:
        func: Función a ejecutar (ej: process)
        *args: Argumentos para func
        callback: Función(result) a ejecutar al terminar (opcional)
        **kwargs: kwargs para func
    
    Returns:
        Future - puede usarse para cancelar o preguntar estado
    """
    future = _executor.submit(func, *args, **kwargs)
    
    if callback:
        # Cuando termina, llama al callback con el resultado
        future.add_done_callback(lambda f: callback(f.result()))
    
    return future


def get_executor() -> ThreadPoolExecutor:
    """Retorna el executor global"""
    return _executor