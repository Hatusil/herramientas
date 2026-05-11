"""Centralized state for Text Analyzer UI."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class TextAnalyzerState:
    """Centralized state for the Text Analyzer application."""

    text_content: str = ""
    cleaned_content: Optional[str] = None
    original_text: str = ""
    sources: Dict[str, List[Any]] = field(
        default_factory=lambda: {"text": [], "files": [], "urls": []}
    )
    exclude_words: str = ""
    remove_stopwords: bool = True
    status: str = ""
    status_color: str = "gray"
    is_processing: bool = False
    current_tab: str = "📥"
    file_path: Optional[str] = None
    last_analysis: Optional[str] = None

    def update_text(self, text: str) -> None:
        """Update text content and track original if empty."""
        self.text_content = text
        if not self.original_text:
            self.original_text = text

    def update_cleaned(self, cleaned: str) -> None:
        """Update cleaned content."""
        self.cleaned_content = cleaned

    def reset(self) -> None:
        """Reset all content to initial state."""
        self.text_content = self.original_text
        self.cleaned_content = None
        self.sources = {"text": [], "files": [], "urls": []}
        self.is_processing = False
        self.last_analysis = None

    @property
    def has_text(self) -> bool:
        """Check if there's text content available."""
        return bool(self.text_content and self.text_content.strip())

    @property
    def sources_summary(self) -> str:
        """Get human-readable summary of sources."""
        text_count = len(self.sources.get("text", []))
        file_count = len(self.sources.get("files", []))
        url_count = len(self.sources.get("urls", []))

        if not text_count and not file_count and not url_count:
            return "📁 Sin contenido cargado"

        parts = []
        if text_count:
            parts.append(f"📝 Txt({text_count})")
        if file_count:
            parts.append(f"📁 Arch({file_count})")
        if url_count:
            parts.append(f"🌐 URLs({url_count})")

        total = text_count + file_count + url_count
        return " + ".join(parts) + f" = {total} total"