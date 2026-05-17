"""Analysis handlers para text_tool - maneja ejecución de análisis."""
from typing import Any, Dict, Callable
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


def create_analysis_handlers(state, callbacks: Callable, executor: ThreadPoolExecutor, status_cb: Callable, text_changed_cb: Callable):
    """Crea handlers de análisis."""
    
    def run_all_analysis() -> None:
        """Run all text analysis methods."""
        if not state.has_text:
            status_cb("No hay texto para analizar", "orange")
            return
        
        text = state.cleaned_content or state.text_content
        from tools.text_tool.ui.analysis import run_all_analysis as run_all
        status_cb("Ejecutando análisis...", "blue")
        
        def worker():
            try:
                results = run_all(text)
                return results
            except Exception as e:
                logger.error(f"Analysis error: {e}")
                return {"error": str(e)}
        
        future = executor.submit(worker)
        # Schedule callback when done - simplified
    
    def run_stats():
        """Run statistics analysis."""
        text = state.cleaned_content or state.text_content
        if text:
            from tools.text_tool.ui.analysis import run_stats
            executor.submit(lambda: run_stats(text))
    
    def run_frequency(params: Dict[str, Any]):
        """Run frequency analysis."""
        text = state.cleaned_content or state.text_content
        if text:
            from tools.text_tool.ui.analysis import run_frequency
            top_n = params.get("top_n", 50) if params else 50
            executor.submit(lambda: run_frequency(text, top_n))
    
    return {
        "run_all": run_all_analysis,
        "stats": run_stats,
        "frequency": run_frequency,
    }