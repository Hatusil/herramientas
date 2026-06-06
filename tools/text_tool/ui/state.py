"""Centralized state for Text Analyzer UI."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from collections import Counter

from core.metrics import Counter, Timer

from tools.text_tool.ui.phases import PhaseManager, CleanPhase

# A12: observability - metrics at module level
_analyses_run = Counter("text_analyzer.analyses_run")
_analyses_errors = Counter("text_analyzer.errors")
_duration_timer = Timer("text_analyzer.duration")


def get_analyses_metrics() -> Dict[str, int]:
    """Return current metrics values. A12 observability."""
    return {
        "analyses_run": _analyses_run.value,
        "errors": _analyses_errors.value,
    }


def record_analysis_start() -> None:
    """Record analysis start. A12 observability."""
    _analyses_run.increment()


def record_analysis_error() -> None:
    """Record analysis error. A12 observability."""
    _analyses_errors.increment()


@dataclass
class TextSource:
    """Representa una fuente de texto con metadatos."""
    content: str
    source_type: str  # "text", "file", "url"
    source_id: str    # path, url, o key
    char_count: int = 0
    word_count: int = 0
    
    def __post_init__(self):
        self.char_count = len(self.content)
        self.word_count = len(self.content.split())


@dataclass
class FilterPipeline:
    """Pipeline de filtros progresivos."""
    raw_text: str = ""
    raw_words: List[str] = field(default_factory=list)
    filtered_words: List[str] = field(default_factory=list)
    applied_filters: List[str] = field(default_factory=list)


@dataclass
class TextAnalyzerState:
    """Centralized state for the Text Analyzer application."""

    # Fuentes discriminadas
    sources: Dict[str, List[TextSource]] = field(default_factory=dict)
    
    # Pipeline de filtros (preserva bruto)
    filter_pipeline: FilterPipeline = field(default_factory=FilterPipeline)
    
    # Texto limpio (resultado del pipeline)
    cleaned_content: Optional[str] = None
    
    # Metadatos legacy
    original_text: str = ""
    exclude_words: str = ""
    remove_stopwords: bool = True
    status: str = ""
    status_color: str = "gray"
    is_processing: bool = False
    phase_manager: PhaseManager = field(default_factory=PhaseManager)
    current_tab: str = "📥"
    file_path: Optional[str] = None
    last_analysis: Optional[str] = None

    @property
    def text_content(self) -> str:
        """Get combined text from all sources."""
        parts = []
        for src_list in self.sources.values():
            for src in src_list:
                parts.append(src.content)
        return "\n".join(parts)

    def add_text_source(self, content: str) -> None:
        """Add text content."""
        import uuid
        key = f"text_{uuid.uuid4().hex[:8]}"
        src = TextSource(content=content, source_type="text", source_id=key)
        self.sources.setdefault("text", []).append(src)
        self._update_pipeline()

    def add_file_source(self, path: str, content: str) -> None:
        """Add file content."""
        src = TextSource(content=content, source_type="file", source_id=path)
        self.sources.setdefault("files", []).append(src)
        self._update_pipeline()

    def add_url_source(self, url: str, content: str) -> None:
        """Add URL content."""
        src = TextSource(content=content, source_type="url", source_id=url)
        self.sources.setdefault("urls", []).append(src)
        self._update_pipeline()

    def remove_source(self, source_type: str, source_id: str) -> None:
        """Remove a specific source."""
        if source_type in self.sources:
            self.sources[source_type] = [
                s for s in self.sources[source_type] if s.source_id != source_id
            ]
        self._update_pipeline()

    def remove_source_type(self, source_type: str) -> None:
        """Remove all sources of a type."""
        if source_type in self.sources:
            self.sources[source_type] = []
        self._update_pipeline()

    def _update_pipeline(self) -> None:
        """Update the filter pipeline with current sources."""
        combined = self.text_content
        words = combined.lower().split()
        self.filter_pipeline.raw_text = combined
        self.filter_pipeline.raw_words = words
        # Re-apply filters
        self._apply_filters()

    def _filter_stopwords(self, words: List[str]) -> List[str]:
        """Filter stopwords from word list."""
        # Basic Spanish stopwords
        stopwords = {
            "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las",
            "por", "un", "para", "con", "no", "una", "su", "al", "es", "lo",
            "como", "más", "pero", "sus", "le", "ya", "o", "este", "sí", "porque",
            "esta", "entre", "cuando", "muy", "sin", "sobre", "también", "me",
            "hasta", "hay", "donde", "quien", "desde", "todo", "nos", "durante",
            "ser", "ha", "son", "tiene", "está", "esto", "ese", "eso", "está",
            "fue", "eran", "sea", "haya", "sea", "tienen", "mismo", "puede",
            "hacer", "ver", "así", "tras", "mientras", "según", "cada", "uno",
            "ella", "tú", "te", "ti", "tu", "su", "mis", "nos", "os", "mi",
        }
        return [w for w in words if w.lower() not in stopwords]

    def _apply_filters(self) -> None:
        """Apply current filters to raw words."""
        words = self.filter_pipeline.raw_words
        exclude = self.exclude_words.lower().split(",") if self.exclude_words else []
        exclude = [w.strip() for w in exclude if w.strip()]
        
        # Apply stopwords
        if self.remove_stopwords:
            words = self._filter_stopwords(words)
        
        # Apply exclusions
        if exclude:
            words = [w for w in words if w not in exclude]
        
        self.filter_pipeline.filtered_words = words
        self.cleaned_content = " ".join(words)

    def apply_stopwords_filter(self, enabled: bool) -> None:
        """Toggle stopwords filter."""
        self.remove_stopwords = enabled
        self._apply_filters()

    def set_exclusions(self, exclusions: str) -> None:
        """Set exclusion words."""
        self.exclude_words = exclusions
        self._apply_filters()

    def clear_analysis(self) -> None:
        """Clear analysis results and cache before running a new analysis.
        
        This ensures previous results don't interfere with new analysis.
        Called before executing analysis from CleanTab.
        """
        from tools.text_tool.ui.analysis import clear_cache
        self.last_analysis = None
        clear_cache()
        self.is_processing = False

    def reset(self) -> None:
        """Reset all content."""
        self.sources = {}
        self.filter_pipeline = FilterPipeline()
        self.cleaned_content = None
        self.is_processing = False
        self.last_analysis = None
        self.phase_manager.reset()

    # Phase transition methods (delegate to phase_manager)
    def advance_phase(self) -> bool:
        """Advance to next phase."""
        return self.phase_manager.advance()

    def transition_to_phase(self, phase: CleanPhase) -> bool:
        """Transition to specific phase."""
        return self.phase_manager.transition_to(phase)

    def can_execute_analysis(self) -> bool:
        """Check if analysis execution is allowed."""
        return self.phase_manager.can_execute()

    @property
    def current_phase(self) -> CleanPhase:
        """Get current phase."""
        return self.phase_manager.current_phase

    @property
    def has_text(self) -> bool:
        """Check if there's text content."""
        return bool(self.text_content and self.text_content.strip())

    def get_source_summary(self) -> str:
        """Get detailed summary of sources."""
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
        """Legacy compatibility."""
        return self.get_source_summary()


@dataclass
class CleanPhaseState:
    """State tracking for CleanTab phase transitions."""

    current_phase: str = "SELECT"  # SELECT, RAW, FILTER, EXECUTE
    raw_created: bool = False
    filters_applied: bool = False
    can_execute: bool = False

    def transition_to(self, phase: str) -> None:
        """Transition to a new phase with validation."""
        valid_transitions = {
            "SELECT": ["RAW"],
            "RAW": ["FILTER"],
            "FILTER": ["EXECUTE"],
            "EXECUTE": [],
        }
        if phase in valid_transitions.get(self.current_phase, []):
            self.current_phase = phase

    def reset(self) -> None:
        """Reset to initial phase."""
        self.current_phase = "SELECT"
        self.raw_created = False
        self.filters_applied = False
        self.can_execute = False