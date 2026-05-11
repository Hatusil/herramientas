"""
Utils - Utilidades y configuración para analizadores.

Funciones:
- check_text_size: verifica tamaño del texto
- process_in_chunks: procesa texto grande en chunks
- ANALYZER_REGISTRY: registro de analizadores disponibles
- get_analyzer, list_analyzers, get_analyzer_info
- check_dependencies, get_text_stats, validate_text
"""

import re
import logging
from typing import Dict, Any, List, Optional, Callable

from core.utils import clean_text, STOP_WORDS

logger = logging.getLogger(__name__)

# Configuración de límites
TEXT_SIZE_WARNING = 100_000
TEXT_SIZE_LIMIT = 500_000
TEXT_SIZE_CHUNK = 50_000

# Check availability
try:
    import nltk
    nltk.data.find('tokenizers/punkt')
    NLTK_AVAILABLE = True
except Exception:
    NLTK_AVAILABLE = False

try:
    from wordcloud import WordCloud
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from openpyxl import load_workbook
    XLXS_AVAILABLE = True
except ImportError:
    XLXS_AVAILABLE = False

try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def check_text_size(text: str) -> Dict[str, Any]:
    """
    Verifica el tamaño del texto y retorna información de estado.

    Returns:
        dict con is_too_large, needs_warning, size, size_mb, word_count, estimated_time
    """
    if not text:
        return {
            'is_too_large': False,
            'needs_warning': False,
            'size': 0,
            'size_mb': 0,
            'word_count': 0,
            'estimated_time': '< 1 seg'
        }

    size = len(text)
    word_count = len(text.split())
    size_mb = size / (1024 * 1024)

    if size < TEXT_SIZE_WARNING:
        time_est = '< 1 seg'
    elif size < TEXT_SIZE_WARNING * 2:
        time_est = '1-5 seg'
    elif size < TEXT_SIZE_LIMIT:
        time_est = '5-15 seg'
    else:
        time_est = '15-30 seg+'

    return {
        'is_too_large': size > TEXT_SIZE_LIMIT,
        'needs_warning': TEXT_SIZE_WARNING < size <= TEXT_SIZE_LIMIT,
        'size': size,
        'size_mb': round(size_mb, 2),
        'word_count': word_count,
        'estimated_time': time_est
    }


def process_in_chunks(text: str, analyzer_func: Callable, chunk_size: int = TEXT_SIZE_CHUNK, **kwargs) -> Dict[str, Any]:
    """
    Procesa texto grande en chunks y combina resultados.

    Args:
        text: Texto a procesar
        analyzer_func: Función de análisis a aplicar
        chunk_size: Tamaño de cada chunk
        **kwargs: Argumentos para la función de análisis

    Returns:
        dict con chunks_processed, successful, errors, results
    """
    chunks = []
    current_chunk = []
    current_size = 0

    paragraphs = re.split(r'\n\s*\n|\n{2,}', text.strip())

    for para in paragraphs:
        para_size = len(para)
        if current_size + para_size > chunk_size and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = []
            current_size = 0
        current_chunk.append(para)
        current_size += para_size

    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    combined_results = []
    errors = []

    for i, chunk in enumerate(chunks):
        try:
            result = analyzer_func(chunk, **kwargs)
            if result.get('success'):
                combined_results.append(result)
            else:
                errors.append(result.get('error', f'Chunk {i+1} falló'))
        except Exception as e:
            errors.append(f'Chunk {i+1}: {str(e)}')

    return {
        'chunks_processed': len(chunks),
        'successful': len(combined_results),
        'errors': errors,
        'results': combined_results
    }


# Registry de analizadores
ANALYZER_REGISTRY: Dict[str, Dict[str, Any]] = {}


def get_analyzer(name: str) -> Optional[Callable]:
    """Obtiene función de análisis por nombre."""
    return ANALYZER_REGISTRY.get(name, {}).get('func')


def list_analyzers() -> List[str]:
    """Lista todos los analizadores registrados."""
    return list(ANALYZER_REGISTRY.keys())


def get_analyzer_info(name: str) -> Optional[Dict[str, Any]]:
    """Obtiene metadata de un analizador."""
    return ANALYZER_REGISTRY.get(name)


