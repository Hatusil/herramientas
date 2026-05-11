"""
WordTree Analyzer - Análisis de árbol de palabras.

Funciones:
- analyze_wordtree_simple: lista plana de continuaciones
- analyze_wordtree: visualización en estructura de árbol
"""

import re
from typing import Dict, Any, List, Optional
from collections import Counter
from io import BytesIO

from core.utils import clean_text


# Helper functions for wordtree (SRP)

def _create_tree_node() -> Dict:
    """Factory for creating tree nodes."""
    return {'count': 0, 'children': {}}


def _build_wordtree(text: str, phrase: str, max_depth: int) -> Dict:
    """Build tree structure from text and phrase."""
    words = text.lower().split()
    phrase_words = phrase.split()
    phrase_len = len(phrase_words)

    tree = _create_tree_node()
    phrase_as_tuple = tuple(phrase_words)

    for i in range(len(words) - phrase_len):
        if tuple(words[i:i+phrase_len]) == phrase_as_tuple:
            current_level = tree
            current_level['count'] += 1

            for depth in range(max_depth):
                next_idx = i + phrase_len + depth
                if next_idx >= len(words):
                    break

                next_word = words[next_idx]

                if next_word and len(next_word) > 0:
                    if next_word not in current_level['children']:
                        current_level['children'][next_word] = _create_tree_node()
                    current_level['children'][next_word]['count'] += 1
                    current_level = current_level['children'][next_word]

    return tree


def _convert_tree_to_dict(root: Dict, phrase: str) -> Dict:
    """Convert tree structure for UI rendering."""
    tree_data = {
        'root': phrase,
        'count': root['count'],
        'children': []
    }

    sorted_children = sorted(root['children'].items(), key=lambda x: x[1]['count'], reverse=True)[:10]
    for word, data in sorted_children:
        child = {
            'word': word,
            'count': data['count'],
            'children': []
        }
        for subword, subdata in sorted(data['children'].items(), key=lambda x: x[1]['count'], reverse=True)[:5]:
            child['children'].append({
                'word': subword,
                'count': subdata['count']
            })
        tree_data['children'].append(child)

    return tree_data


def _render_wordtree_chart(tree: Dict, phrase: str) -> Optional[bytes]:
    """Generate matplotlib visualization."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 12))
        ax.set_xlim(-0.5, 10.5)
        ax.set_ylim(-0.5, max(8, len(tree['children']) * 1.0 + 1))

        root_x, root_y = 0.5, 5
        ax.text(root_x, root_y, phrase, fontsize=14, fontweight='bold',
               ha='center', va='center',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='#ADD8E6', edgecolor='black'))

        first_level_items = sorted(tree['children'].items(), key=lambda x: x[1]['count'], reverse=True)

        if not first_level_items:
            ax.text(5, 2.5, "No se encontraron relaciones repetidas",
                   fontsize=12, ha='center', style='italic', color='gray')
        else:
            first_level_items = first_level_items[:8]
            level_height = 4
            item_spacing = 10 / (len(first_level_items) + 1)

            for idx, (word, data) in enumerate(first_level_items):
                x_pos = item_spacing * (idx + 1)
                y_pos = level_height

                ax.plot([root_x, x_pos], [root_y - 0.2, y_pos + 0.2],
                       'k-', linewidth=1, alpha=0.5)

                count_text = f"({data['count']})"
                ax.text(x_pos, y_pos, f"{word}\n{count_text}",
                       fontsize=10, ha='center', va='center',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='#E8E8E8', edgecolor='gray'))

        ax.set_title(f'Árbol de Palabras: "{phrase}"', fontsize=14, fontweight='bold')
        ax.axis('off')

        img_buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(img_buffer, format='PNG', dpi=100)
        img_buffer.seek(0)
        plt.close(fig)

        return img_buffer.getvalue()
    except Exception:
        return None


def analyze_wordtree_simple(text: str, phrase: str, max_results: int = 20) -> Dict[str, Any]:
    """
    Análisis WordTree Simple - lista plana de palabras que siguen una frase raíz.

    Args:
        text: Texto de entrada
        phrase: Frase raíz a buscar
        max_results: Máximo de resultados

    Returns:
        Dict con 'success', 'continuations', 'phrase', 'error'
    """
    if not text or not text.strip():
        return {'success': False, 'error': 'Ingrese texto para analizar', 'continuations': [], 'phrase': ''}

    phrase = phrase.strip().lower()
    if not phrase:
        return {'success': False, 'error': 'Ingrese una frase para analizar', 'continuations': [], 'phrase': ''}

    max_results = max(10, min(50, max_results))

    cleaned = clean_text(text, remove_stopwords=True, exclude_words=[])
    words = cleaned.lower().split()
    phrase_words = phrase.split()
    phrase_len = len(phrase_words)

    if len(words) < phrase_len + 1:
        return {'success': False, 'error': 'Texto muy corto para analizar', 'continuations': [], 'phrase': phrase}

    phrase_as_tuple = tuple(phrase_words)
    continuations = Counter()

    for i in range(len(words) - phrase_len):
        if tuple(words[i:i+phrase_len]) == phrase_as_tuple:
            next_idx = i + phrase_len
            if next_idx < len(words):
                next_word = words[next_idx]
                if next_word and len(next_word) > 0:
                    continuations[next_word] += 1

    if not continuations:
        return {
            'success': True,
            'continuations': [],
            'phrase': phrase,
            'error': 'No se encontraron continuaciones'
        }

    sorted_continuations = sorted(continuations.items(), key=lambda x: x[1], reverse=True)[:max_results]

    result_list = [{'word': word, 'count': count} for word, count in sorted_continuations]

    return {
        'success': True,
        'continuations': result_list,
        'phrase': phrase,
        'total_found': len(continuations),
        'error': ''
    }


def analyze_wordtree(text: str, phrase: str, max_depth: int = 5) -> Dict[str, Any]:
    """
    Análisis WordTree - visualiza relaciones en estructura de árbol.

    Args:
        text: Texto de entrada
        phrase: Frase raíz a buscar
        max_depth: Profundidad máxima del árbol

    Returns:
        Dict con 'success', 'image_data', 'tree', 'error'
    """
    try:
        import matplotlib
    except ImportError:
        return {'success': False, 'error': 'matplotlib no instalado', 'image_data': None, 'tree': None}

    if not text or not text.strip():
        return {'success': False, 'error': 'Ingrese texto para analizar', 'image_data': None, 'tree': None}

    phrase = phrase.strip().lower()
    if not phrase:
        return {'success': False, 'error': 'Ingrese una frase para analizar', 'image_data': None, 'tree': None}

    cleaned = clean_text(text, remove_stopwords=True, exclude_words=[])
    words = cleaned.lower().split()
    phrase_words = phrase.split()
    phrase_len = len(phrase_words)

    if len(words) < phrase_len + 1:
        return {'success': False, 'error': 'Texto muy corto para analizar', 'image_data': None, 'tree': None}

    tree = _build_wordtree(cleaned, phrase, max_depth)

    if tree['count'] == 0 and len(tree['children']) == 0:
        return {'success': True, 'data': [], 'error': 'No se encontraron relaciones repetidas', 'tree': {}}

    tree_data = _convert_tree_to_dict(tree, phrase)

    try:
        image_data = _render_wordtree_chart(tree, phrase)
        return {
            'success': True,
            'image_data': image_data,
            'tree': tree_data,
            'error': ''
        }
    except Exception as e:
        return {'success': False, 'error': str(e), 'image_data': None, 'tree': None}