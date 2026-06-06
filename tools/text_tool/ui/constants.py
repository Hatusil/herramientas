"""
Constants para TextAnalyzerUI.
Separado de main_ui.py por SRP (máxima R0: clases <300 líneas).
"""

from core.theme import get_status_color

# Status colors - resolver desde tema activo
STATUS_COLORS = {k: get_status_color(k) for k in ["blue", "green", "orange", "red", "gray"]}

# Tab configuration - consolidated to 5 main tabs
TAB_ORDER = ["input", "clean", "stats", "freq", "viz"]

TAB_ICONS = {
    "input": "📥",
    "clean": "⚙️",
    "stats": "📉",
    "freq": "📈",
    "viz": "📊",
}

# Visualization options available in the "viz" dropdown
VIZ_OPTIONS = {
    "wc": {"name": "WordCloud", "icon": "☁️", "tab_key": "wc"},
    "ngrams": {"name": "N-grams", "icon": "🔗", "tab_key": "ngrams"},
    "trends": {"name": "Trends", "icon": "📊", "tab_key": "trends"},
    "corr": {"name": "Correlaciones", "icon": "🔥", "tab_key": "corr"},
    "scatter": {"name": "Scatter", "icon": "⬡", "tab_key": "scatter"},
    "wordtree": {"name": "WordTree", "icon": "🌳", "tab_key": "wordtree"},
    "streamgraph": {"name": "StreamGraph", "icon": "🌊", "tab_key": "streamgraph"},
    "bubblelines": {"name": "BubbleLines", "icon": "🫧", "tab_key": "bubblelines"},
    "mandala": {"name": "Mandala", "icon": "⭕", "tab_key": "mandala"},
    "kwic": {"name": "KWIC", "icon": "🔍", "tab_key": "kwic"},
    "topics": {"name": "Topics", "icon": "📚", "tab_key": "topics"},
}

# Legacy tab icons (for backwards compatibility)
LEGACY_TAB_ICONS = {
    "wc": "☁️", "ngrams": "🔗", "trends": "📊", "corr": "🔥",
    "scatter": "⬡", "wordtree": "🌳", "streamgraph": "🌊",
    "bubblelines": "🫧", "mandala": "⭕", "kwic": "🔍", "topics": "📚"
}

HELP_CONTENT = {
    "title": "Ayuda - Text Analyzer",
    "description": "📊 Analiza texto: WordCloud, frecuencia, estadísticas, n-grams, Trends, Correlaciones, Scatter, StreamGraph, Bubblelines, Mandala",
    "usage": [
        "1. Elegir tipo: Texto/Archivo/URL",
        "2. Ingresar o seleccionar contenido",
        "3. Click en 'Cargar y Analizar'",
        "4. Ver resultados en las solapas",
        "5. Click en gráficos para ver en ventana grande",
    ],
    "tips": [
        "💡 Ctrl+V=paste, Ctrl+O=abrir, Ctrl+S=guardar",
        "💡 Ctrl+Enter=analizar, Escape=cancelar",
        "💡 Arrastrá archivos sobre el área de texto",
        "💡 StreamGraph: más términos = más detalle",
        "💡 Bubblelines: ingresá términos separados por coma",
        "💡 Mandala: más anillos = más granularidad",
    ],
    "warnings": [
        "⚠️ Textos grandes (>100KB) son más lentos",
        "⚠️ URL scraping puede fallar con anti-bot",
    ],
}

# Subtools configuration
SUBTOOL_INFO = {
    "text": {"name": "Texto", "icon": "📝"},
    "file": {"name": "Archivo", "icon": "📄"},
    "url": {"name": "URL", "icon": "🌐"},
}