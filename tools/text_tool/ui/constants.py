"""
Constants para TextAnalyzerUI.
Separado de main_ui.py por SRP (máxima R0: clases <300 líneas).
"""

# Tab configuration
TAB_ORDER = [
    "input", "clean", "stats", "freq", "wc", "ngrams",
    "trends", "corr", "scatter", "wordtree", "streamgraph",
    "bubblelines", "mandala", "kwic", "topics"
]

TAB_ICONS = {
    "input": "📥", "clean": "⚙️", "stats": "📉", "freq": "📈",
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