"""Clean tab phase enum and state machine."""
from __future__ import annotations
from enum import Enum, auto


class CleanPhase(Enum):
    """Phases for CleanTab state machine."""
    SELECT = auto()      # Select source (text/files/URLs)
    CREATE_RAW = auto()  # Create raw text from source
    PREVIEW = auto()     # Show top 20 words preview
    EXECUTE = auto()     # Ready to execute (button enabled after filters)


# Valid phase transitions (manual UI flow — user can click any button)
VALID_TRANSITIONS: dict[CleanPhase, list[CleanPhase]] = {
    CleanPhase.SELECT: [CleanPhase.CREATE_RAW, CleanPhase.PREVIEW, CleanPhase.EXECUTE],
    CleanPhase.CREATE_RAW: [CleanPhase.PREVIEW],
    CleanPhase.PREVIEW: [CleanPhase.EXECUTE],
    CleanPhase.EXECUTE: [CleanPhase.PREVIEW, CleanPhase.EXECUTE],
}


def can_transition(from_phase: CleanPhase, to_phase: CleanPhase) -> bool:
    """Check if transition from one phase to another is valid."""
    return to_phase in VALID_TRANSITIONS.get(from_phase, [])


def get_next_phase(current: CleanPhase) -> CleanPhase | None:
    """Get the next valid phase from current, or None."""
    transitions = VALID_TRANSITIONS.get(current, [])
    return transitions[0] if transitions else None