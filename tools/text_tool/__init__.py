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
        return {'success': True, 'message': 'UI handles directly'}
    
    def process(self, files: list, options: dict) -> dict:
        return {'success': True, 'message': 'UI handles directly'}