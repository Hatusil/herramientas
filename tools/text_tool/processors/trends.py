"""
Trends Analyzer - Análisis de tendencias de términos por secciones.

Funciones:
- analyze_trends: frecuencia de palabras en diferentes secciones del texto
"""

from typing import Dict, Any, List
from collections import Counter
from io import BytesIO

from core.utils import clean_text


# Helper functions for SRP

def _get_top_words(text: str, n_terms: int) -> List[str]:
    """Extraer las n palabras más frecuentes del texto."""
    cleaned = clean_text(text, remove_stopwords=True)
    words = cleaned.split()
    freq = Counter(words)
    return [w for w, _ in freq.most_common(n_terms)]


def _calculate_trends_data(words: List[str], top_words: List[str], n_sections: int) -> Dict[str, List[int]]:
    """Calcular frecuencia de palabras por sección."""
    section_size = len(words) // n_sections
    trends_data = {word: [] for word in top_words}

    for i in range(n_sections):
        start = i * section_size
        end = start + section_size if i < n_sections - 1 else len(words)
        section_words = words[start:end]
        section_freq = Counter(section_words)

        for word in top_words:
            trends_data[word].append(section_freq.get(word, 0))

    return trends_data


def _generate_trends_chart(top_words: List[str], trends_data: Dict[str, List[int]], n_sections: int) -> bytes:
    """Generar gráfico de tendencias."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5))

    x = range(n_sections)
    for word in top_words:
        ax.plot(x, trends_data[word], marker='o', label=word, linewidth=2)

    ax.set_xlabel('Sección del texto')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Tendencias de palabras en el texto')
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)

    img_buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(img_buffer, format='PNG', dpi=100)
    img_buffer.seek(0)

    plt.close(fig)
    return img_buffer.getvalue()


def analyze_trends(text: str, n_terms: int = 5, n_sections: int = 10) -> Dict[str, Any]:
    """
    Análisis de tendencias: frecuencia de palabras en diferentes secciones.

    Args:
        text: Texto de entrada
        n_terms: Número de términos a mostrar
        n_sections: Número de secciones del texto

    Returns:
        Dict con 'success', 'image_data', 'top_words', 'trends'
    """
    try:
        import matplotlib
    except ImportError:
        return {'success': False, 'error': 'matplotlib no instalado'}

    cleaned = clean_text(text, remove_stopwords=True)
    words = cleaned.split()

    if len(words) < n_sections:
        return {'success': False, 'error': 'Texto muy corto para tendencias'}

    top_words = _get_top_words(text, n_terms)

    if not top_words:
        return {'success': False, 'error': 'No hay palabras suficientes'}

    trends_data = _calculate_trends_data(words, top_words, n_sections)

    try:
        image_data = _generate_trends_chart(top_words, trends_data, n_sections)

        return {
            'success': True,
            'image_data': image_data,
            'top_words': top_words,
            'trends': trends_data
        }
    except Exception as e:
        return {'success': False, 'error': f'Error al generar gráfico: {str(e)}'}