"""Text Analyzer UI module.

Re-exports from main_ui for backward compatibility.
"""
from __future__ import annotations

# Re-export main_ui components
from tools.text_tool.ui.main_ui import TextAnalyzerUI

# Re-export state, callbacks, and constants
from tools.text_tool.ui.state import TextAnalyzerState
from tools.text_tool.ui.callbacks import AppCallbacks
from tools.text_tool.ui.constants import SUBTOOL_INFO

__all__ = [
    "TextAnalyzerUI",
    "TextAnalyzerState",
    "AppCallbacks",
    "SUBTOOL_INFO",
]