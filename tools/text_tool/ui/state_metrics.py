"""Observability metrics for Text Analyzer."""
from core.metrics import Counter

_analyses_run = Counter("text_analyzer.analyses_run")
_analyses_errors = Counter("text_analyzer.errors")


def record_analysis_start() -> None:
    _analyses_run.increment()


def record_analysis_error() -> None:
    _analyses_errors.increment()
