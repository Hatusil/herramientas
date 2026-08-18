"""Centralized state for Text Analyzer UI."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from tools.text_tool.ui.phases import PhaseManager, CleanPhase
from tools.text_tool.ui.state_metrics import record_analysis_start, record_analysis_error

__all__ = ["TextAnalyzerState", "record_analysis_start", "record_analysis_error"]


@dataclass
class TextSource:
    content: str
    source_type: str
    source_id: str
    char_count: int = 0
    word_count: int = 0

    def __post_init__(self):
        self.char_count = len(self.content)
        self.word_count = len(self.content.split())


@dataclass
class FilterPipeline:
    raw_text: str = ""
    raw_words: List[str] = field(default_factory=list)
    filtered_words: List[str] = field(default_factory=list)


@dataclass
class TextAnalyzerState:
    sources: Dict[str, List[TextSource]] = field(default_factory=dict)
    filter_pipeline: FilterPipeline = field(default_factory=FilterPipeline)
    cleaned_content: Optional[str] = None
    exclude_words: str = ""
    remove_stopwords: bool = True
    status: str = ""
    status_color: str = "gray"
    is_processing: bool = False
    phase_manager: PhaseManager = field(default_factory=PhaseManager)
    current_tab: str = "📥"
    file_path: Optional[str] = None

    @property
    def text_content(self) -> str:
        parts = []
        for src_list in self.sources.values():
            for src in src_list:
                parts.append(src.content)
        return "\n".join(parts)

    def add_text_source(self, content: str) -> None:
        key = f"text_{uuid.uuid4().hex[:8]}"
        src = TextSource(content=content, source_type="text", source_id=key)
        self.sources.setdefault("text", []).append(src)
        self._update_pipeline()

    def add_file_source(self, path: str, content: str) -> None:
        src = TextSource(content=content, source_type="file", source_id=path)
        self.sources.setdefault("files", []).append(src)
        self._update_pipeline()

    def add_url_source(self, url: str, content: str) -> None:
        src = TextSource(content=content, source_type="url", source_id=url)
        self.sources.setdefault("urls", []).append(src)
        self._update_pipeline()

    def remove_source(self, source_type: str, source_id: str) -> None:
        if source_type in self.sources:
            self.sources[source_type] = [
                s for s in self.sources[source_type] if s.source_id != source_id
            ]
        self._update_pipeline()

    def remove_source_type(self, source_type: str) -> None:
        if source_type in self.sources:
            self.sources[source_type] = []
        self._update_pipeline()

    def _update_pipeline(self) -> None:
        combined = self.text_content
        words = combined.lower().split()
        self.filter_pipeline.raw_text = combined
        self.filter_pipeline.raw_words = words
        self._apply_filters()

    def _filter_stopwords(self, words: List[str]) -> List[str]:
        stopwords = {
            "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las",
            "por", "un", "para", "con", "no", "una", "su", "al", "es", "lo",
            "como", "más", "pero", "sus", "le", "ya", "o", "este", "sí", "porque",
            "esta", "entre", "cuando", "muy", "sin", "sobre", "también", "me",
            "hasta", "hay", "donde", "quien", "desde", "todo", "nos", "durante",
            "ser", "ha", "son", "tiene", "está", "esto", "ese", "eso",
            "fue", "eran", "haya", "tienen", "mismo", "puede",
            "hacer", "ver", "así", "tras", "mientras", "según", "cada", "uno",
            "ella", "tú", "te", "ti", "tu", "mis", "os", "mi",
        }
        return [w for w in words if w.lower() not in stopwords]

    def _apply_filters(self) -> None:
        words = self.filter_pipeline.raw_words
        exclude = self.exclude_words.lower().split(",") if self.exclude_words else []
        exclude = [w.strip() for w in exclude if w.strip()]

        if self.remove_stopwords:
            words = self._filter_stopwords(words)

        if exclude:
            words = [w for w in words if w not in exclude]

        self.filter_pipeline.filtered_words = words
        self.cleaned_content = " ".join(words)

    def apply_stopwords_filter(self, enabled: bool) -> None:
        self.remove_stopwords = enabled
        self._apply_filters()

    def set_exclusions(self, exclusions: str) -> None:
        self.exclude_words = exclusions
        self._apply_filters()

    def clear_analysis(self) -> None:
        from tools.text_tool.ui.analysis import clear_cache
        clear_cache()
        self.is_processing = False

    def reset(self) -> None:
        self.sources = {}
        self.filter_pipeline = FilterPipeline()
        self.cleaned_content = None
        self.is_processing = False
        self.phase_manager.reset()

    def advance_phase(self) -> bool:
        return self.phase_manager.advance()

    def transition_to_phase(self, phase: CleanPhase) -> bool:
        return self.phase_manager.transition_to(phase)

    def can_execute_analysis(self) -> bool:
        return self.phase_manager.can_execute()

    @property
    def current_phase(self) -> CleanPhase:
        return self.phase_manager.current_phase

    @property
    def has_text(self) -> bool:
        return bool(self.text_content and self.text_content.strip())

    def get_source_summary(self) -> str:
        parts = []
        total_chars = 0
        total_words = 0

        for src_type, src_list in self.sources.items():
            if not src_list:
                continue
            chars = sum(s.char_count for s in src_list)
            words = sum(s.word_count for s in src_list)
            total_chars += chars
            total_words += words
            count = len(src_list)
            icon = {"text": "📝", "files": "📄", "urls": "🌐"}.get(src_type, "📁")
            if src_type == "files":
                parts.append(f"{icon} {count} archivo(s): {chars} chars")
            elif src_type == "urls":
                parts.append(f"{icon} {count} URL(s): {chars} chars")
            else:
                parts.append(f"{icon} {count} texto(s): {chars} chars")

        if not parts:
            return "📁 Sin contenido cargado"

        return " | ".join(parts) + f" | TOTAL: {total_chars} chars, {total_words} palabras"

    def sources_summary(self) -> str:
        return self.get_source_summary()
