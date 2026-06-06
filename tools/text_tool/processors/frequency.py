"""
Frequency Analyzer - Análisis de frecuencia, n-grams y estadísticas.

Funciones:
- analyze_frequency: palabras más frecuentes
- analyze_ngrams: bigramas, trigramas
- analyze_stats: estadísticas del corpus
"""

import re
from typing import Dict, Any, List
from collections import Counter

from core.utils import clean_text
from core.metrics import Timer, Counter as MetCounter, get_metric

# Métricas globales para text_tool (A12)
_wordcloud_duration = get_metric('text_wordcloud_duration')
_wordcloud_count = get_metric('text_wordcloud_count')
_frequency_duration = get_metric('text_frequency_duration')
_frequency_count = get_metric('text_frequency_count')
_stats_duration = get_metric('text_stats_duration')
_stats_count = get_metric('text_stats_count')
_words_processed = get_metric('text_words_processed')

# Optional: NLTK check
try:
    import nltk
    nltk.data.find('tokenizers/punkt')
    NLTK_AVAILABLE = True
except Exception:
    NLTK_AVAILABLE = False


def analyze_frequency(
    text: str,
    n: int = 20,
    remove_stopwords: bool = True,
    exclude_words: List[str] = None,
    already_cleaned: bool = False
) -> Dict[str, Any]:
    """Analiza frecuencia de palabras. A12: métricas de duración y conteo."""
    with Timer('frequency_analysis'):
        cleaned = text if already_cleaned else clean_text(
            text, remove_stopwords=remove_stopwords, exclude_words=exclude_words
        )
        words = cleaned.split()
        _words_processed.increment(len(words))

        freq = {}
        for word in words:
            freq[word] = freq.get(word, 0) + 1

        sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:n]
        _frequency_count.increment()

        return {
            'success': True,
            'frequencies': dict(sorted_freq),
            'total_words': len(words),
            'unique_words': len(freq)
        }


def analyze_ngrams(text: str, n: int = 2, top_k: int = 20, already_cleaned: bool = False) -> Dict[str, Any]:
    """
    Analiza n-grams (sin dependencia de nltk).

    Args:
        text: Texto de entrada
        n: Tamaño del n-gram (2=bigramas, 3=trigramas)
        top_k: Número de n-grams más frecuentes

    Returns:
        Dict con 'success', 'ngrams', 'n', 'total'
    """
    cleaned = text if already_cleaned else clean_text(text, remove_stopwords=True)
    words = cleaned.split()

    if len(words) < n:
        return {'success': False, 'error': 'Texto muy corto para n-grams'}

    ngram_list = []
    for i in range(len(words) - n + 1):
        ngram_list.append(tuple(words[i:i+n]))

    freq = Counter(ngram_list)
    sorted_ngrams = freq.most_common(top_k)

    return {
        'success': True,
        'ngrams': {(' '.join(ng)): count for ng, count in sorted_ngrams},
        'n': n,
        'total': len(ngram_list)
    }


def analyze_stats(text: str) -> Dict[str, Any]:
    """Estadísticas del corpus. A12: métricas de duración y conteo."""
    with Timer('stats_analysis'):
        words = text.split()
        _words_processed.increment(len(words))
        _stats_count.increment()

        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]

        total_chars = len(text)
        total_words = len(words)
        unique_words = len(set(words))
        avg_word_len = sum(len(w) for w in words) / total_words if total_words > 0 else 0
        avg_sentence_len = total_words / len(sentences) if sentences else 0

        return {
            'success': True,
            'total_chars': total_chars,
            'total_words': total_words,
            'unique_words': unique_words,
            'total_sentences': len(sentences),
            'avg_word_length': round(avg_word_len, 2),
            'avg_sentence_length': round(avg_sentence_len, 2),
            'type_token_ratio': round(unique_words / total_words, 4) if total_words > 0 else 0
        }