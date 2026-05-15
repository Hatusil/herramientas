"""
ProgressMixin - Mixin para barra de progreso y procesamiento async.
"""
import logging
from typing import Dict, Any, List

import customtkinter as ctk
from core.async_utils import run_in_background

logger = logging.getLogger(__name__)


class ProgressMixin:
    """Mixin que provee funcionalidad de barra de progreso y procesamiento async."""
    
    def _setup_progress_bar(self) -> None:
        """Crea una barra de progreso (llamar después de status_label)."""
        self.progress_bar = ctk.CTkProgressBar(self, mode='indeterminate')
        self.progress_bar.set(0)
    
    def start_progress(self) -> None:
        """Inicia la barra de progreso."""
        if self.progress_bar and not self._processing:
            self._processing = True
            self.progress_bar.pack(fill="x", padx=10, pady=5)
            self.progress_bar.start()
    
    def stop_progress(self) -> None:
        """Detiene la barra de progreso."""
        if self.progress_bar and self._processing:
            self._processing = False
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
    
    def set_buttons_enabled(self, enabled: bool) -> None:
        """Habilita/desabilita botones de procesar."""
        if hasattr(self, 'is_processing'):
            self.is_processing = not enabled
    
    def process_async(self, action: str, files: List[str], options: Dict[str, Any]) -> None:
        """Procesa en background con callback automático."""
        # Evitar doble click si hay is_processing
        if hasattr(self, 'is_processing') and self.is_processing:
            return
        
        # Marcar como procesando
        if hasattr(self, 'is_processing'):
            self.is_processing = True
        self.start_progress()
        
        def on_done(result: Dict[str, Any]) -> None:
            try:
                self.after(0, self._finish_processing, result)
            except Exception as e:
                logger.error(f"Error en callback: {e}")
                self.after(0, self._handle_error, str(e))
        
        # Ejecutar el proceso
        tool = getattr(self, 'tool', None)
        
        if tool and hasattr(tool, 'process_async'):
            tool.process_async(files, {'action': action, **options}, on_done)
        elif hasattr(self, 'on_process'):
            def run_sync():
                return self.on_process(action, files, options)
            
            run_in_background(run_sync, callback=on_done)
    
    def _finish_processing(self, result: Dict[str, Any]) -> None:
        """Maneja resultado en thread principal."""
        self.stop_progress()
        if hasattr(self, 'is_processing'):
            self.is_processing = False
        self._show_result(result)
    
    def _handle_error(self, error: str) -> None:
        """Maneja error en thread principal."""
        if hasattr(self, 'is_processing'):
            self.is_processing = False
        if self.status_label:
            self.status_label.configure(text=f"Error: {error}", text_color="red")
    
    def _show_result(self, result: Dict[str, Any]) -> None:
        """Muestra el resultado."""
        if self.status_label:
            if result.get('success'):
                msg = result.get('message', 'Completado')
                if not msg or msg.strip() == '':
                    msg = 'Completado'
                self.status_label.configure(
                    text=msg,
                    text_color="green"
                )
            else:
                error_msg = result.get('error') or result.get('message') or 'Error'
                self.status_label.configure(
                    text=f"❌ {error_msg}",
                    text_color="red"
                )
    
    def set_processing_state(self, is_processing: bool, message: str = "") -> None:
        """Sets processing state and updates all relevant UI feedback."""
        self.is_processing = is_processing
        self._processing = is_processing
        if self.status_label:
            if is_processing and message:
                self.status_label.configure(text=message, text_color="blue")
            elif is_processing:
                self.status_label.configure(text="Procesando...", text_color="blue")