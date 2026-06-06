# Text Analyzer Architecture

## Overview

Text Analyzer es una herramienta de análisis de texto con arquitectura modular y extensible. Soporta 13 visualizaciones: WordCloud, Frecuencia, Estadísticas, N-grams, Trends, Correlaciones, Scatter, WordTree, KWIC, Topics, StreamGraph, Bubblelines y Mandala.

## Directory Structure

```
tools/text_tool/
├── __init__.py              # Plugin entry point
├── processor.py             # Extractors, cleaners, registry
├── ARCHITECTURE.md          # Este documento
├── processors/              # Un módulo por visualización
│   ├── __init__.py
│   ├── extractors.py        # File/URL extraction
│   ├── utils.py             # Cleaners, helpers
│   ├── frequency.py         # Frecuencia + Stats
│   ├── wordcloud.py         # Nube de palabras
│   ├── trends.py            # Tendencias
│   ├── correlations.py      # Co-ocurrencias
│   ├── scatter.py           # Scatter plot
│   ├── wordtree.py          # Árbol de palabras
│   ├── kwic.py              # KWIC concordance
│   ├── topics.py            # Topic modeling
│   ├── streamgraph.py       # 🌊 Área apilada
│   ├── bubblelines.py       # 🫧 Líneas + burbujas
│   └── mandala.py           # ⭕ Diagrama polar
├── ui/
│   ├── __init__.py
│   ├── constants.py         # HELP_CONTENT, VIZ_OPTIONS, TAB_ORDER
│   ├── main_ui.py           # TextAnalyzerUI (hereda BaseToolUI)
│   ├── analysis.py          # Orchestrator de análisis
│   ├── callbacks.py         # Callbacks de UI
│   ├── common.py            # Shared UI components
│   ├── keyboard_shortcuts.py
│   ├── modal.py             # Modal dialogs
│   ├── modal_export.py      # Export dialogs
│   ├── state.py             # Estado de UI
│   ├── viz_panel.py         # Panel de visualización
│   └── tabs/                # Setup de tabs por visualización
└── tests/
```

## Processor Modules (processors/)

Cada visualización es un módulo independiente siguiendo SRP:

| Módulo | Función Principal | Retorna |
|--------|-------------------|---------|
| `frequency.py` | `analyze_frequency()`, `analyze_stats()` | `image` |
| `wordcloud.py` | `analyze_wordcloud()` | `image` |
| `trends.py` | `analyze_trends()` | `image` |
| `correlations.py` | `analyze_correlations()` | `image` |
| `scatter.py` | `analyze_scatter()` | `image` |
| `wordtree.py` | `analyze_wordtree()` | `image` |
| `kwic.py` | `analyze_kwic()` | `text` |
| `topics.py` | `analyze_topics()` | `text` |
| `streamgraph.py` | `analyze_streamgraph()` | `image` |
| `bubblelines.py` | `analyze_bubblelines()` | `image` |
| `mandala.py` | `analyze_mandala()` | `image` |

## Plugin Architecture

### Cómo agregar un nuevo analizador

```python
# 1. Crear processors/mi_analizador.py
def analyze_mi_analizador(text: str, **kwargs) -> dict:
    """Análisis personalizado."""
    return {'success': True, 'image_data': bytes, 'error': ''}

# 2. Registrar en processor.py
ANALYZER_REGISTRY['mi_analizador'] = {
    'func': analyze_mi_analizador,
    'requires': [],           # ['matplotlib', 'nltk']
    'returns': 'image',
    'description': 'Mi análisis',
    'min_words': 50
}

# 3. Crear tab en ui/tabs/mi_analizador_tab.py
# 4. Agregar en constants.py: VIZ_OPTIONS
# 5. Integrar en ui/analysis.py
```

### Registry Pattern

```python
ANALYZER_REGISTRY = {
    'nombre': {
        'func': Callable,
        'requires': List[str],
        'returns': 'image' | 'text' | 'data' | 'stats',
        'description': str,
        'min_words': int
    }
}
```

## UI Architecture

### TextAnalyzerUI (hereda BaseToolUI)

```
BaseToolUI (core/)
    └── TextAnalyzerUI
            ├── Input (Pestaña 1): Switch 3 opciones
            │   ├── Texto directo
            │   ├── Archivos (seleccionar archivos)
            │   └── URLs (ingresar URLs)
            │   → Solo guarda, no analiza
            │
            ├── Clean (Pestaña 2): Clean tab
            │   ├── Selector de fuente (texto/archivos/urls)
            │   ├── Botón "Crear texto bruto"
            │   ├── Stats: chars, palabras reales
            │   ├── Preview: top 20 palabras
            │   ├── Filtros: conectores, palabras excluidas
            │   ├── Botón "Aplicar filtros"
            │   └── Botón "Ejecutar análisis y crear visualizaciones"
            │
            └── Visualization (Pestañas 3-13): 13 visualizaciones
                ├── Cada una con filtros independientes
                └── Regenera si cambia análisis anterior
```

