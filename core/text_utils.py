"""
Utilidades de procesamiento de texto.
Cumple con máxima A1 (una sola responsabilidad).
"""
import re
from typing import List, Optional


# ============================================================================
# STOP WORDS - Palabras comunes a filtrar en procesamiento de texto
# ============================================================================
STOP_WORDS = {
    'es': {'el', 'la', 'los', 'las', 'un', 'una', 'unas', 'unos', 'de', 'del', 'al', 'a', 
           'en', 'con', 'por', 'para', 'sin', 'sobre', 'entre', 'y', 'e', 'o', 'u', 'que',
           'como', 'más', 'pero', 'ni', 'si', 'no', 'sí', 'él', 'ella', 'ellos', 'ellas',
           'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos', 'esas', 'esto',
           'mi', 'tu', 'su', 'mis', 'tus', 'sus', 'nuestro', 'nuestra', 'nosotros',
           'ser', 'estar', 'hay', 'fue', 'era', 'son', 'es', 'está', 'han', 'había',
           'lo', 'al', 'todo', 'toda', 'todos', 'todas', 'poco', 'poca', 'pocos', 'pocas',
           'mucho', 'mucha', 'muchos', 'muchas', 'otro', 'otra', 'otros', 'otras', 'mismo', 'misma'},
    'en': {'the', 'a', 'an', 'and', 'or', 'but', 'if', 'in', 'to', 'of', 'for', 'on', 
           'with', 'at', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been',
           'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
           'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used',
           'it', 'he', 'she', 'they', 'we', 'you', 'i', 'me', 'him', 'her', 'us', 'them',
           'this', 'that', 'these', 'those', 'what', 'which', 'who', 'whom', 'whose',
           'my', 'your', 'his', 'its', 'our', 'their',
           'not', 'no', 'yes', 'all', 'any', 'some', 'such', 'nor', 'only',
           'very', 'just', 'also', 'now', 'then', 'there', 'here', 'when', 'where',
           'each', 'every', 'both', 'few', 'more', 'most', 'other',
           'so', 'than', 'too', 'even', 'still', 'already', 'yet'}
}


def clean_text(text: str, remove_stopwords: bool = True, languages: List[str] = ['es', 'en'], exclude_words: Optional[List[str]] = None) -> str:
    """
    Limpia el texto: minúsculas, remove signos, stopwords.
    
    Args:
        text: Texto a limpiar
        remove_stopwords: Si True,移除 stopwords según idiomas
        languages: Lista de idiomas para stopwords (es, en)
        exclude_words: Lista de palabras adicionales a excluir
        
    Returns:
        str: Texto limpio
    """
    # Minúsculas
    text = text.lower()
    
    # Remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    
    # Normalizar espacios
    text = re.sub(r'\s+', ' ', text).strip()
    
    if remove_stopwords:
        stop = set()
        for lang in languages:
            stop.update(STOP_WORDS.get(lang, set()))
        words = text.split()
        text = ' '.join(w for w in words if w not in stop and len(w) > 2)
    
    # Excluir palabras custom
    if exclude_words:
        exclude_set = set(w.lower() for w in exclude_words)
        words = text.split()
        text = ' '.join(w for w in words if w not in exclude_set)
    
    return text