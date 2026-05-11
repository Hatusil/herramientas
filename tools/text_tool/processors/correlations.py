"""
Correlations Analyzer - Análisis de correlaciones entre términos.

Funciones:
- analyze_correlations: heatmap de co-ocurrencia de términos
"""

from typing import Dict, Any
from collections import Counter
from io import BytesIO

from core.utils import clean_text


def analyze_correlations(text: str, n_terms: int = 15) -> Dict[str, Any]:
    """
    Análisis de correlaciones entre términos - heatmap de co-ocurrencia.

    Args:
        text: Texto de entrada
        n_terms: Número de términos a analizar

    Returns:
        Dict con 'success', 'image_data', 'terms', 'matrix'
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        return {'success': False, 'error': 'matplotlib no instalado'}

    cleaned = clean_text(text, remove_stopwords=True)
    words = cleaned.split()

    if len(words) < 20:
        return {'success': False, 'error': 'Texto muy corto para correlaciones'}

    freq = Counter(words)
    top_words = [w for w, _ in freq.most_common(n_terms)]

    if len(top_words) < 3:
        return {'success': False, 'error': 'No hay suficientes palabras'}

    n = len(top_words)
    cooccur = np.zeros((n, n))

    word_idx = {w: i for i, w in enumerate(top_words)}
    window = 5

    for i, word in enumerate(words):
        if word in word_idx:
            for j in range(max(0, i - window), min(len(words), i + window + 1)):
                other = words[j]
                if other in word_idx and other != word:
                    cooccur[word_idx[word]][word_idx[other]] += 1

    fig, ax = plt.subplots(figsize=(10, 8))

    im = ax.imshow(cooccur, cmap='YlOrRd', aspect='auto')

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(top_words, rotation=45, ha='right', fontsize=8)
    ax.set_yticklabels(top_words, fontsize=8)

    ax.set_title('Correlaciones entre términos')

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Co-ocurrencia')

    try:
        img_buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(img_buffer, format='PNG', dpi=100)
        img_buffer.seek(0)
        plt.close(fig)

        return {
            'success': True,
            'image_data': img_buffer.getvalue(),
            'terms': top_words,
            'matrix': cooccur.tolist()
        }
    except Exception as e:
        return {'success': False, 'error': f'Error al generar gráfico: {str(e)}'}