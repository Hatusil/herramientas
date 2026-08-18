import re
import logging
from typing import Dict, Any, List, Callable

from core.utils import clean_text

logger = logging.getLogger(__name__)

TEXT_SIZE_WARNING = 100_000
TEXT_SIZE_LIMIT = 500_000
TEXT_SIZE_CHUNK = 50_000

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

from tools.text_tool.processors._registry import (
    ANALYZER_REGISTRY,
    get_analyzer,
    list_analyzers,
    get_analyzer_info,
)


def check_text_size(text: str) -> Dict[str, Any]:
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


def check_dependencies(requires: List[str]) -> Dict[str, Any]:
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
    if not text or not text.strip():
        return {'valid': False, 'error': 'Texto vacío', 'word_count': 0}

    words = len(text.split())

    if words < min_words:
        return {'valid': False, 'error': f'Texto muy corto (mínimo {min_words} palabras)', 'word_count': words}

    return {'valid': True, 'error': '', 'word_count': words}
