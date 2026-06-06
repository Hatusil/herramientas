"""
Mandala Analyzer - Diagrama circular concéntrico.

Funciones:
- analyze_mandala: visualización radial de términos por anillos
"""

from typing import Dict, Any, List
from collections import Counter
from io import BytesIO

from core.utils import clean_text


# Helper functions for SRP

def _get_mandala_top_terms(text: str, n_terms: int, already_cleaned: bool = False) -> List[str]:
    """Extraer los n términos más frecuentes."""
    cleaned = text if already_cleaned else clean_text(text, remove_stopwords=True)
    words = cleaned.split()
    freq = Counter(words)
    return [w for w, _ in freq.most_common(n_terms)]


def _calculate_mandala_data(words: List[str], top_words: List[str], n_rings: int) -> Dict[str, List[int]]:
    """Calcular frecuencia de términos por anillo."""
    section_size = len(words) // n_rings
    mandala_data = {word: [] for word in top_words}

    for i in range(n_rings):
        start = i * section_size
        end = start + section_size if i < n_rings - 1 else len(words)
        section_words = words[start:end]
        section_freq = Counter(section_words)

        for word in top_words:
            mandala_data[word].append(section_freq.get(word, 0))

    return mandala_data


def _generate_mandala_chart(top_words: List[str], mandala_data: Dict[str, List[int]], n_rings: int) -> bytes:
    """Generar gráfico polar tipo mandala."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})

    angles = np.linspace(0, 2 * np.pi, len(top_words), endpoint=False)
    radii = list(range(1, n_rings + 1))

    max_val = max(max(values) for values in mandala_data.values()) if mandala_data else 1
    colors = plt.cm.viridis(np.linspace(0, 1, len(top_words)))

    for ring_idx, radius in enumerate(radii):
        for term_idx, (word, values) in enumerate(mandala_data.items()):
            if ring_idx < len(values):
                val = values[ring_idx] / max_val if max_val > 0 else 0
                angle = angles[term_idx]
                size = 50 + (val * 200)
                ax.scatter(angle, radius, s=size, c=[colors[term_idx]], alpha=0.7)

                if ring_idx == n_rings - 1:
                    ax.annotate(word, (angle, radius + 0.15), fontsize=8,
                               ha='center', va='center', fontweight='bold')

    ax.set_ylim(0, n_rings + 0.5)
    ax.set_yticklabels([])
    ax.set_title('Mandala - Diagrama circular concéntrico', pad=20, fontsize=14, fontweight='bold')

    legend_elements = [plt.Line2D([0], [0], marker='o', color='w',
                                  markerfacecolor=colors[i], markersize=10,
                                  label=f'Término {i+1}') for i in range(min(5, len(top_words)))]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=8)

    img_buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(img_buffer, format='PNG', dpi=100)
    img_buffer.seek(0)
    plt.close(fig)

    return img_buffer.getvalue()


def analyze_mandala(text: str, n_terms: int = 12, n_rings: int = 3, already_cleaned: bool = False) -> Dict[str, Any]:
    """
    Análisis Mandala - diagrama circular concéntrico.

    Args:
        text: Texto de entrada
        n_terms: Número de términos (5-15)
        n_rings: Número de anillos (2-6)

    Returns:
        Dict con 'success', 'image_data', 'terms', 'rings', 'error'
    """
    try:
        import matplotlib
    except ImportError:
        return {'success': False, 'error': 'matplotlib no instalado', 'image_data': None, 'terms': [], 'rings': []}

    if n_terms < 5 or n_terms > 15:
        return {'success': False, 'error': 'n_terms debe estar entre 5 y 15', 'image_data': None}

    if n_rings < 2 or n_rings > 6:
        return {'success': False, 'error': 'n_rings debe estar entre 2 y 6', 'image_data': None}

    cleaned = text if already_cleaned else clean_text(text, remove_stopwords=True)
    words = cleaned.split()

    if len(words) < 100:
        return {'success': False, 'error': 'Texto muy corto para Mandala (mínimo 100 palabras)', 'image_data': None}

    top_words = _get_mandala_top_terms(text, n_terms, already_cleaned=already_cleaned)

    if not top_words:
        return {'success': False, 'error': 'No hay palabras suficientes', 'image_data': None}

    mandala_data = _calculate_mandala_data(words, top_words, n_rings)

    try:
        image_data = _generate_mandala_chart(top_words, mandala_data, n_rings)

        return {
            'success': True,
            'image_data': image_data,
            'terms': top_words,
            'rings': list(range(1, n_rings + 1)),
            'error': ''
        }
    except Exception as e:
        return {'success': False, 'error': f'Error al generar gráfico: {str(e)}', 'image_data': None}