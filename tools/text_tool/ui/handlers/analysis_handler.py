"""Analysis handlers for text_tool UI. R0: <80 lines each."""
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from tools.text_tool.ui.main_ui import TextAnalyzerUI

from tools.text_tool.ui.state import record_analysis_start, record_analysis_error

from .analysis_quick_handler import run_stats, _on_stats_done, run_frequency, _on_freq_done


def run_all_analysis(ui: "TextAnalyzerUI") -> None:
    """Run all CORE analysis via dispatch. R0: <30 lines."""
    if not ui.state.has_text:
        ui._on_status("No hay texto para analizar", "orange")
        return
    text = ui.state.cleaned_content or ui.state.text_content
    ui._is_processing = True
    ui._on_status("Ejecutando análisis...", "blue")
    ui.start_progress()
    record_analysis_start()
    ui.executor.submit(lambda: _run_and_complete(ui, text, _on_all_complete))


def _run_and_complete(ui: "TextAnalyzerUI", text: str, callback):
    try:
        from tools.text_tool.ui.analysis import run_analysis
        results = run_analysis(text)
        ui.after(0, lambda: callback(ui, results))
    except Exception as e:
        ui.after(0, lambda err=e: _on_error(ui, err))


def _on_all_complete(ui: "TextAnalyzerUI", results: Dict) -> None:
    ui.stop_progress()
    ui._is_processing = False
    errors = [k for k, v in results.items() if isinstance(v, dict) and v.get("error")]
    ok = len(results) - len(errors)
    status = f"Visualizaciones: {ok} ok, {len(errors)} fallaron" if errors else f"Visualizaciones y análisis: {ok} generados"
    color = "orange" if errors else "green"
    ui._on_status(status, color)
    ui._on_text_changed()


def _on_error(ui: "TextAnalyzerUI", msg: str) -> None:
    ui._is_processing = False
    ui.stop_progress()
    record_analysis_error()
    ui._on_status(f"Error: {msg}", "red")


def run_specific_analysis(ui: "TextAnalyzerUI", analyzers: list) -> None:
    """Ejecuta una lista específica de análisis. R0: <20 lines."""
    text = ui.state.cleaned_content or ui.state.text_content
    if not text:
        ui._on_status("No hay texto para analizar", "orange")
        return
    ui._on_status(f"Ejecutando {len(analyzers)} análisis...", "blue")
    ui.start_progress()
    record_analysis_start()
    ui.executor.submit(lambda: _run_specific_and_complete(ui, text, analyzers))


def _run_specific_and_complete(ui, text, analyzers):
    try:
        from tools.text_tool.ui.analysis import run_analysis
        results = run_analysis(text, analyzers=analyzers)
        ui.after(0, lambda: _on_specific_complete(ui, results))
    except Exception as e:
        ui.after(0, lambda err=e: _on_error(ui, err))


def _on_specific_complete(ui, results):
    ui.stop_progress()
    ui._is_processing = False
    ok = sum(1 for v in results.values() if isinstance(v, dict) and v.get("success"))
    errors = sum(1 for v in results.values() if isinstance(v, dict) and v.get("error"))
    status = f"{ok} análisis completados" + (f", {errors} errores" if errors else "")
    color = "orange" if errors else "green"
    ui._on_status(status, color)
    ui._on_text_changed()