"""Regression: PipelineTab crashed at construction ('_operations' missing).

PDFBaseTab.__init__ drives _setup_frame(), so any attribute read there must
exist before super().__init__() returns. PipelineTab now adopts the
state-owned list (PDFState.pipeline_operations) instead of publishing its own
after the fact — single source of truth lives in state.
"""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

PT = "tools.pdf_tool.ui.tabs.pipeline_tab"

WIDGET_PATCHES = [
    patch(f"{PT}.ctk.CTkFont"),
    patch(f"{PT}.create_frame", return_value=MagicMock()),
    patch(f"{PT}.create_label", return_value=MagicMock()),
    patch(f"{PT}.create_option_menu", return_value=MagicMock()),
    patch(f"{PT}.create_entry", return_value=MagicMock()),
    patch(f"{PT}.create_button", return_value=MagicMock()),
    patch(f"{PT}.create_textbox", return_value=MagicMock()),
]


@pytest.fixture
def mocked_widgets():
    for p in WIDGET_PATCHES:
        p.start()
    yield
    for p in WIDGET_PATCHES:
        p.stop()


def _make_tab():
    from tools.pdf_tool.ui.tabs.pipeline_tab import PipelineTab

    state = SimpleNamespace(
        pipeline_operations=[],
        ctx=SimpleNamespace(files=[]),
    )
    return PipelineTab(None, MagicMock(), None, state), state


def test_construction_succeeds_and_adopts_state_list(mocked_widgets):
    """Tab must construct without AttributeError and use the state-owned list."""
    tab, state = _make_tab()
    assert tab._operations is state.pipeline_operations


def test_mutations_are_visible_through_state(mocked_widgets):
    """Adding/clearing ops through the tab must be visible in state."""
    tab, state = _make_tab()
    tab._operations.append({"type": "rotate", "params": {"degrees": 90}})
    assert state.pipeline_operations == [
        {"type": "rotate", "params": {"degrees": 90}}
    ]
