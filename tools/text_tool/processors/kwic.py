"""KWIC concordance analyzer."""

import re
from typing import List, Dict, Any


def analyze_kwic(
    text: str,
    keyword: str,
    context: int = 5,
    max_results: int = 20,
) -> Dict[str, Any]:
    """Busca keyword in context y devuelve concordancias."""
    if not text or not keyword:
        return {"success": False, "error": "Texto o keyword vacío"}

    words = text.split()
    keyword_lower = keyword.lower()
    concordances: List[Dict[str, str]] = []

    for i, word in enumerate(words):
        if word.lower().strip(".,!?;:\"'()[]{}") == keyword_lower:
            start = max(0, i - context)
            end = min(len(words), i + context + 1)
            before = " ".join(words[start:i])
            after = " ".join(words[i + 1:end])
            concordances.append({
                "before": before,
                "keyword": word,
                "after": after,
            })
            if len(concordances) >= max_results:
                break

    return {"success": True, "data": concordances}
