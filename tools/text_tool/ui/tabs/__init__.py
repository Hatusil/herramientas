"""Tab registry and exports for Text Analyzer UI."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from tools.text_tool.ui.tabs.base_tab import BaseTab

# Import all tab classes for registration
from tools.text_tool.ui.tabs.base_tab import BaseTab
from tools.text_tool.ui.tabs.input_tab import InputTab
from tools.text_tool.ui.tabs.clean_tab import CleanTab
from tools.text_tool.ui.tabs.stats_tab import StatsTab
from tools.text_tool.ui.tabs.freq_tab import FreqTab
from tools.text_tool.ui.tabs.trends_tab import TrendsTab
from tools.text_tool.ui.tabs.ngrams_tab import NgramsTab
from tools.text_tool.ui.tabs.scatter_tab import ScatterTab
from tools.text_tool.ui.tabs.corr_tab import CorrTab
from tools.text_tool.ui.tabs.streamgraph_tab import StreamGraphTab
from tools.text_tool.ui.tabs.bubblelines_tab import BubblelinesTab
from tools.text_tool.ui.tabs.mandala_tab import MandalaTab
from tools.text_tool.ui.tabs.wc_tab import WCTab
from tools.text_tool.ui.tabs.kwic_tab import KwicTab
from tools.text_tool.ui.tabs.topics_tab import TopicsTab
from tools.text_tool.ui.tabs.wordtree_tab import WordTreeTab

__all__ = [
    "BaseTab",
    "InputTab",
    "CleanTab",
    "StatsTab",
    "FreqTab",
    "NgramsTab",
    "TrendsTab",
    "ScatterTab",
    "CorrTab",
    "StreamGraphTab",
    "BubblelinesTab",
    "MandalaTab",
    "WCTab",
    "KwicTab",
    "TopicsTab",
    "WordTreeTab",
    "TAB_REGISTRY",
]

# Registry of available tabs (populated when tabs are imported)
TAB_REGISTRY: dict[str, type] = {}


def register_tab(name: str, tab_class: type) -> None:
    """Register a tab class in the global registry."""
    TAB_REGISTRY[name] = tab_class


def get_tab(name: str) -> Optional[type]:
    """Get a tab class by name."""
    return TAB_REGISTRY.get(name)


# Auto-register all tabs
register_tab("input", InputTab)
register_tab("clean", CleanTab)
register_tab("stats", StatsTab)
register_tab("freq", FreqTab)
register_tab("trends", TrendsTab)
register_tab("ngrams", NgramsTab)
register_tab("scatter", ScatterTab)
register_tab("corr", CorrTab)
register_tab("streamgraph", StreamGraphTab)
register_tab("bubblelines", BubblelinesTab)
register_tab("mandala", MandalaTab)
register_tab("wc", WCTab)
register_tab("kwic", KwicTab)
register_tab("topics", TopicsTab)
register_tab("wordtree", WordTreeTab)