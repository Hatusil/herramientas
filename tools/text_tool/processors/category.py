"""
Category Analyzer - Clasificación de texto, sentimiento, entidades y resumen.

Funciones:
- analyze_category: clasificación en categorías (informativo, opinión, técnico, narrativo)
- analyze_sentiment: análisis de sentimiento (positivo/negativo/neutral)
- analyze_entities: reconocimiento de entidades (emails, URLs, fechas, teléfonos)
- analyze_summary: resumen extractivo por frecuencia de palabras
"""

import re
from typing import Dict, Any, List
from collections import Counter

from core.utils import clean_text


def analyze_sentiment(text: str, **kwargs) -> Dict[str, Any]:
    """
    Análisis de sentimiento usando heurísticas basadas en palabras clave.

    Args:
        text: Texto de entrada
        **kwargs: Argumentos adicionales (ignorado)

    Returns:
        Dict con 'success', 'polarity', 'subjectivity', 'label', 'description'
    """
    if not text or not text.strip():
        return {'success': False, 'error': 'Texto vacío'}

    words = text.lower().split()
    word_count = len(words)

    positive_words = {
        'bien', 'bueno', 'excelente', 'maravilloso', 'fantástico', 'genial',
        'perfecto', 'mejor', 'increíble', 'magnífico', 'grandioso', 'excepcional',
        'positivo', 'feliz', 'alegre', 'satisfecho', 'agradecido', 'éxito',
        'logro', 'progreso', 'avance', 'beneficio', 'ventaja', 'apoyo',
        'recomiendo', 'encanta', 'gusta', 'amor', 'felicidad', 'esperanza',
        'buena', 'buenas', 'mejorar', 'mejora', 'crecimiento', 'oportunidad'
    }

    negative_words = {
        'mal', 'malo', 'terrible', 'horrible', 'pésimo', 'peor', 'desastre',
        'fallo', 'error', 'problema', 'dificultad', 'fracaso', 'pérdida',
        'negativo', 'triste', 'descontento', 'insatisfecho', 'frustrado',
        'enojado', 'molesto', 'irritado', 'preocupado', 'ansioso', 'miedo',
        'peligro', 'amenaza', 'riesgo', 'crisis', 'conflicto', 'descenso',
        'caída', 'deterioro', 'empeorar', 'peorar', 'baja', 'fallar', 'fallo'
    }

    positive_count = sum(1 for w in words if w in positive_words)
    negative_count = sum(1 for w in words if w in negative_words)

    if word_count > 0:
        pos_ratio = positive_count / word_count
        neg_ratio = negative_count / word_count
        polarity = (pos_ratio - neg_ratio) * 2
        polarity = max(-1, min(1, polarity))

        subjectivity = (pos_ratio + neg_ratio)
        subjectivity = min(1, subjectivity)
    else:
        polarity = 0
        subjectivity = 0

    if polarity > 0.1:
        label = 'positive'
        description = 'El texto expresa opiniones positivas o favorables'
    elif polarity < -0.1:
        label = 'negative'
        description = 'El texto expresa opiniones negativas o desfavorables'
    else:
        label = 'neutral'
        description = 'El texto es mayormente objetivo o neutral'

    return {
        'success': True,
        'polarity': round(polarity, 3),
        'subjectivity': round(subjectivity, 3),
        'label': label,
        'description': description
    }


def analyze_entities(text: str, **kwargs) -> Dict[str, Any]:
    """
    Named Entity Recognition simple usando regex.

    Detecta: emails, URLs, fechas, números de teléfono, nombres propios.

    Args:
        text: Texto de entrada
        **kwargs: Argumentos adicionales (ignorado)

    Returns:
        Dict con 'success', 'entities' (list de dicts con type, value, count)
    """
    if not text or not text.strip():
        return {'success': False, 'error': 'Texto vacío'}

    entities = []

    # Emails
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        entities.append({'type': 'email', 'value': emails[0], 'count': len(emails)})

    # URLs
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text, re.IGNORECASE)
    if urls:
        entities.append({'type': 'url', 'value': urls[0], 'count': len(urls)})

    # Dates
    date_patterns = [
        r'\d{1,2}/\d{1,2}/\d{2,4}',
        r'\d{1,2}-\d{1,2}-\d{2,4}',
        r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}',
        r'\d{4}-\d{2}-\d{2}',
        r'\d{1,2}\s+\w+\s+\d{4}'
    ]
    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, text, re.IGNORECASE))
    if dates:
        entities.append({'type': 'date', 'value': dates[0], 'count': len(dates)})

    # Phone
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}'
    phones = re.findall(phone_pattern, text)
    phones = [p for p in phones if len(re.sub(r'\D', '', p)) >= 7]
    if phones:
        entities.append({'type': 'phone', 'value': phones[0], 'count': len(phones)})

    # Proper nouns
    proper_noun_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b'
    proper_nouns = re.findall(proper_noun_pattern, text)
    if proper_nouns:
        noun_counts = Counter(proper_nouns)
        for noun, count in noun_counts.most_common(5):
            if count >= 2:
                entities.append({'type': 'proper_noun', 'value': noun, 'count': count})

    return {
        'success': True,
        'entities': entities
    }


