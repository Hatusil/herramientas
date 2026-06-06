"""
async_utils.py - Utilidades para ejecución en background
"""
import logging
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)


# Threadpool global - 4 workers para no saturar sistema
_executor = ThreadPoolExecutor(max_workers=4)


def _make_done_callback(user_cb: Optional[Callable[[Any], None]]) -> Callable[[Future], None]:
    """Build a done-callback for run_in_background. Logs exceptions, invokes
    the user callback exactly once with the result (or skips on failure).

    Extracted from an inline lambda to:
      - call f.result() only once
      - catch and log exceptions instead of letting concurrent.futures log
        them at ERROR with full traceback while the user callback is never
        notified
      - keep the UI callback contract: only invoked on success
    """
    def _done(f: Future) -> None:
        try:
            result = f.result()
        except Exception:
            logger.exception("run_in_background worker raised")
            return
        logger.debug("run_in_background done: result=%r", result)
        if user_cb is not None:
            user_cb(result)
    return _done


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
    logger.debug("run_in_background: func=%r, args=%r, kwargs=%r, callback=%r",
                 func, args, kwargs, callback)
    future = _executor.submit(func, *args, **kwargs)
    if callback is not None:
        future.add_done_callback(_make_done_callback(callback))

    return future


def get_executor() -> ThreadPoolExecutor:
    """Retorna el executor global"""
    return _executor
