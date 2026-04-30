"""
TextAnalyzerProcessor: Procesamiento de análisis de texto.
"""
import os
import re
from pathlib import Path
from typing import Dict, Any, List
from io import BytesIO
from collections import Counter

logger = logging.getLogger(__name__)

try:
    import nltk
    # NLTK para n-grams
    nltk.data.find('tokenizers/punkt')
    NLTK_AVAILABLE = True
except Exception as e:
        logger.warning(f"NLTK not available: {e}")
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
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


# Stop words comunes (español + inglés)
STOP_WORDS = {
    'es': {'el', 'la', 'los', 'las', 'un', 'una', 'unas', 'unos', 'de', 'del', 'al', 'a', 
           'en', 'con', 'por', 'para', 'sin', 'sobre', 'entre', 'y', 'e', 'o', 'u', 'que',
           'como', 'más', 'pero', 'ni', 'si', 'no', 'sí', 'él', 'ella', 'ellos', 'ellas',
           'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos', 'esas', 'esto',
           'mi', 'tu', 'su', 'mis', 'tus', 'sus', 'nuestro', 'nuestra', 'nosotros',
           'ser', 'estar', 'hay', 'fue', 'era', 'son', 'son', 'es', 'está', 'han', 'había',
           'lo', 'su', 'al', 'todo', 'toda', 'todos', 'todas', 'poco', 'poca', 'pocos', 'pocas',
           'mucho', 'mucha', 'muchos', 'muchas', 'otro', 'otra', 'otros', 'otras', 'mismo', 'misma'},
    'en': {'the', 'a', 'an', 'and', 'or', 'but', 'if', 'in', 'to', 'of', 'for', 'on', 
           'with', 'at', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been',
           'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
           'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used',
           'it', 'he', 'she', 'they', 'we', 'you', 'i', 'me', 'him', 'her', 'us', 'them',
           'this', 'that', 'these', 'those', 'what', 'which', 'who', 'whom', 'whose',
           'my', 'your', 'his', 'her', 'its', 'our', 'their', 'whose',
           'not', 'no', 'yes', 'all', 'any', 'some', 'such', 'no', 'nor', 'only',
           'very', 'just', 'also', 'now', 'then', 'there', 'here', 'when', 'where',
           'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'any',
           'so', 'than', 'too', 'very', 'just', 'even', 'still', 'already', 'yet'}
}


def extract_text_from_file(file_path: str) -> Dict[str, Any]:
    """Extrae texto de archivos .txt, .pdf, .docx."""
    if not os.path.exists(file_path):
        return {'success': False, 'error': 'Archivo no encontrado'}
    
    ext = Path(file_path).suffix.lower()
    
    try:
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            return {'success': True, 'text': text, 'source': file_path}
        
        elif ext == '.pdf':
            if not PDFPLUMBER_AVAILABLE:
                return {'success': False, 'error': 'pdfplumber no instalado'}
            
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    text += page_text + "\n"
            return {'success': True, 'text': text, 'source': file_path}
        
        elif ext in ['.docx', '.doc']:
            if not DOCX_AVAILABLE:
                return {'success': False, 'error': 'python-docx no instalado'}
            
            doc = DocxDocument(file_path)
            text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            return {'success': True, 'text': text, 'source': file_path}
        
        else:
            return {'success': False, 'error': f'Formato no soportado: {ext}'}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def extract_text_from_url(url: str) -> Dict[str, Any]:
    """Extrae texto de una URL."""
    logger.info(f"Intentando scrapear URL: {url}")
    
    if not REQUESTS_AVAILABLE:
        logger.error("requests no está instalado")
        return {'success': False, 'error': 'requests no instalado'}
    
    # Validar que la URL tenga protocolo
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        logger.warning(f"URL sin protocolo válido: {url}")
        url = 'https://' + url
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        }
        
        logger.info(f"Haciendo request a: {url}")
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        logger.info(f"Response received, status: {response.status_code}")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraer texto visible
        for script in soup(['script', 'style']):
            script.decompose()
        
        text = soup.get_text(separator=' ')
        text = re.sub(r'\s+', ' ', text).strip()
        
        logger.info(f"Texto extraído: {len(text)} caracteres")
        return {'success': True, 'text': text, 'source': url}
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e}")
        return {'success': False, 'error': f'HTTP {e.response.status_code}'}
    except requests.exceptions.ConnectionError:
        logger.error("Error de conexión - verifica la URL")
        return {'success': False, 'error': 'Error de conexión - verifica la URL'}
    except requests.exceptions.Timeout:
        logger.error("Timeout - la página tardó mucho en responder")
        return {'success': False, 'error': 'Timeout - la página tardó mucho'}
    except Exception as e:
        logger.error(f"Error al scrapear: {e}")
        return {'success': False, 'error': str(e)}


