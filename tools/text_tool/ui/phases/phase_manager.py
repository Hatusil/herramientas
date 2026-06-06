"""Phase manager for CleanTab state transitions."""
from __future__ import annotations
import logging

from tools.text_tool.ui.phases.clean_phase import (
    CleanPhase,
    can_transition,
    get_next_phase,
)

logger = logging.getLogger(__name__)


class PhaseManager:
    """Manages CleanTab phase transitions with validation."""

    def __init__(self) -> None:
        self._current_phase: CleanPhase = CleanPhase.SELECT

    @property
    def current_phase(self) -> CleanPhase:
        """Get current phase."""
        return self._current_phase

    @property
    def phase_name(self) -> str:
        """Get human-readable phase name."""
        names = {
            CleanPhase.SELECT: "SELECT",
            CleanPhase.CREATE_RAW: "CREATE_RAW",
            CleanPhase.PREVIEW: "PREVIEW",
            CleanPhase.EXECUTE: "EXECUTE",
        }
        return names.get(self._current_phase, "UNKNOWN")

    def transition_to(self, new_phase: CleanPhase) -> bool:
        """Attempt to transition to a new phase.
        
        Returns True if transition succeeded, False otherwise.
        """
        if can_transition(self._current_phase, new_phase):
            logger.info(f"Phase transition: {self.phase_name} → {new_phase.name}")
            self._current_phase = new_phase
            return True
        logger.warning(
            f"Invalid transition: {self.phase_name} → {new_phase.name}"
        )
        return False

    def advance(self) -> bool:
        """Advance to next phase automatically.
        
        Returns True if advanced, False if already at final phase.
        """
        next_phase = get_next_phase(self._current_phase)
        if next_phase:
            self._current_phase = next_phase
            return True
        return False

    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        return self._current_phase == CleanPhase.EXECUTE

    def reset(self) -> None:
        """Reset to initial SELECT phase."""
        self._current_phase = CleanPhase.SELECT

    def is_phase(self, phase: CleanPhase) -> bool:
        """Check if currently in a specific phase."""
        return self._current_phase == phase

    def requires_source(self) -> bool:
        """Check if current phase requires a source to be selected."""
        return self._current_phase in (CleanPhase.SELECT,)

    def requires_raw(self) -> bool:
        """Check if current phase requires raw text to be created."""
        return self._current_phase == CleanPhase.CREATE_RAW

    def requires_filters(self) -> bool:
        """Check if current phase requires filters to be applied."""
        return self._current_phase in (CleanPhase.PREVIEW,)