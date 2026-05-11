"""
Scatter Analyzer - Scatter plot de términos basado en frecuencia y posición.

Funciones:
- analyze_scatter: distribución término-posición en el texto
"""

from typing import Dict, Any
from collections import Counter
from io import BytesIO

from core.utils import clean_text


def analyze_scatter(text: str, n_terms: int = 30) -> Dict[str, Any]:
    """
    Scatter plot de términos basado en frecuencia y posición.

    Args:
        text: Texto de entrada
        n_terms: Número de términos a mostrar

    Returns:
        Dict con 'success', 'image_data', 'data'
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        return {'success': False, 'error': 'matplotlib no instalado'}

    cleaned = clean_text(text, remove_stopwords=True)
    words = cleaned.split()

    if len(words) < 20:
        return {'success': False, 'error': 'Texto muy corto'}

    freq = Counter(words)
    position_sum = {}
    position_count = {}

    for i, word in enumerate(words):
        if word not in position_sum:
            position_sum[word] = 0
            position_count[word] = 0
        position_sum[word] += i
        position_count[word] += 1

    data = []
    for word in freq:
        if position_count[word] >= 2:
            avg_position = position_sum[word] / position_count[word]
            normalized_pos = avg_position / len(words)
            data.append({
                'word': word,
                'frequency': freq[word],
                'avg_position': normalized_pos
            })

    if not data:
        return {'success': False, 'error': 'Datos insuficientes'}

    data = sorted(data, key=lambda x: x['frequency'], reverse=True)[:n_terms]

    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        freqs = [d['frequency'] for d in data]
        positions = [d['avg_position'] for d in data]
        labels = [d['word'] for d in data]

        sizes = [f * 20 + 50 for f in freqs]

        scatter = ax.scatter(positions, freqs, s=sizes, alpha=0.6, c=freqs, cmap='viridis')

        for i, label in enumerate(labels):
            ax.annotate(label, (positions[i], freqs[i]), fontsize=8, alpha=0.8)

        ax.set_xlabel('Posición promedio en el texto (inicio → fin)')
        ax.set_ylabel('Frecuencia')
        ax.set_title('Distribución de términos en el texto')
        ax.grid(True, alpha=0.3)

        img_buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(img_buffer, format='PNG', dpi=100)
        img_buffer.seek(0)
        plt.close(fig)

        return {
            'success': True,
            'image_data': img_buffer.getvalue(),
            'data': data
        }
    except Exception as e:
        return {'success': False, 'error': f'Error al generar gráfico: {str(e)}'}