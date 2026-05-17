"""Analysis runner - ejecuta análisis y maneja resultados."""
from typing import Any, Dict, Callable
import logging

logger = logging.getLogger(__name__)


class AnalysisRunner:
    """Maneja la ejecución de análisis y callbacks."""
    
    def __init__(self, state, callbacks: Callable, executor):
        self.state = state
        self._callbacks = callbacks
        self.executor = executor
        self._is_processing = False
    
    def run_all_analysis(self) -> None:
        """Ejecuta análisis completo."""
        if self._is_processing:
            return
        self._is_processing = True
        text = self.state.get_text()
        if not text:
            self._callbacks.on_status("⚠️ No hay texto para analizar", "orange")
            self._is_processing = False
            return
        
        self._callbacks.on_status("🔄 Análisis completo...", "blue")
        # Análisis completo - delegar a processor
    
    def run_stats(self, params: Dict[str, Any]) -> None:
        """Ejecuta análisis de estadísticas."""
        from tools.text_tool import processor
        text = self.state.get_text()
        if not text:
            self._callbacks.on_status("⚠️ No hay texto", "orange")
            return
        
        self._callbacks.on_status("📊 Calculando estadísticas...", "blue")
        try:
            result = processor.analyze_stats(text)
            self._on_stats_complete(result)
        except Exception as e:
            logger.error(f"Stats analysis error: {e}")
            self._callbacks.on_status(f"❌ Error: {e}", "red")
    
    def _on_stats_complete(self, result: Dict[str, Any]) -> None:
        """Callback cuando terminan las estadísticas."""
        if result.get('success'):
            self.state.set_stats_result(result)
            self._callbacks.on_status("✅ Estadísticas calculadas", "green")
            self._callbacks.on_text_changed()
        else:
            self._callbacks.on_status(f"❌ {result.get('error', 'Error')}", "red")
    
    def run_frequency(self, params: Dict[str, Any]) -> None:
        """Ejecuta análisis de frecuencia."""
        from tools.text_tool import processor
        text = self.state.get_text()
        if not text:
            self._callbacks.on_status("⚠️ No hay texto", "orange")
            return
        
        n = params.get('n', 20) if params else 20
        remove_stopwords = params.get('remove_stopwords', True) if params else True
        
        self._callbacks.on_status("📈 Calculando frecuencia...", "blue")
        try:
            result = processor.analyze_frequency(text, n=n, remove_stopwords=remove_stopwords)
            self._on_freq_complete(result)
        except Exception as e:
            logger.error(f"Frequency analysis error: {e}")
            self._callbacks.on_status(f"❌ Error: {e}", "red")
    
    def _on_freq_complete(self, result: Dict[str, Any]) -> None:
        """Callback cuando termina el análisis de frecuencia."""
        if result.get('success'):
            self.state.set_frequency_result(result)
            self._callbacks.on_status("✅ Frecuencia calculada", "green")
            self._callbacks.on_text_changed()
        else:
            self._callbacks.on_status(f"❌ {result.get('error', 'Error')}", "red")
    
    def stop_progress(self) -> None:
        """Detiene el procesamiento en curso."""
        self._is_processing = False
        self._callbacks.on_status("⏹️ Cancelado", "gray")