"""
Bubblelines Analyzer - Líneas con burbujas superpuestas.

Funciones:
- analyze_bubblelines: distribución de términos a lo largo del documento
"""

from typing import Dict, Any, List
from collections import Counter
from io import BytesIO

from core.utils import clean_text


def analyze_bubblelines(
    text: str,
    terms_list: List[str] = None,
    show_bubbles: bool = True,
    bubble_scale: float = 1.5
) -> Dict[str, Any]:
    """
    Análisis Bubblelines - líneas con burbujas.

    Args:
        text: Texto de entrada
        terms_list: Lista de términos a comparar
        show_bubbles: Si mostrar burbujas
        bubble_scale: Escala del tamaño de burbujas

    Returns:
        Dict con 'success', 'image_data', 'terms', 'data', 'error'
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        return {'success': False, 'error': 'matplotlib no instalado', 'image_data': None, 'terms': [], 'data': {}}

    if terms_list is None:
        terms_list = []

    if bubble_scale < 0.5 or bubble_scale > 3.0:
        return {'success': False, 'error': 'bubble_scale debe estar entre 0.5 y 3.0', 'image_data': None}

    cleaned = clean_text(text, remove_stopwords=True)
    words = cleaned.split()

    if len(words) < 50:
        return {'success': False, 'error': 'Texto muy corto para Bubblelines (mínimo 50 palabras)', 'image_data': None}

    valid_terms = []
    word_counter = Counter(words)
    for term in terms_list:
        term_clean = term.strip().lower()
        if term_clean and word_counter.get(term_clean, 0) > 0:
            valid_terms.append(term_clean)

    if not valid_terms:
        return {'success': False, 'error': 'No se encontraron los términos especificados en el texto', 'image_data': None}

    n_sections = 15
    section_size = len(words) // n_sections
    bubblelines_data = {term: {'line': [], 'bubbles': []} for term in valid_terms}

    for i in range(n_sections):
        start = i * section_size
        end = start + section_size if i < n_sections - 1 else len(words)
        section_words = words[start:end]
        section_freq = Counter(section_words)

        for term in valid_terms:
            count = section_freq.get(term, 0)
            bubblelines_data[term]['line'].append(count)

            if show_bubbles:
                positions = [j for j, w in enumerate(section_words) if w == term]
                scaled_positions = [(i + (p / section_size)) for p in positions]
                bubblelines_data[term]['bubbles'].extend(scaled_positions)

    try:
        fig, ax = plt.subplots(figsize=(12, 6))

        colors = plt.cm.tab10([i / len(valid_terms) for i in range(len(valid_terms))])

        for idx, term in enumerate(valid_terms):
            ax.plot(range(n_sections), bubblelines_data[term]['line'],
                   marker='o', label=term, linewidth=2, color=colors[idx])

            if show_bubbles and bubblelines_data[term]['bubbles']:
                total_freq = Counter(words).get(term, 1)
                bubble_sizes = [50 + (total_freq * 5) * bubble_scale for _ in bubblelines_data[term]['bubbles']]
                ax.scatter(bubblelines_data[term]['bubbles'],
                          [bubblelines_data[term]['line'][int(p)] for p in bubblelines_data[term]['bubbles']],
                          s=bubble_sizes, alpha=0.5, color=colors[idx])

        ax.set_xlabel('Sección del texto')
        ax.set_ylabel('Frecuencia')
        ax.set_title('Bubblelines - Distribución de términos')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)

        img_buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(img_buffer, format='PNG', dpi=100)
        img_buffer.seek(0)
        plt.close(fig)

        return {
            'success': True,
            'image_data': img_buffer.getvalue(),
            'terms': valid_terms,
            'data': bubblelines_data,
            'error': ''
        }
    except Exception as e:
        return {'success': False, 'error': f'Error al generar gráfico: {str(e)}', 'image_data': None}