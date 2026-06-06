"""Quick analysis handlers (stats, frequency)."""
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from tools.text_tool.ui.main_ui import TextAnalyzerUI

from core.constants import COLORS
from tools.text_tool.ui.state import record_analysis_start


def run_stats(ui: TextAnalyzerUI) -> None:
    from tools.text_tool.ui.analysis import run_stats
    text = ui.state.cleaned_content or ui.state.text_content
    if not text:
        ui._on_status("No hay texto para analizar", "orange")
        return
    ui._on_status("Calculando estadísticas...", "blue")
    ui.start_progress()
    record_analysis_start()
    ui.executor.submit(lambda: _on_stats_done(ui, run_stats(text)))


def _on_stats_done(ui: TextAnalyzerUI, result: Dict) -> None:
    ui.stop_progress()
    msg, color = ("Estadísticas actualizadas", "green") if result.get("success") else (f"Error: {result.get('error', 'Unknown')}", "red")
    ui._on_status(msg, color)
    ui._on_text_changed()


def run_frequency(ui: TextAnalyzerUI, params: Dict) -> None:
    from tools.text_tool.ui.analysis import run_frequency
    text = ui.state.cleaned_content or ui.state.text_content
    if not text:
        ui._on_status("No hay texto para analizar", "orange")
        return
    ui._on_status("Calculando frecuencias...", COLORS.get("info", "blue"))
    ui.start_progress()
    record_analysis_start()
    top_n = (params.get("top_n", 50) if params else 50) if params else 50
    ui.executor.submit(lambda: _on_freq_done(ui, run_frequency(text, top_n)))


def _on_freq_done(ui: TextAnalyzerUI, result: Dict) -> None:
    ui.stop_progress()
    ui._on_text_changed()
    msg, color = ("Frecuencias actualizadas", "green") if result.get("success") else (f"Error: {result.get('error', 'Unknown')}", "red")
    ui._on_status(msg, color)
