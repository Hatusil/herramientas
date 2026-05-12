"""
Text Analyzer Processors - Módulos especializados por responsabilidad.

Este paquete contiene los analizadores de texto organizados por tipo:
- frequency: analyze_frequency, analyze_ngrams, analyze_stats
- wordcloud: analyze_wordcloud
- wordtree: analyze_wordtree_simple, analyze_wordtree
- topics: analyze_topics (LDA)
- correlations: analyze_correlations
- scatter: analyze_scatter
- streamgraph: analyze_streamgraph
- bubblelines: analyze_bubblelines
- mandala: analyze_mandala
- category: analyze_category, analyze_sentiment, analyze_entities, analyze_summary
- extractors: extract_text_from_file, extract_text_from_url

Backward compatibility: todas las funciones también se importan desde el módulo padre.
"""

# Re-export todo para backwards compatibility
from tools.text_tool.processors.frequency import (
    analyze_frequency,
    analyze_ngrams,
    analyze_stats,
)

from tools.text_tool.processors.wordcloud import (
    analyze_wordcloud,
)

from tools.text_tool.processors.wordtree import (
    analyze_wordtree_simple,
    analyze_wordtree,
)

from tools.text_tool.processors.topics import (
    analyze_topics,
)

from tools.text_tool.processors.correlations import (
    analyze_correlations,
)

from tools.text_tool.processors.scatter import (
    analyze_scatter,
)

from tools.text_tool.processors.streamgraph import (
    analyze_streamgraph,
)

from tools.text_tool.processors.bubblelines import (
    analyze_bubblelines,
)

from tools.text_tool.processors.mandala import (
    analyze_mandala,
)

from tools.text_tool.processors.category import (
    analyze_category,
    analyze_sentiment,
    analyze_entities,
    analyze_summary,
)

from tools.text_tool.processors.trends import (
    analyze_trends,
)

from tools.text_tool.processors.kwic import (
    analyze_kwic,
)

# Re-export extractors
from tools.text_tool.processors.extractors import (
    extract_text_from_file,
    extract_text_from_url,
)

# Re-export utils
from tools.text_tool.processors.utils import (
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

__all__ = [
    # frequency
    'analyze_frequency',
    'analyze_ngrams',
    'analyze_stats',
    # wordcloud
    'analyze_wordcloud',
    # wordtree
    'analyze_wordtree_simple',
    'analyze_wordtree',
    # topics
    'analyze_topics',
    # correlations
    'analyze_correlations',
    # scatter
    'analyze_scatter',
    # streamgraph
    'analyze_streamgraph',
    # bubblelines
    'analyze_bubblelines',
    # mandala
    'analyze_mandala',
    # category
    'analyze_category',
    'analyze_sentiment',
    'analyze_entities',
    'analyze_summary',
    # trends
    'analyze_trends',
    # kwic
    'analyze_kwic',
    # extractors
    'extract_text_from_file',
    'extract_text_from_url',
    # utils
    'check_text_size',
    'process_in_chunks',
    'ANALYZER_REGISTRY',
    'get_analyzer',
    'list_analyzers',
    'get_analyzer_info',
    'check_dependencies',
    'get_text_stats',
    'validate_text',
    'NLTK_AVAILABLE',
    'WORDCLOUD_AVAILABLE',
    'PDFPLUMBER_AVAILABLE',
    'DOCX_AVAILABLE',
    'XLXS_AVAILABLE',
    'REQUESTS_AVAILABLE',
    'SKLEARN_AVAILABLE',
]