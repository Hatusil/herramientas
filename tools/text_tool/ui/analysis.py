"""Analysis methods for TextAnalyzerUI."""
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def run_all_analysis(text: str) -> Dict[str, Any]:
    """Run all text analysis methods."""
    from tools.text_tool.processor import (
        analyze_stats, analyze_frequency, analyze_ngrams, analyze_trends
    )
    analyses = [
        ("stats", lambda: analyze_stats(text)),
        ("frequency", lambda: analyze_frequency(text)),
        ("ngrams", lambda: analyze_ngrams(text, n=2)),
        ("trends", lambda: analyze_trends(text))
    ]
    results = {}
    for name, fn in analyses:
        try:
            results[name] = fn()
        except Exception as e:
            results[name] = {"error": str(e)}
    return results


def run_stats(text: str) -> Dict[str, Any]:
    """Run statistics analysis."""
    from tools.text_tool.processor import analyze_stats
    return analyze_stats(text)


def run_frequency(text: str, top_n: int = 50) -> Dict[str, Any]:
    """Run frequency analysis."""
    from tools.text_tool.processor import analyze_frequency
    return analyze_frequency(text, n=top_n)