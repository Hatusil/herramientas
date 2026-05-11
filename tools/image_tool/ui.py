"""
Image Tool UI - Interfaz de usuario para procesamiento de imágenes.

Este módulo es un HUB DE RE-EXPORT para backwards compatibility.
El código real está en tools/image_tool/ui/.

Para imports directos:
    from tools.image_tool.ui import ImageToolUI

Para backwards compatibility (código旧 que importa de image_tool.ui):
    from tools.image_tool import ui
    ui.ImageToolUI(...)  # Funciona igual
"""

from tools.image_tool.ui import ImageToolUI

__all__ = ['ImageToolUI']