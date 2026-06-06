"""Analysis methods for TextAnalyzerUI with selective dispatch and caching."""
import hashlib
import logging
import threading
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

CORE_ANALYZERS = ["stats", "frequency", "ngrams", "trends"]


class _AllAnalyzersSentinel:
    pass

ALL_ANALYZERS = _AllAnalyzersSentinel()  # sentinel meaning "all registered analyzers"


@dataclass
class AnalysisCache:
    _store: OrderedDict = field(default_factory=OrderedDict)
    _lock: threading.Lock = field(default_factory=threading.Lock)
    max_texts: int = 100

    def _text_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _make_key(self, text: str, analyzer: str) -> str:
        return f"{self._text_hash(text)}:{analyzer}"

    def get(self, text: str, analyzer: str) -> Optional[Dict[str, Any]]:
        key = self._make_key(text, analyzer)
        with self._lock:
            if key in self._store:
                self._store.move_to_end(key)
                return self._store[key]
            return None

    def set(self, text: str, analyzer: str, result: Dict[str, Any]) -> None:
        key = self._make_key(text, analyzer)
        with self._lock:
            self._store[key] = result
            self._store.move_to_end(key)
            self._evict_if_needed()

    def _evict_if_needed(self) -> None:
        unique_texts = len({k.split(":")[0] for k in self._store})
        while unique_texts > self.max_texts and self._store:
            self._store.popitem(last=False)
            unique_texts = len({k.split(":")[0] for k in self._store})

    def invalidate_text(self, text: str) -> None:
        prefix = f"{self._text_hash(text)}:"
        with self._lock:
            self._store = OrderedDict(
                (k, v) for k, v in self._store.items() if not k.startswith(prefix)
            )

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._store)


_analysis_cache = AnalysisCache()


def run_analysis(
    text: str,
    analyzers: Optional[List[str]] = None,
    use_cache: bool = True,
) -> Dict[str, Any]:
    from tools.text_tool.processors.utils import ANALYZER_REGISTRY

    if analyzers is None:
        names = CORE_ANALYZERS
    elif analyzers is ALL_ANALYZERS:
        names = list(ANALYZER_REGISTRY.keys())
    else:
        names = list(analyzers)

    cache = _analysis_cache if use_cache else None
    results: Dict[str, Any] = {}

    for name in names:
        if cache:
            cached = cache.get(text, name)
            if cached is not None:
                results[name] = cached
                continue

        info = ANALYZER_REGISTRY.get(name)
        if info is None:
            results[name] = {"error": f"Unknown analyzer: {name}"}
            continue

        try:
            result = info["func"](text)
            results[name] = result
            if cache:
                cache.set(text, name, result)
        except Exception as e:
            results[name] = {"error": str(e)}

    return results


def clear_cache() -> None:
    _analysis_cache.clear()


def run_all_analysis(text: str) -> Dict[str, Any]:
    return run_analysis(text, analyzers=None, use_cache=True)


def run_stats(text: str) -> Dict[str, Any]:
    return run_analysis(text, analyzers=["stats"], use_cache=True).get("stats", {})


def run_frequency(text: str, top_n: int = 50) -> Dict[str, Any]:
    from tools.text_tool.processor import analyze_frequency
    result = analyze_frequency(text, n=top_n)
    _analysis_cache.set(text, "frequency", result)
    return result
