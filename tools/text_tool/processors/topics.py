"""
Topics Analyzer - Análisis de tópicos usando LDA.

Funciones:
- analyze_topics: Latent Dirichlet Allocation para extraer temas del texto
"""

import re
import logging
from typing import Dict, Any, List

from core.utils import clean_text

logger = logging.getLogger(__name__)

# Check sklearn availability
try:
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def analyze_topics(
    text: str,
    n_topics: int = 5,
    max_iter: int = 10,
    remove_stopwords: bool = True,
    exclude_words: List[str] = None,
    already_cleaned: bool = False
) -> Dict[str, Any]:
    """
    Análisis de Tópicos usando LDA.

    Args:
        text: Texto de entrada
        n_topics: Número de tópicos a extraer (default: 5)
        max_iter: Máximo de iteraciones para LDA (default: 10)
        remove_stopwords: Eliminar stopwords
        exclude_words: Palabras adicionales a excluir
        already_cleaned: Si True, usar texto directamente

    Returns:
        Dict con 'success', 'data' ([{'topic_id': int, 'words': [{'word': str, 'weight': float}]}]), 'error'
    """
    if not SKLEARN_AVAILABLE:
        return {'success': False, 'error': 'scikit-learn no instalado', 'data': None}

    if not text or not text.strip():
        return {'success': False, 'error': 'Ingrese texto para analizar', 'data': None}

    # Apply cleaning filters
    if not already_cleaned:
        cleaned = clean_text(
            text,
            remove_stopwords=remove_stopwords,
            exclude_words=exclude_words
        )
    else:
        cleaned = text

    # Split into paragraphs
    paragraphs = re.split(r'\n\s*\n|\n{2,}', cleaned)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    # If not enough paragraphs, split by sentences
    if len(paragraphs) < 3:
        sentences = re.split(r'[.!?]+', cleaned)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]

        if len(sentences) >= 6:
            paragraphs = []
            for i in range(0, len(sentences), 3):
                para = ' '.join(sentences[i:i+3])
                if para:
                    paragraphs.append(para)

            if len(paragraphs) < n_topics:
                paragraphs = []
                for i in range(0, len(sentences), 2):
                    para = ' '.join(sentences[i:i+2])
                    if para:
                        paragraphs.append(para)

    if len(paragraphs) < 2:
        words = cleaned.split()
        if len(words) >= 20:
            section_size = max(10, len(words) // 5)
            paragraphs = []
            for i in range(0, len(words), section_size):
                section = ' '.join(words[i:i+section_size])
                if section:
                    paragraphs.append(section)
        else:
            return {'success': False, 'error': 'Texto insuficiente. Se requieren al menos 20 palabras.', 'data': None}

    try:
        vectorizer = CountVectorizer(
            max_df=0.95,
            min_df=1,
            stop_words='english',
            max_features=1000
        )

        doc_term_matrix = vectorizer.fit_transform(paragraphs)

        if doc_term_matrix.shape[1] == 0:
            return {'success': False, 'error': 'No hay suficientes palabras para analizar temas.', 'data': None}

        feature_names = vectorizer.get_feature_names_out()

        lda = LatentDirichletAllocation(
            n_components=min(n_topics, doc_term_matrix.shape[0]),
            max_iter=max_iter,
            learning_method='online',
            random_state=42,
            n_jobs=-1
        )

        lda.fit(doc_term_matrix)

        topics_data = []
        for topic_idx, topic in enumerate(lda.components_):
            top_word_indices = topic.argsort()[:-11:-1]

            words = []
            for word_idx in top_word_indices:
                word = feature_names[word_idx]
                weight = float(topic[word_idx])
                words.append({'word': word, 'weight': weight})

            topics_data.append({
                'topic_id': topic_idx,
                'words': words
            })

        return {
            'success': True,
            'data': topics_data,
            'error': ''
        }

    except Exception as e:
        logger.error(f"LDA error: {e}")
        return {'success': False, 'error': str(e), 'data': None}