def clean_text(text: str, remove_stopwords: bool = True, languages: List[str] = ['es', 'en']) -> str:
    """Limpia el texto: minúsculas, remove signos, stopwords."""
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
    
    return text


def analyze_wordcloud(text: str, n_words: int = 100, width: int = 800, height: int = 400) -> Dict[str, Any]:
    """Genera unaWordCloud."""
    if not WORDCLOUD_AVAILABLE:
        return {'success': False, 'error': 'wordcloud no instalado'}
    
    try:
        cleaned = clean_text(text, remove_stopwords=True)
        
        wc = WordCloud(
            width=width, 
            height=height,
            background_color='white',
            max_words=n_words,
            colormap='viridis',
            prefer_horizontal=0.7
        )
        
        wc.generate(cleaned)
        
        # Convertir a imagen
        img_buffer = BytesIO()
        wc.to_image().save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return {
            'success': True,
            'image_data': img_buffer.getvalue(),
            'message': f'WordCloud con {n_words} palabras'
        }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def analyze_frequency(text: str, n: int = 20, remove_stopwords: bool = True) -> Dict[str, Any]:
    """Analiza frecuencia de palabras."""
    cleaned = clean_text(text, remove_stopwords=remove_stopwords)
    words = cleaned.split()
    
    # Contar
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    
    # Ordenar
    sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:n]
    
    return {
        'success': True,
        'frequencies': dict(sorted_freq),
        'total_words': len(words),
        'unique_words': len(freq)
    }


def analyze_trends(text: str, n_terms: int = 5, n_sections: int = 10) -> Dict[str, Any]:
    """
    Análisis de tendencias: frecuencia de palabras en diferentes secciones del texto.
    Similar a 'Trends' de Voyant.
    """
    try:
        import matplotlib
        matplotlib.use('Agg')  # Sin GUI
        import matplotlib.pyplot as plt
        from collections import Counter
    except ImportError:
        return {'success': False, 'error': 'matplotlib no instalado'}
    
    cleaned = clean_text(text, remove_stopwords=True)
    words = cleaned.split()
    
    if len(words) < n_sections:
        return {'success': False, 'error': 'Texto muy corto para tendencias'}
    
    # Encontrar palabras más frecuentes
    freq = Counter(words)
    top_words = [w for w, _ in freq.most_common(n_terms)]
    
    if not top_words:
        return {'success': False, 'error': 'No hay palabras suficientes'}
    
    # Dividir texto en secciones y contar frecuencia de cada palabra
    section_size = len(words) // n_sections
    trends_data = {word: [] for word in top_words}
    
    for i in range(n_sections):
        start = i * section_size
        end = start + section_size if i < n_sections - 1 else len(words)
        section_words = words[start:end]
        section_freq = Counter(section_words)
        
        for word in top_words:
            trends_data[word].append(section_freq.get(word, 0))
    
    # Crear gráfico
    fig, ax = plt.subplots(figsize=(10, 5))
    
    x = range(n_sections)
    for word in top_words:
        ax.plot(x, trends_data[word], marker='o', label=word, linewidth=2)
    
    ax.set_xlabel('Sección del texto')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Tendencias de palabras en el texto')
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # Convertir a imagen
    img_buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(img_buffer, format='PNG', dpi=100)
    img_buffer.seek(0)
    
    return {
        'success': True,
        'image_data': img_buffer.getvalue(),
        'top_words': top_words,
        'trends': trends_data
    }