def analyze_category(text: str, **kwargs) -> Dict[str, Any]:
    """
    Clasificación simple de texto en categorías básicas.

    Categorías: 'informativo', 'opinión', 'técnico', 'narrativo'

    Args:
        text: Texto de entrada
        **kwargs: Argumentos adicionales (ignorado)

    Returns:
        Dict con 'success', 'category', 'confidence', 'features'
    """
    if not text or not text.strip():
        return {'success': False, 'error': 'Texto vacío'}

    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s for s in sentences if s.strip()]

    word_count = len(words)
    sentence_count = len(sentences)

    avg_sentence_len = word_count / sentence_count if sentence_count > 0 else 0

    numbers = re.findall(r'\d+', text)
    has_numbers = len(numbers) > 0

    code_patterns = [
        r'def\s+\w+\s*\(',
        r'class\s+\w+',
        r'function\s+\w+',
        r'import\s+\w+',
        r'var\s+\w+\s*=',
        r'let\s+\w+\s*=',
        r'const\s+\w+\s*='
    ]
    has_code = any(re.search(p, text) for p in code_patterns)

    opinion_markers = [
        'pienso', 'creo', 'opinión', 'parece', 'considero', 'mejor',
        'peor', 'debería', 'deberian', 'recomiendo', 'sugiero',
        'I think', 'I believe', 'in my opinion', 'probably', 'maybe'
    ]
    opinion_count = sum(1 for m in opinion_markers if m in text.lower())

    narrative_markers = [
        'entonces', 'después', 'luego', 'primero', 'finalmente',
        'había', 'era', 'sucedió', 'llegó', 'fue cuando',
        'then', 'after', 'finally', 'suddenly', 'happened'
    ]
    narrative_count = sum(1 for m in narrative_markers if m in text.lower())

    scores = {}

    scores['informativo'] = 0
    if 10 < avg_sentence_len < 30:
        scores['informativo'] += 0.3
    if word_count > 100:
        scores['informativo'] += 0.2

    scores['opinión'] = 0
    if opinion_count >= 2:
        scores['opinión'] += 0.5
    if avg_sentence_len < 20:
        scores['opinión'] += 0.2

    scores['técnico'] = 0
    if has_code:
        scores['técnico'] += 0.6
    if has_numbers and len(numbers) > 5:
        scores['técnico'] += 0.3
    if any(w in text.lower() for w in ['sistema', 'proceso', 'método', 'algoritmo', 'configuración', 'installation', 'setup', 'configuration']):
        scores['técnico'] += 0.2

    scores['narrativo'] = 0
    if narrative_count >= 2:
        scores['narrativo'] += 0.5
    if avg_sentence_len > 15:
        scores['narrativo'] += 0.2

    category = max(scores, key=scores.get)
    confidence = scores[category] / sum(scores.values()) if sum(scores.values()) > 0 else 0
    confidence = min(1, confidence + 0.3)

    return {
        'success': True,
        'category': category,
        'confidence': round(confidence, 2),
        'features': {
            'avg_sentence_length': round(avg_sentence_len, 1),
            'has_numbers': has_numbers,
            'has_code': has_code,
            'opinion_markers': opinion_count,
            'narrative_markers': narrative_count,
            'sentence_count': sentence_count,
            'word_count': word_count
        }
    }


def analyze_summary(text: str, n_sentences: int = 5, **kwargs) -> Dict[str, Any]:
    """
    Resumen extractivo basado en frecuencia de palabras.

    Args:
        text: Texto de entrada
        n_sentences: Número de oraciones en el resumen
        **kwargs: Argumentos adicionales (ignorado)

    Returns:
        Dict con 'success', 'summary', 'original_sentences', 'summary_sentences'
    """
    if not text or not text.strip():
        return {'success': False, 'error': 'Texto vacío'}

    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]

    if len(sentences) < 2:
        return {
            'success': True,
            'summary': text,
            'original_sentences': len(sentences),
            'summary_sentences': len(sentences)
        }

    cleaned = clean_text(text, remove_stopwords=True)
    word_freq = Counter(cleaned.split())

    total_words = sum(word_freq.values())
    if total_words > 0:
        max_freq = max(word_freq.values())
        for word in word_freq:
            word_freq[word] = word_freq[word] / max_freq

    sentence_scores = []
    for i, sentence in enumerate(sentences):
        score = 0
        sentence_clean = clean_text(sentence, remove_stopwords=True)
        sentence_words = sentence_clean.split()

        for word in sentence_words:
            if word in word_freq:
                score += word_freq[word]

        score = score / len(sentence_words) if sentence_words else 0
        sentence_scores.append((i, sentence, score))

    sentence_scores.sort(key=lambda x: x[2], reverse=True)

    n = min(n_sentences, len(sentences))
    selected_indices = [x[0] for x in sentence_scores[:n]]
    selected_indices.sort()

    summary_sentences = [sentences[i] for i in selected_indices]
    summary = '. '.join(summary_sentences)
    if summary and not summary.endswith('.'):
        summary += '.'

    return {
        'success': True,
        'summary': summary,
        'original_sentences': len(sentences),
        'summary_sentences': len(summary_sentences)
    }