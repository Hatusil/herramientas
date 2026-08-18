from typing import Dict, Any, Optional, Callable, List

ANALYZER_REGISTRY: Dict[str, Dict[str, Any]] = {}


def get_analyzer(name: str) -> Optional[Callable]:
    return ANALYZER_REGISTRY.get(name, {}).get('func')


def list_analyzers() -> List[str]:
    return list(ANALYZER_REGISTRY.keys())


def get_analyzer_info(name: str) -> Optional[Dict[str, Any]]:
    return ANALYZER_REGISTRY.get(name)


def _register_analyzers():
    from tools.text_tool.processors.frequency import analyze_frequency, analyze_ngrams, analyze_stats
    from tools.text_tool.processors.wordcloud import analyze_wordcloud
    from tools.text_tool.processors.wordtree import analyze_wordtree_simple, analyze_wordtree
    from tools.text_tool.processors.topics import analyze_topics
    from tools.text_tool.processors.correlations import analyze_correlations
    from tools.text_tool.processors.scatter import analyze_scatter
    from tools.text_tool.processors.streamgraph import analyze_streamgraph
    from tools.text_tool.processors.bubblelines import analyze_bubblelines
    from tools.text_tool.processors.mandala import analyze_mandala
    from tools.text_tool.processors.category import analyze_category, analyze_sentiment, analyze_entities, analyze_summary
    from tools.text_tool.processors.trends import analyze_trends

    ANALYZER_REGISTRY.update({
        'wordcloud': {
            'func': analyze_wordcloud,
            'requires': ['wordcloud'],
            'returns': 'image',
            'description': 'Genera nube de palabras',
            'min_words': 10
        },
        'frequency': {
            'func': analyze_frequency,
            'requires': [],
            'returns': 'text',
            'description': 'Palabras más frecuentes',
            'min_words': 5
        },
        'stats': {
            'func': analyze_stats,
            'requires': [],
            'returns': 'stats',
            'description': 'Estadísticas del corpus',
            'min_words': 1
        },
        'ngrams': {
            'func': analyze_ngrams,
            'requires': [],
            'returns': 'text',
            'description': 'N-grams (bigramas, trigramas)',
            'min_words': 3
        },
        'trends': {
            'func': analyze_trends,
            'requires': ['matplotlib'],
            'returns': 'image',
            'description': 'Tendencia de términos por secciones',
            'min_words': 50
        },
        'correlations': {
            'func': analyze_correlations,
            'requires': ['matplotlib', 'numpy'],
            'returns': 'image',
            'description': 'Co-ocurrencia de términos',
            'min_words': 20
        },
        'scatter': {
            'func': analyze_scatter,
            'requires': ['matplotlib'],
            'returns': 'image',
            'description': 'Distribución término-posición',
            'min_words': 20
        },
        'topics': {
            'func': analyze_topics,
            'requires': ['sklearn'],
            'returns': 'data',
            'description': 'LDA - Latent Dirichlet Allocation',
            'min_words': 100
        },
        'wordtree': {
            'func': analyze_wordtree,
            'requires': ['matplotlib'],
            'returns': 'image',
            'description': 'WordTree - Árbol de palabras',
            'min_words': 50
        },
        'wordtree_simple': {
            'func': analyze_wordtree_simple,
            'requires': [],
            'returns': 'text',
            'description': 'WordTree Simple - lista de continuaciones',
            'min_words': 20
        },
        'streamgraph': {
            'func': analyze_streamgraph,
            'requires': ['matplotlib'],
            'returns': 'image',
            'description': 'StreamGraph - gráfico de área apilada',
            'min_words': 50
        },
        'bubblelines': {
            'func': analyze_bubblelines,
            'requires': ['matplotlib'],
            'returns': 'image',
            'description': 'Bubblelines - líneas con burbujas',
            'min_words': 50
        },
        'mandala': {
            'func': analyze_mandala,
            'requires': ['matplotlib'],
            'returns': 'image',
            'description': 'Mandala - diagrama circular concéntrico',
            'min_words': 100
        },
        'sentiment': {
            'func': analyze_sentiment,
            'requires': [],
            'returns': 'data',
            'description': 'Análisis de sentimiento (positivo/negativo/neutral)',
            'min_words': 10
        },
        'entities': {
            'func': analyze_entities,
            'requires': [],
            'returns': 'data',
            'description': 'Reconocimiento de entidades (emails, URLs, fechas, teléfonos)',
            'min_words': 5
        },
        'category': {
            'func': analyze_category,
            'requires': [],
            'returns': 'data',
            'description': 'Clasificación de texto (informativo, opinión, técnico, narrativo)',
            'min_words': 20
        },
        'summary': {
            'func': analyze_summary,
            'requires': [],
            'returns': 'text',
            'description': 'Resumen extractivo por frecuencia de palabras',
            'min_words': 30
        }
    })


_register_analyzers()
