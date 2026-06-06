"""Tests for analysis dispatch and caching."""
import time
import pytest
from tools.text_tool.ui.analysis import (
    AnalysisCache,
    run_analysis,
    clear_cache,
    CORE_ANALYZERS,
    ALL_ANALYZERS,
)

SAMPLE_TEXT = "el gato y el perro juegan en el jardin"
SHORT_TEXT = "hola mundo"


@pytest.fixture(autouse=True)
def reset_cache():
    clear_cache()
    yield
    clear_cache()


class TestAnalysisCache:
    def test_miss_returns_none(self):
        cache = AnalysisCache()
        assert cache.get("some text", "stats") is None

    def test_hit_returns_stored_value(self):
        cache = AnalysisCache()
        cache.set("test", "stats", {"success": True, "total_words": 5})
        result = cache.get("test", "stats")
        assert result == {"success": True, "total_words": 5}

    def test_miss_after_different_analyzer(self):
        cache = AnalysisCache()
        cache.set("test", "stats", {"success": True})
        assert cache.get("test", "frequency") is None

    def test_invalidate_text_removes_all_for_text(self):
        cache = AnalysisCache()
        cache.set("test", "stats", {"a": 1})
        cache.set("test", "frequency", {"b": 2})
        cache.invalidate_text("test")
        assert cache.size == 0

    def test_invalidate_text_keeps_other_texts(self):
        cache = AnalysisCache()
        cache.set("text_a", "stats", {"a": 1})
        cache.set("text_b", "stats", {"b": 2})
        cache.invalidate_text("text_a")
        assert cache.get("text_b", "stats") == {"b": 2}
        assert cache.size == 1

    def test_clear_removes_all(self):
        cache = AnalysisCache()
        cache.set("a", "stats", {"x": 1})
        cache.set("b", "frequency", {"y": 2})
        cache.clear()
        assert cache.size == 0

    def test_eviction_removes_oldest_texts(self):
        cache = AnalysisCache(max_texts=2)
        cache.set("text_1", "stats", {"a": 1})
        cache.set("text_2", "stats", {"b": 2})
        cache.set("text_3", "stats", {"c": 3})
        assert cache.size <= 2
        assert cache.get("text_1", "stats") is None

    def test_get_moves_to_end_lru(self):
        cache = AnalysisCache(max_texts=2)
        cache.set("text_a", "stats", {"a": 1})
        cache.set("text_b", "stats", {"b": 2})
        cache.get("text_a", "stats")
        cache.set("text_c", "stats", {"c": 3})
        assert cache.get("text_a", "stats") is not None
        assert cache.get("text_b", "stats") is None


class TestRunAnalysisDispatch:
    def test_default_runs_core_analyzers(self):
        result = run_analysis(SAMPLE_TEXT)
        for name in CORE_ANALYZERS:
            assert name in result

    def test_selective_only_runs_requested(self):
        result = run_analysis(SAMPLE_TEXT, analyzers=["stats"])
        assert "stats" in result
        assert "frequency" not in result

    def test_unknown_analyzer_returns_error(self):
        result = run_analysis(SAMPLE_TEXT, analyzers=["nonexistent"])
        assert "nonexistent" in result
        assert "error" in result["nonexistent"]

    def test_empty_analyzer_list_returns_empty(self):
        result = run_analysis(SAMPLE_TEXT, analyzers=[])
        assert result == {}

    def test_all_analyzers_runs_everything(self):
        result = run_analysis(SHORT_TEXT, analyzers=ALL_ANALYZERS)
        from tools.text_tool.processors.utils import ANALYZER_REGISTRY
        for name in ANALYZER_REGISTRY:
            assert name in result

    def test_cached_hit_returns_same_object(self):
        first = run_analysis(SAMPLE_TEXT, analyzers=["stats"])
        second = run_analysis(SAMPLE_TEXT, analyzers=["stats"])
        assert first["stats"] == second["stats"]

    def test_cached_skip_with_use_cache_false(self):
        result = run_analysis(SAMPLE_TEXT, analyzers=["stats"], use_cache=False)
        assert "stats" in result

    def test_core_equivalence_with_default(self):
        default = run_analysis(SAMPLE_TEXT)
        explicit = run_analysis(SAMPLE_TEXT, analyzers=None)
        for k in CORE_ANALYZERS:
            assert k in default and k in explicit
