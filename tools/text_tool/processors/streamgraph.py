"""
StreamGraph Analyzer - Gráfico de área apilada estilo río.

Funciones:
- analyze_streamgraph: evolución de términos a través del texto
"""

from typing import Dict, Any
from collections import Counter
from io import BytesIO

from core.utils import clean_text


def analyze_streamgraph(text: str, n_terms: int = 8, n_sections: int = 15) -> Dict[str, Any]:
    """
    Análisis StreamGraph - gráfico de área apilada.

    Args:
        text: Texto de entrada
        n_terms: Número de términos a mostrar (5-12)
        n_sections: Número de secciones del texto (5-20)

    Returns:
        Dict con 'success', 'image_data', 'top_words', 'data', 'error'
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        return {'success': False, 'error': 'matplotlib no instalado', 'image_data': None, 'top_words': [], 'data': {}}

    if n_terms < 5 or n_terms > 12:
        return {'success': False, 'error': 'n_terms debe estar entre 5 y 12', 'image_data': None}

    if n_sections < 5 or n_sections > 20:
        return {'success': False, 'error': 'n_sections debe estar entre 5 y 20', 'image_data': None}

    cleaned = clean_text(text, remove_stopwords=True)
    words = cleaned.split()

    if len(words) < 50:
        return {'success': False, 'error': 'Texto muy corto para StreamGraph (mínimo 50 palabras)', 'image_data': None}

    freq = Counter(words)
    top_words = [w for w, _ in freq.most_common(n_terms)]

    if not top_words:
        return {'success': False, 'error': 'No hay palabras suficientes', 'image_data': None}

    section_size = len(words) // n_sections
    stream_data = {word: [] for word in top_words}

    for i in range(n_sections):
        start = i * section_size
        end = start + section_size if i < n_sections - 1 else len(words)
        section_words = words[start:end]
        section_freq = Counter(section_words)

        for word in top_words:
            stream_data[word].append(section_freq.get(word, 0))

    try:
        fig, ax = plt.subplots(figsize=(12, 6))

        x = list(range(n_sections))
        colors = plt.cm.viridis([i / n_terms for i in range(n_terms)])

        stacks = []
        labels = []
        for word in top_words:
            stacks.append(stream_data[word])
            labels.append(word)

        ax.stackplot(x, *stacks, labels=labels, colors=colors, alpha=0.8)

        ax.set_xlabel('Sección del texto')
        ax.set_ylabel('Frecuencia')
        ax.set_title('StreamGraph - Evolución de términos a través del texto')
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3)

        img_buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(img_buffer, format='PNG', dpi=100)
        img_buffer.seek(0)
        plt.close(fig)

        return {
            'success': True,
            'image_data': img_buffer.getvalue(),
            'top_words': top_words,
            'data': stream_data,
            'error': ''
        }
    except Exception as e:
        return {'success': False, 'error': f'Error al generar gráfico: {str(e)}', 'image_data': None}