def analyze_correlations(text: str, n_terms: int = 15) -> Dict[str, Any]:
    """
    Análisis de correlaciones entre términos.
    Muestra qué palabras aparecen juntas.
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
        from collections import Counter
    except ImportError:
        return {'success': False, 'error': 'matplotlib no instalado'}
    
    cleaned = clean_text(text, remove_stopwords=True)
    words = cleaned.split()
    
    if len(words) < 20:
        return {'success': False, 'error': 'Texto muy corto para correlaciones'}
    
    # Encontrar términos más frecuentes
    freq = Counter(words)
    top_words = [w for w, _ in freq.most_common(n_terms)]
    
    if len(top_words) < 3:
        return {'success': False, 'error': 'No hay suficientes palabras'}
    
    # Crear matriz de co-ocurrencia
    n = len(top_words)
    cooccur = np.zeros((n, n))
    
    word_idx = {w: i for i, w in enumerate(top_words)}
    
    # Window de 5 palabras
    window = 5
    for i, word in enumerate(words):
        if word in word_idx:
            for j in range(max(0, i - window), min(len(words), i + window + 1)):
                other = words[j]
                if other in word_idx and other != word:
                    cooccur[word_idx[word]][word_idx[other]] += 1
    
    # Crear heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    
    im = ax.imshow(cooccur, cmap='YlOrRd', aspect='auto')
    
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(top_words, rotation=45, ha='right', fontsize=8)
    ax.set_yticklabels(top_words, fontsize=8)
    
    ax.set_title('Correlaciones entre términos')
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Co-ocurrencia')
    
    # Convertir a imagen
    img_buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(img_buffer, format='PNG', dpi=100)
    img_buffer.seek(0)
    
    return {
        'success': True,
        'image_data': img_buffer.getvalue(),
        'terms': top_words,
        'matrix': cooccur.tolist()
    }


def analyze_scatter(text: str, n_terms: int = 30) -> Dict[str, Any]:
    """
    Scatter plot de términos basado en frecuencia y posición.
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from collections import Counter
    except ImportError:
        return {'success': False, 'error': 'matplotlib no instalado'}
    
    cleaned = clean_text(text, remove_stopwords=True)
    words = cleaned.split()
    
    if len(words) < 20:
        return {'success': False, 'error': 'Texto muy corto'}
    
    # Contar frecuencia y posición promedio
    freq = Counter(words)
    position_sum = {}
    position_count = {}
    
    for i, word in enumerate(words):
        if word not in position_sum:
            position_sum[word] = 0
            position_count[word] = 0
        position_sum[word] += i
        position_count[word] += 1
    
    # Calcular métricas
    data = []
    for word in freq:
        if position_count[word] >= 2:
            avg_position = position_sum[word] / position_count[word]
            normalized_pos = avg_position / len(words)  # 0-1
            data.append({
                'word': word,
                'frequency': freq[word],
                'avg_position': normalized_pos
            })
    
    if not data:
        return {'success': False, 'error': 'Datos insuficientes'}
    
    # Ordenar por frecuencia y tomar top
    data = sorted(data, key=lambda x: x['frequency'], reverse=True)[:n_terms]
    
    # Crear scatter plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    freqs = [d['frequency'] for d in data]
    positions = [d['avg_position'] for d in data]
    labels = [d['word'] for d in data]
    
    sizes = [f * 20 + 50 for f in freqs]  # Tamaño según frecuencia
    
    scatter = ax.scatter(positions, freqs, s=sizes, alpha=0.6, c=freqs, cmap='viridis')
    
    # Labels
    for i, label in enumerate(labels):
        ax.annotate(label, (positions[i], freqs[i]), fontsize=8, alpha=0.8)
    
    ax.set_xlabel('Posición promedio en el texto (inicio → fin)')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Distribución de términos en el texto')
    ax.grid(True, alpha=0.3)
    
    # Convertir a imagen
    img_buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(img_buffer, format='PNG', dpi=100)
    img_buffer.seek(0)
    
    return {
        'success': True,
        'image_data': img_buffer.getvalue(),
        'data': data
    }


def analyze_stats(text: str) -> Dict[str, Any]:
    """Estadísticas del corpus."""
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s for s in sentences if s.strip()]
    
    # Calcular
    total_chars = len(text)
    total_words = len(words)
    unique_words = len(set(words))
    avg_word_len = sum(len(w) for w in words) / total_words if total_words > 0 else 0
    avg_sentence_len = total_words / len(sentences) if sentences else 0
    
    return {
        'success': True,
        'total_chars': total_chars,
        'total_words': total_words,
        'unique_words': unique_words,
        'total_sentences': len(sentences),
        'avg_word_length': round(avg_word_len, 2),
        'avg_sentence_length': round(avg_sentence_len, 2),
        'type_token_ratio': round(unique_words / total_words, 4) if total_words > 0 else 0
    }


def analyze_ngrams(text: str, n: int = 2, top_k: int = 20) -> Dict[str, Any]:
    """Analiza n-grams (sin dependencia de nltk)."""
    cleaned = clean_text(text, remove_stopwords=True)
    words = cleaned.split()
    
    if len(words) < n:
        return {'success': False, 'error': 'Texto muy corto para n-grams'}
    
    # Generar n-grams manualmente
    ngram_list = []
    for i in range(len(words) - n + 1):
        ngram_list.append(tuple(words[i:i+n]))
    
    # Contar
    freq = Counter(ngram_list)
    
    # Ordenar
    sorted_ngrams = freq.most_common(top_k)
    
    return {
        'success': True,
        'ngrams': {(' '.join(ng)): count for ng, count in sorted_ngrams},
        'n': n,
        'total': len(ngram_list)
    }