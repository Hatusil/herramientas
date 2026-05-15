"""
TextAnalyzerTool: Plugin para análisis de texto.
"""
from core.base_tool import BaseTool
from tools.text_tool.ui import TextAnalyzerUI


class TextAnalyzerTool(BaseTool):
    """Herramienta para análisis de texto."""
    
    def __init__(self):
        self.ui = None
    
    def get_name(self) -> str:
        return "Text Analyzer"
    
    def get_icon(self) -> str:
        return "📊"
    
    def get_description(self) -> str:
        return "Análisis de texto: WordCloud, frecuencia, estadísticas, N-grams"
    
    def build_ui(self, parent_frame) -> None:
        self.ui = TextAnalyzerUI(parent_frame, self._on_process)
        self.ui.pack(fill="both", expand=True)
    
    def _on_process(self, action: str, files: list, options: dict) -> dict:
        return self.process(files, options)
    
    def process(self, files: list, options: dict) -> dict:
        from tools.text_tool import processor
        action = options.get('action', 'stats')

        # Get text: from options['text'] or first file content
        text = options.get('text', '')
        if not text and files:
            # Try to read as text file
            try:
                with open(files[0], 'r', encoding='utf-8') as f:
                    text = f.read()
            except Exception:
                return {'success': False, 'error': 'No se pudo leer el archivo de texto'}

        if not text:
            return {'success': False, 'error': 'No hay texto para analizar'}

        # Extract relevant options for each action
        common_opts = {
            'n': options.get('n', 20),
            'remove_stopwords': options.get('remove_stopwords', True),
            'exclude_words': options.get('exclude_words'),
            'already_cleaned': True,  # text from process is raw, let processor clean
        }

        try:
            if action == 'stats':
                return processor.analyze_stats(text)
            elif action == 'frequency':
                return processor.analyze_frequency(
                    text,
                    n=options.get('n', 20),
                    remove_stopwords=options.get('remove_stopwords', True),
                    exclude_words=options.get('exclude_words'),
                    already_cleaned=False
                )
            elif action == 'ngrams':
                return processor.analyze_ngrams(
                    text,
                    n=options.get('n', 2),
                    top_k=options.get('top_k', 20),
                    already_cleaned=False
                )
            elif action == 'wordcloud':
                return processor.analyze_wordcloud(text)
            elif action == 'wordtree':
                return processor.analyze_wordtree_simple(
                    text,
                    phrase=options.get('phrase', ''),
                    max_results=options.get('max_results', 50),
                    already_cleaned=False
                )
            elif action == 'topics':
                return processor.analyze_topics(
                    text,
                    n_topics=options.get('n_topics', 5),
                    already_cleaned=False
                )
            elif action == 'correlations':
                return processor.analyze_correlations(
                    text,
                    min_freq=options.get('min_freq', 3),
                    already_cleaned=False
                )
            elif action == 'scatter':
                return processor.analyze_scatter(text)
            elif action == 'streamgraph':
                return processor.analyze_streamgraph(text)
            elif action == 'bubblelines':
                return processor.analyze_bubblelines(text)
            elif action == 'mandala':
                return processor.analyze_mandala(
                    text,
                    n_terms=options.get('n_terms', 30),
                    n_rings=options.get('n_rings', 5),
                    already_cleaned=False
                )
            elif action == 'kwic':
                return processor.analyze_kwic(
                    text,
                    keyword=options.get('keyword', ''),
                    window=options.get('window', 5),
                    already_cleaned=False
                )
            elif action == 'trends':
                return processor.analyze_trends(text)
            elif action == 'category':
                return processor.analyze_category(
                    text,
                    method=options.get('method', 'simple'),
                    already_cleaned=False
                )
            elif action == 'sentiment':
                return processor.analyze_sentiment(text)
            elif action == 'entities':
                return processor.analyze_entities(text)
            elif action == 'summary':
                return processor.analyze_summary(text)
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}