"""
RenameTool: Plugin para renombrar archivos en masa.
"""
from core.base_tool import BaseTool


class RenameTool(BaseTool):
    """Herramienta para renombrar archivos."""
    
    def __init__(self):
        self.ui = None
    
    def get_name(self) -> str:
        return "Renombrar"
    
    def get_icon(self) -> str:
        return "✏️"
    
    def get_description(self) -> str:
        return "Renombrar archivos en masa"
    
    def build_ui(self, parent_frame) -> None:
        from tools.rename_tool.ui import RenameToolUI
        self.ui = RenameToolUI(parent_frame, self._on_process)
        self.ui.pack(fill="both", expand=True)
    
    def _on_process(self, action: str, files: list, options: dict) -> dict:
        return self.process(files, options)
    
    def process(self, files: list, options: dict) -> dict:
        from tools.rename_tool import processor
        action = options.get('action', 'prefix')
        
        if action == 'prefix':
            return processor.rename_with_prefix(files, options.get('prefix', ''))
        elif action == 'suffix':
            return processor.rename_with_suffix(files, options.get('suffix', ''))
        elif action == 'replace':
            return processor.rename_replace(
                files, options.get('find', ''), options.get('replace', ''))
        elif action == 'numbered':
            return processor.rename_numbered(
                files, options.get('start', 1), options.get('pattern', '{name}_{n}'))
        elif action == 'case':
            return processor.rename_case(files, options.get('case', 'lower'))
        elif action == 'regex':
            return processor.rename_regex(
                files, options.get('pattern', ''), options.get('replace', ''))
        else:
            return {'success': False, 'error': f'Unknown action: {action}'}