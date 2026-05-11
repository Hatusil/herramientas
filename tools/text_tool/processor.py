"""
TextAnalyzerProcessor: Procesamiento de análisis de texto.

Este módulo es un HUB DE RE-EXPORT para backwards compatibility.
El código real está en tools/text_tool/processors/.

Para imports directos:
    from tools.text_tool.processors import analyze_frequency, analyze_wordcloud, ...

Para backwards compatibility (旧 código que importa de processor.py):
    from tools.text_tool import processor
    processor.analyze_frequency(...)  # Funciona igual
"""

# Re-export todo desde processors para backwards compatibility
from tools.text_tool.processors import (
    # frequency
    analyze_frequency,
    analyze_ngrams,
    analyze_stats,
    # wordcloud
    analyze_wordcloud,
    # wordtree
    analyze_wordtree_simple,
    analyze_wordtree,
    # topics
    analyze_topics,
    # correlations
    analyze_correlations,
    # scatter
    analyze_scatter,
    # streamgraph
    analyze_streamgraph,
    # bubblelines
    analyze_bubblelines,
    # mandala
    analyze_mandala,
    # category
    analyze_category,
    analyze_sentiment,
    analyze_entities,
    analyze_summary,
    # trends
    analyze_trends,
    # extractors
    extract_text_from_file,
    extract_text_from_url,
    # utils
    check_text_size,
    process_in_chunks,
    ANALYZER_REGISTRY,
    get_analyzer,
    list_analyzers,
    get_analyzer_info,
    check_dependencies,
    get_text_stats,
    validate_text,
    NLTK_AVAILABLE,
    WORDCLOUD_AVAILABLE,
    PDFPLUMBER_AVAILABLE,
    DOCX_AVAILABLE,
    XLXS_AVAILABLE,
    REQUESTS_AVAILABLE,
    SKLEARN_AVAILABLE,
)

# Metadata
__all__ = [
    'analyze_frequency', 'analyze_ngrams', 'analyze_stats',
    'analyze_wordcloud',
    'analyze_wordtree_simple', 'analyze_wordtree',
    'analyze_topics',
    'analyze_correlations',
    'analyze_scatter',
    'analyze_streamgraph',
    'analyze_bubblelines',
    'analyze_mandala',
    'analyze_category', 'analyze_sentiment', 'analyze_entities', 'analyze_summary',
    'analyze_trends',
    'extract_text_from_file', 'extract_text_from_url',
    'check_text_size', 'process_in_chunks',
    'ANALYZER_REGISTRY', 'get_analyzer', 'list_analyzers', 'get_analyzer_info',
    'check_dependencies', 'get_text_stats', 'validate_text',
    'NLTK_AVAILABLE', 'WORDCLOUD_AVAILABLE', 'PDFPLUMBER_AVAILABLE',
    'DOCX_AVAILABLE', 'XLXS_AVAILABLE', 'REQUESTS_AVAILABLE', 'SKLEARN_AVAILABLE',
]