"""
Audio Tool UI - Interfaz de usuario para procesamiento de audio.

Este módulo es un HUB DE RE-EXPORT para backwards compatibility.
El código real está en tools/audio_tool/ui/.

Para imports directos:
    from tools.audio_tool.ui import AudioToolUI

Para backwards compatibility (código旧 que importa de audio_tool.ui):
    from tools.audio_tool import ui
    ui.AudioToolUI(...)  # Funciona igual
"""

from tools.audio_tool.ui import AudioToolUI

__all__ = ['AudioToolUI']