### VIZ_OPTIONS (constants.py)

```python
VIZ_OPTIONS = {
    "wc": {"name": "WordCloud", "icon": "☁️"},
    "ngrams": {"name": "N-grams", "icon": "🔗"},
    "trends": {"name": "Trends", "icon": "📊"},
    "corr": {"name": "Correlaciones", "icon": "🔥"},
    "scatter": {"name": "Scatter", "icon": "⬡"},
    "wordtree": {"name": "WordTree", "icon": "🌳"},
    "streamgraph": {"name": "StreamGraph", "icon": "🌊"},
    "bubblelines": {"name": "BubbleLines", "icon": "🫧"},
    "mandala": {"name": "Mandala", "icon": "⭕"},
    "kwic": {"name": "KWIC", "icon": "🔍"},
    "topics": {"name": "Topics", "icon": "📚"},
}
```

## Supported File Formats

| Format | Extension | Module | Notes |
|--------|-----------|--------|-------|
| Texto plano | .txt, .md | built-in | UTF-8 |
| PDF | .pdf | pdfplumber | Requiere texto |
| Word | .docx, .doc | python-docx | |
| Excel | .xlsx, .xls | openpyxl | data_only=True |
| CSV | .csv | built-in csv | |
| URL | Web | requests + bs4 | Scraping |

## Design Patterns

### Result Dictionary Pattern

```python
{
    'success': bool,
    'image_data': bytes | None,  # PNG
    'error': str | None          # Solo si success=False
}
```

### Metrics Pattern (processor.py)

```python
from core.metrics import Timer, Counter, get_metric

def analyze_wordcloud(text: str) -> dict:
    timer = get_metric('text_wordcloud_duration')
    counter = get_metric('text_wordcloud_count')
    with Timer('wordcloud'):
        # ... implementation
        counter.increment()
        words_processed = get_metric('text_words_processed')
        words_processed.increment(len(words))
```

## Dependencies

| Package | Used By | Required For |
|---------|---------|--------------|
| wordcloud | wordcloud.py | Nube de palabras |
| pdfplumber | extractors.py | Leer PDFs |
| python-docx | extractors.py | Leer .docx |
| openpyxl | extractors.py | Leer .xlsx |
| requests | extractors.py | Web scraping |
| beautifulsoup4 | extractors.py | HTML parsing |
| matplotlib | trends, correlations, etc. | Charts |
| numpy | correlations.py | Matrix ops |

## Workflow (NEW - Manual Mode)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   INPUT     │────▶│   CLEAN     │────▶│   VIZ       │
│             │     │             │     │             │
│ • Texto     │     │ • Elegir   │     │ 13 módulos  │
│ • Archivos  │     │   fuente   │     │ en processors/
│ • URLs      │     │ • Crear    │     │ (manual)    │
│ (solo       │     │   texto    │     │             │
│  guardar)   │     │   bruto    │     │             │
│             │     │ • Preview  │     │             │
│             │     │   top 20   │     │             │
│             │     │ • Aplicar  │     │             │
│             │     │   filtros  │     │             │
│             │     │ • Botón:   │     │             │
│             │     │   "Ejecutar │     │             │
│             │     │   análisis"│     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Nuevo Flujo (detallado)

**1. INPUT (Pestaña 1)**
- Switch con 3 opciones: Texto | Archivos | URLs
- Cada opción solo GUARDA el contenido en el state
- NO ejecuta análisis ni procesos automáticos
- Pasa a la pestaña Clean

**2. CLEAN (Pestaña 2)**
- Selector de fuente: texto cargado | archivos | URLs scrapeadas
- Botón "Crear texto bruto" → combina fuentes seleccionadas
- Muestra stats reales del texto en bruto (chars, palabras)
- Preview: top 20 palabras
- Botón "Aplicar filtros" (opcional): conectores, palabras excluidas
- Botón "Ejecutar análisis y crear visualizaciones" (HABILITADO solo después de aplicar filtros)
- Al ejecutar → limpia análisis anteriores y regenera todo

**3. VIZ (Pestañas 3-13)**
- Cada gráfico es independiente
- Tiene sus propios filtros/modificadores
- Si se modifica pestaña Clean → limpia y regenera todos los gráficos

## Future Extensions

- Sentiment Analysis
- Named Entity Recognition (NER)
- Text Classification
- Automatic Summarization
- Topic Modeling (LDA/NMF)

## Error Handling

Todas las funciones retornan:
```python
return {'success': False, 'error': 'Mensaje descriptivo'}
```

Errores comunes: archivo no encontrado, formato no soportado, dependencias faltantes, texto muy corto, error de red.