"""
VideoTool: Plugin para procesamiento básico de video.
"""
from core.base_tool import BaseTool
from tools.video_tool.ui import VideoToolUI


class VideoTool(BaseTool):
    """Herramienta para video."""
    
    def __init__(self):
        self.ui = None
    
    def get_name(self) -> str:
        return "Video"
    
    def get_icon(self) -> str:
        return "🎬"
    
    def get_description(self) -> str:
        return "Extraer audio y convertir videos"
    
    def build_ui(self, parent_frame) -> None:
        self.ui = VideoToolUI(parent_frame, self._on_process)
        self.ui.pack(fill="both", expand=True)
    
    def _on_process(self, action: str, files: list, options: dict) -> dict:
        return {'success': True, 'message': 'UI handles directly'}
    
    def process(self, files: list, options: dict) -> dict:
        return {'success': True, 'message': 'UI handles directly'}