def _register_analyzers():
    """Registra todos los analizadores disponibles."""
    # Importar aquí para evitar imports circulares
    from tools.text_tool.processors.frequency import analyze_frequency, analyze_ngrams, analyze_stats
    from tools.text_tool.processors.wordcloud import analyze_wordcloud
    from tools.text_tool.processors.wordtree import analyze_wordtree_simple, analyze_wordtree
    from tools.text_tool.processors.topics import analyze_topics
    from tools.text_tool.processors.correlations import analyze_correlations
    from tools.text_tool.processors.scatter import analyze_scatter
    from tools.text_tool.processors.streamgraph import analyze_streamgraph
    from tools.text_tool.processors.bubblelines import analyze_bubblelines
    from tools.text_tool.processors.mandala import analyze_mandala
    from tools.text_tool.processors.category import analyze_category, analyze_sentiment, analyze_entities, analyze_summary
    from tools.text_tool.processors.trends import analyze_trends

    global ANALYZER_REGISTRY

    ANALYZER_REGISTRY.update({
        'wordcloud': {
            'func': analyze_wordcloud,
            'requires': ['wordcloud'],
            'returns': 'image',
            'description': 'Genera nube de palabras',
            'min_words': 10
        },
        'frequency': {
            'func': analyze_frequency,
            'requires': [],
            'returns': 'text',
            'description': 'Palabras más frecuentes',
            'min_words': 5
        },
        'stats': {
            'func': analyze_stats,
            'requires': [],
            'returns': 'stats',
            'description': 'Estadísticas del corpus',
            'min_words': 1
        },
        'ngrams': {
            'func': analyze_ngrams,
            'requires': [],
            'returns': 'text',
            'description': 'N-grams (bigramas, trigramas)',
            'min_words': 3
        },
        'trends': {
            'func': analyze_trends,
            'requires': ['matplotlib'],
            'returns': 'image',
            'description': 'Tendencia de términos por secciones',
            'min_words': 50
        },
        'correlations': {
            'func': analyze_correlations,
            'requires': ['matplotlib', 'numpy'],
            'returns': 'image',
            'description': 'Co-ocurrencia de términos',
            'min_words': 20
        },
        'scatter': {
            'func': analyze_scatter,
            'requires': ['matplotlib'],
            'returns': 'image',
            'description': 'Distribución término-posición',
            'min_words': 20
        },
        'topics': {
            'func': analyze_topics,
            'requires': ['sklearn'],
            'returns': 'data',
            'description': 'LDA - Latent Dirichlet Allocation',
            'min_words': 100
        },
        'wordtree': {
            'func': analyze_wordtree,
            'requires': ['matplotlib'],
            'returns': 'image',
            'description': 'WordTree - Árbol de palabras',
            'min_words': 50
        },
        'wordtree_simple': {
            'func': analyze_wordtree_simple,
            'requires': [],
            'returns': 'text',
            'description': 'WordTree Simple - lista de continuaciones',
            'min_words': 20
        },
        'streamgraph': {
            'func': analyze_streamgraph,
            'requires': ['matplotlib'],
            'returns': 'image',
            'description': 'StreamGraph - gráfico de área apilada',
            'min_words': 50
        },
        'bubblelines': {
            'func': analyze_bubblelines,
            'requires': ['matplotlib'],
            'returns': 'image',
            'description': 'Bubblelines - líneas con burbujas',
            'min_words': 50
        },
        'mandala': {
            'func': analyze_mandala,
            'requires': ['matplotlib'],
            'returns': 'image',
            'description': 'Mandala - diagrama circular concéntrico',
            'min_words': 100
        },
        'sentiment': {
            'func': analyze_sentiment,
            'requires': [],
            'returns': 'data',
            'description': 'Análisis de sentimiento (positivo/negativo/neutral)',
            'min_words': 10
        },
        'entities': {
            'func': analyze_entities,
            'requires': [],
            'returns': 'data',
            'description': 'Reconocimiento de entidades (emails, URLs, fechas, teléfonos)',
            'min_words': 5
        },
        'category': {
            'func': analyze_category,
            'requires': [],
            'returns': 'data',
            'description': 'Clasificación de texto (informativo, opinión, técnico, narrativo)',
            'min_words': 20
        },
        'summary': {
            'func': analyze_summary,
            'requires': [],
            'returns': 'text',
            'description': 'Resumen extractivo por frecuencia de palabras',
            'min_words': 30
        }
    })


# Inicializar registry al importar
_register_analyzers()


# Funciones utilitarias adicionales

def check_dependencies(requires: List[str]) -> Dict[str, Any]:
    """Verifica si las dependencias están disponibles."""
    missing = []

    dep_map = {
        'wordcloud': WORDCLOUD_AVAILABLE,
        'matplotlib': 'matplotlib',
        'numpy': 'numpy',
        'pdfplumber': PDFPLUMBER_AVAILABLE,
        'docx': DOCX_AVAILABLE,
        'requests': REQUESTS_AVAILABLE,
        'sklearn': SKLEARN_AVAILABLE
    }

    for req in requires:
        if req in dep_map and not dep_map[req]:
            missing.append(req)

    if missing:
        return {'success': False, 'missing': missing, 'error': f'Faltan librerías: {", ".join(missing)}'}

    return {'success': True, 'missing': [], 'error': ''}


def get_text_stats(text: str) -> Dict[str, Any]:
    """Obtiene estadísticas básicas del texto sin limpiar."""
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s for s in sentences if s.strip()]

    return {
        'chars': len(text),
        'words': len(words),
        'unique': len(set(words)),
        'sentences': len(sentences),
        'avg_word_len': sum(len(w) for w in words) / len(words) if words else 0
    }


def validate_text(text: str, min_words: int = 1) -> Dict[str, Any]:
    """Valida que el texto tenga suficiente contenido."""
    if not text or not text.strip():
        return {'valid': False, 'error': 'Texto vacío', 'word_count': 0}

    words = len(text.split())

    if words < min_words:
        return {'valid': False, 'error': f'Texto muy corto (mínimo {min_words} palabras)', 'word_count': words}

    return {'valid': True, 'error': '', 'word_count': words}