"""Phases module for text_tool UI."""
from __future__ import annotations

from tools.text_tool.ui.phases.clean_phase import (
    CleanPhase,
    can_transition,
    get_next_phase,
    VALID_TRANSITIONS,
)
from tools.text_tool.ui.phases.phase_manager import PhaseManager

__all__ = [
    "CleanPhase",
    "can_transition",
    "get_next_phase",
    "VALID_TRANSITIONS",
    "PhaseManager",
]