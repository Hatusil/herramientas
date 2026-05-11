"""Sub-tool information constants for Text Analyzer UI.

Extracted from ui.py SUBTOOL_INFO dictionary.
"""

# Dictionary of descriptions for each sub-tool
SUBTOOL_INFO = {
    "wordcloud": {
        "name": "WordCloud",
        "icon": "☁️",
        "description": "Nube de palabras visual",
        "what_is": "Representación visual donde el tamaño de cada palabra indica su frecuencia en el texto. Las palabras más grandes aparecen más veces en el documento, creando una 'nube'.",
        "use_for": [
            "Identificar términos dominantes rápidamente",
            "Ver estructura temática del documento",
            "Crear visualizaciones para presentaciones",
            "Detectar palabras clave de un vistazo"
        ]
    },
    "frequency": {
        "name": "Frecuencia",
        "icon": "📈",
        "description": "Palabras más frecuentes",
        "what_is": "Lista ordenada de las palabras más usadas en el texto, con su conteo exacto. Muestra ranking de términos por frecuencia.",
        "use_for": [
            "Conocer las palabras clave del texto",
            "Analizar vocabulario del autor",
            "Detectar temas principales",
            "Comparar vocabulario entre textos"
        ]
    },
    "stats": {
        "name": "Estadísticas",
        "icon": "📉",
        "description": "Estadísticas del texto",
        "what_is": "Conjunto de métricas cuantitativas del texto: caracteres, palabras, oraciones, palabras únicas, promedios y Type-Token Ratio (riqueza léxica).",
        "use_for": [
            "Medir extensión y complejidad del texto",
            "Evaluar riqueza de vocabulario",
            "Comparar textos por métricas",
            "Analizar estilo de escritura"
        ]
    },
    "ngrams": {
        "name": "N-grams",
        "icon": "🔗",
        "description": "Frases repetidas (bigramas/trigramas)",
        "what_is": "Secuencias de 2 o 3 palabras que aparecen juntas frecuentemente en el texto. Revela expresiones comunes y patrones de escritura.",
        "use_for": [
            "Encontrar expresiones típicas del autor",
            "Identificar frases feitas",
            "Analizar estilo y tono",
            "Descubrir temas recurrentes"
        ]
    },
    "trends": {
        "name": "Tendencias",
        "icon": "📊",
        "description": "Frecuencia por secciones",
        "what_is": "Gráfico que muestra cómo la frecuencia de palabras clave cambia a lo largo del texto (por secciones). Revela la evolución temática.",
        "use_for": [
            "Ver cambios temáticos a lo largo del documento",
            "Identificar cuándo aparecen ciertos temas",
            "Analizar estructura narrativa",
            "Rastrear evolución de ideas"
        ]
    },
    "correlations": {
        "name": "Correlaciones",
        "icon": "🔥",
        "description": "Palabras que aparecen juntas",
        "what_is": "Análisis de asociación que encuentra palabras que statistically tienden a aparecer próximas entre sí. Revela relaciones semánticas implícitas.",
        "use_for": [
            "Descubrir relaciones entre conceptos",
            "Identificar sinónimos implícitos",
            "Analizar redes semánticas",
            "Detectar patrones temáticos"
        ]
    },
    "scatter": {
        "name": "Scatter",
        "icon": "⬡",
        "description": "Distribución término vs posición",
        "what_is": "Gráfico de dispersión que muestra la posición de cada palabra clave en el texto. Permite ver concentración o distribución de términos.",
        "use_for": [
            "Ver dónde aparecen términos específicos",
            "Detectar repeticiones anómalas",
            "Analizar distribución textual",
            "Identificar clusters temáticos"
        ]
    },
    "kwic": {
        "name": "KWIC (Contextos)",
        "icon": "🔍",
        "description": "Keyword In Context / Concordancia",
        "what_is": "Muestra cada aparición de una palabra junto con sus palabras circundantes. Esencial para análisis cualitativo de contexto de uso.",
        "use_for": [
            "Analizar contexto de uso de términos",
            "Entender significados en contexto",
            "Ver patrones de uso",
            "Investigar acepciones específicas"
        ]
    },
    "topics": {
        "name": "Temas (LDA)",
        "icon": "📚",
        "description": "Latent Dirichlet Allocation",
        "what_is": "Técnica de topic modeling que descubre automáticamente los temaslatentes en el texto. Agrupa palabras que tienden a aparecer juntas.",
        "use_for": [
            "Descubrir temas principales automáticamente",
            "Segmentar documento por temas",
            "Resumen automático",
            "Clasificación de documentos"
        ]
    },
    "wordtree": {
        "name": "Árbol de Palabras",
        "icon": "🌳",
        "description": "WordTree jerárquico",
        "what_is": "Visualización jerárquica en forma de árbol que muestra las palabras que siguen a una palabra clave, ramificando en múltiples direcciones.",
        "use_for": [
            "Explorar patrones de secuenciación",
            "Ver ramificaciones después de una palabra",
            "Analizar estructura de frases",
            "Mapear contexto expandido"
        ]
    },
    "streamgraph": {
        "name": "StreamGraph",
        "icon": "🌊",
        "description": "Gráfico de área apilada estilo río",
        "what_is": "Visualización que muestra cómo cambia la frecuencia de varios términos a través de las secciones del texto, apilando las áreas una sobre otra.",
        "use_for": [
            "Ver evolución de temas en documentos largos",
            "Comparar cambios en frecuencia de términos",
            "Identificar patrones temporales en el texto"
        ]
    },
    "bubblelines": {
        "name": "Bubblelines",
        "icon": "🫧",
        "description": "Líneas con burbujas",
        "what_is": "Combina gráficos de línea con puntos (burbujas) cuyo tamaño refleja la importancia o frecuencia en cada posición.",
        "use_for": [
            "Comparar distribución de términos específicos",
            "Ver patrones de aparición",
            "Analizar concentración de términos"
        ]
    },
    "mandala": {
        "name": "Mandala",
        "icon": "⭕",
        "description": "Diagrama circular concéntrico",
        "what_is": "Visualización radial donde los términos se organizan en anillos concéntricos, mostrando relaciones entre términos y secciones.",
        "use_for": [
            "Ver relaciones entre términos y documentos",
            "Análisis radial de corpus",
            "Visualizar estructura multi-sección"
        ]
    }
}


# Tab order for the UI (logical grouping)
TAB_ORDER = [
    "input",      # Grupo 1: Entrada
    "clean",      # Limpieza
    "stats",      # Grupo 2: Estadísticas básicas
    "frequency",
    "wordcloud",  # Grupo 3: Visualizaciones básicas
    "ngrams",
    "trends",     # Grupo 4: Visualizaciones avanzadas
    "correlations",
    "scatter",
    "wordtree",
    "streamgraph",
    "bubblelines",
    "mandala",
    "kwic",       # Grupo 5: Análisis avanzado
    "topics",
]


# Tab icons mapping
TAB_ICONS = {
    "input": "📥",
    "clean": "⚙️",
    "stats": "📉",
    "frequency": "📈",
    "wordcloud": "☁️",
    "ngrams": "🔗",
    "trends": "📊",
    "correlations": "🔥",
    "scatter": "⬡",
    "wordtree": "🌳",
    "streamgraph": "🌊",
    "bubblelines": "🫧",
    "mandala": "⭕",
    "kwic": "🔍",
    "topics": "📚",
}