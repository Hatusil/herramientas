"""
HashTool: Plugin para calcular y verificar checksums.
"""
import logging
from typing import List, Dict, Any

from core.base_tool import BaseTool
from tools.hash_tool import processor
from tools.hash_tool.ui import HashToolUI


logger = logging.getLogger(__name__)


class HashTool(BaseTool):
    """Herramienta para calcular y verificar hashes."""
    
    def __init__(self):
        self.ui = None
    
    def get_name(self) -> str:
        return "Hash"
    
    def get_icon(self) -> str:
        return "#️⃣"
    
    def get_description(self) -> str:
        return "Calcular y verificar MD5, SHA1, SHA256"
    
    def build_ui(self, parent_frame) -> None:
        self.ui = HashToolUI(parent_frame, self._on_process)
        self.ui.pack(fill="both", expand=True)
    
    def _on_process(self, action: str, files: List[str], options: Dict[str, Any]) -> Dict[str, Any]:
        return {'success': True, 'message': 'UI handles actions directly'}
    
    def process(self, files: List[str], options: Dict[str, Any]) -> Dict[str, Any]:
        return {'success': True, 'message': 'UI handles actions directly'}