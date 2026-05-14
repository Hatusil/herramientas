"""
VideoTool: Plugin para procesamiento básico de video.
"""
from core.base_tool import BaseTool


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
        from tools.video_tool.ui import VideoToolUI
        self.ui = VideoToolUI(parent_frame, self._on_process)
        self.ui.pack(fill="both", expand=True)
    
    def _on_process(self, action: str, files: list, options: dict) -> dict:
        return self.process(files, options)
    
    def process(self, files: list, options: dict) -> dict:
        from tools.video_tool import processor
        action = options.get('action', 'audio')
        
        if action == 'audio':
            if not files:
                return {'success': False, 'error': 'No hay archivo de video'}
            return processor.extract_audio(
                files[0], options.get('output_format', 'mp3'))
        elif action == 'convert':
            return processor.convert_video(
                files, options.get('output_format', 'mp4'), **options)
        elif action == 'info':
            if not files:
                return {'success': False, 'error': 'No hay archivo de video'}
            return processor.get_video_info(files[0])
        else:
            return {'success': False, 'error': f'Unknown action: {action}'}