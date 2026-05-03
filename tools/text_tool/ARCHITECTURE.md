# Text Analyzer Architecture

## Overview

Text Analyzer es una herramienta de análisis de texto con arquitectura modular y extensible. Permite analizar texto de múltiples fuentes (archivos, URLs, entrada directa) y generar visualizaciones como WordCloud, gráficos de frecuencia, tendencias, correlaciones y scatter plots.

## Directory Structure

```
tools/text_tool/
├── __init__.py          # Plugin entry point
├── processor.py        # Core processing logic
├── ui.py             # User interface
└── test_processor.py  # Unit tests
```

## Module Design

### 1. processor.py - Core Processing

El módulo principal contiene:

#### Extractors (Extracción de contenido)
- `extract_text_from_file(file_path)` → Extrae texto de archivos
- `extract_text_from_url(url)` → Scraping de URLs

#### Cleaners (Limpieza)
- `clean_text(text, remove_stopwords, languages, exclude_words)` → Normaliza texto

#### Analyzers (Análisis)
- `analyze_wordcloud(text)` → Genera WordCloud
- `analyze_frequency(text)` → Frecuencia de palabras
- `analyze_stats(text)` → Estadísticas del corpus
- `analyze_ngrams(text, n)` → N-grams
- `analyze_trends(text)` → Tendencias por secciones
- `analyze_correlations(text)` → Co-ocurrencia de términos
- `analyze_scatter(text)` → Distribución término-posición

### 2. ui.py - User Interface

Interfaz basada en CustomTkinter con:
- Pestañas para cada analizador
- Panel de configuración de limpieza
- Visualización de resultados

## Plugin Architecture

### How to Add New Analyzers

Para agregar un nuevo analizador (ejemplo: sentiment, NER, classification):

```python
# 1. Definir función en processor.py
def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Análisis de sentimiento del texto.
    Returns: {'success': True, 'data': {'positive': float, 'negative': float, 'neutral': float}}
    """
    # Implementar lógica
    # ...
    return {'success': True, 'data': {...}}

# 2. Registrar en ANALYZER_REGISTRY (al final de processor.py)
def _register_analyzers():
    ANALYZER_REGISTRY.update({
        'sentiment': {
            'func': analyze_sentiment,
            'requires': [],  # Dependencias necesarias
            'returns': 'data',
            'description': 'Análisis de sentimiento',
            'min_words': 10
        }
    })

# 3. Agregar en ui.py si quieres UI
#    - Agregar tab en _setup_tabs()
#    - Agregar método _show_sentiment()
```

### Analyzer Registry Pattern

```python
ANALYZER_REGISTRY = {
    'nombre': {
        'func': Callable,           # Función analizadora
        'requires': List[str],     # ['matplotlib', 'nltk', etc.]
        'returns': 'image' | 'text' | 'data' | 'stats',
        'description': str,
        'min_words': int
    }
}
```

### Returns Type Semantics

| Type | Descripción | UI Rendering |
|------|------------|---------------|
| `image` | Bytes PNG | `_show_image()` genérico |
| `text` | Texto formateado | `_show_text()` genérico |
| `data` | Dict con datos | Custom render |
| `stats` | Estadísticas | `_show_stats()` genérico |

## Supported File Formats

| Format | Extension | Module | Notes |
|--------|----------|--------|-------|
| Texto plano | .txt, .md | built-in | UTF-8 |
| PDF | .pdf | pdfplumber | Requiere texto |
| Word | .docx, .doc | python-docx | |
| Excel | .xlsx, .xls | openpyxl | data_only=True |
| CSV | .csv | built-in csv | |
| URL | Web | requests + bs4 | Scraping |

## Design Patterns

### 1. Result Dictionary Pattern

Todas las funciones retornan:
```python
{
    'success': bool,
    'result_key': Any,  # image_data, frequencies, error, etc.
    'error': str | None  # Solo si success=False
}
```

### 2. Dependency Check Pattern

```python
def analyze_wordcloud(text: str) -> Dict[str, Any]:
    if not WORDCLOUD_AVAILABLE:
        return {'success': False, 'error': 'wordcloud no instalado'}
    # ... implementation
```

### 3. Validation Pattern

```python
def analyze_trends(text: str, n_terms: int = 5) -> Dict[str, Any]:
    cleaned = clean_text(text, remove_stopwords=True)
    words = cleaned.split()
    
    if len(words) < n_sections:
        return {'success': False, 'error': 'Texto muy corto para tendencias'}
    # ... implementation
```

### 4. Image Generation Pattern

```python
def _generate_plot_image(fig) -> bytes:
    img_buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(img_buffer, format='PNG', dpi=100)
    img_buffer.seek(0)
    return img_buffer.getvalue()
```

## Workflow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   INPUT    │────▶│  LIMPIEZA   │────▶│  ANALYSIS  │
│            │     │             │     │            │
│ • Texto    │     │ • Stopwords │     │ • WordCloud│
│ • Archivo │     │ • Exclude   │     │ • Frecuency│
│ • URL     │     │ • Languages │     │ • Stats    │
└─────────────┘     └─────────────┘     │ • N-grams │
                                        │ • Trends  │
                                        │ • Corr    │
                                        │ • Scatter│
                                        └─────────────┘
```

## Dependencies (Optional)

| Package | Used By | Required For |
|---------|---------|--------------|
| wordcloud | WordCloud | Nube de palabras |
| pdfplumber | PDF extraction | Leer PDFs |
| python-docx | Word extraction | Leer .docx |
| openpyxl | Excel extraction | Leer .xlsx |
| requests | URL scraping | Web scraping |
| beautifulsoup4 | HTML parsing | Web scraping |
| matplotlib | Charts | Trends, Corr, Scatter |
| numpy | Matrix ops | Correlaciones |

## Future Extensions

### Planned Analyzers

1. **Sentiment Analysis** - Análisis de sentimiento
2. **NER** - Named Entity Recognition
3. **Classification** - Clasificación de texto
4. **Summarization** - Resumen automático
5. **Topic Modeling** - LDA/NMF topics

### External Services (Optional)

- OpenAI API (GPT análisis)
- HuggingFace (transformers NER)
- Spacy (NLP avanzado)

## Error Handling

Errores se manejan retornando:
```python
return {'success': False, 'error': 'Mensaje descriptivo'}
```

Errores comunes:
- Archivo no encontrado
- Formato no soportado
- Dependencias faltantes
- Texto muy corto
- Error de red (URL)

## Performance Tips

1. **Textos grandes**: Usar chunks para procesamiento
2. **Múltiples archivos**: Procesar en background thread
3. **Imágenes**: Usar thumbnail para display
4. **Cache**: Cachear resultados intermedios