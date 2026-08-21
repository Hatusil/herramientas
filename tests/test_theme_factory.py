"""Regression tests: theme factory must let caller kwargs override theme defaults.

Bug: create_frame/create_button hardcoded theme colors alongside **kwargs, so any
caller passing its own fg_color crashed with
"CTkFrame() got multiple values for keyword argument 'fg_color'".
Every helper is now override-safe; the sweep below locks that contract in.
"""
from unittest.mock import patch

import pytest

from ui import theme_factory

PROBE_COLOR = "#0f0f0f"
_NOOP = lambda: None  # noqa: E731

# (helper, CTk widget class, extra positional args, probe kwarg, COLORS key for default)
SWEEP = [
    ("create_button", "CTkButton", ("t", _NOOP), "fg_color", "button_fg"),
    ("create_primary_button", "CTkButton", ("t", _NOOP), "fg_color", "primary"),
    ("create_tool_button", "CTkButton", ("t", _NOOP), "fg_color", "bg_medium"),
    ("create_bordered_button", "CTkButton", ("t", _NOOP), "border_color", "border"),
    ("create_danger_button", "CTkButton", ("t", _NOOP), "fg_color", "error"),
    ("create_secondary_label", "CTkLabel", (), "text_color", "text_secondary"),
    ("create_muted_label", "CTkLabel", (), "text_color", "text_muted"),
    ("create_frame", "CTkFrame", (), "fg_color", "bg_light"),
    ("create_panel", "CTkFrame", (), "fg_color", "bg_medium"),
    ("create_border_frame", "CTkFrame", (), "border_color", "border"),
    ("create_control_frame", "CTkFrame", (), "border_color", "border"),
    ("create_divider", "CTkFrame", (), "fg_color", "border"),
    ("create_card", "CTkFrame", (), "fg_color", "bg_light"),
    ("create_entry", "CTkEntry", (), "fg_color", "bg_input"),
    ("create_textbox", "CTkTextbox", (), "fg_color", "bg_input"),
    ("create_switch", "CTkSwitch", (), "fg_color", "bg_hover"),
    ("create_checkbox", "CTkCheckBox", (), "fg_color", "primary"),
    ("create_radiobutton", "CTkRadioButton", (), "fg_color", "primary"),
    ("create_progress_bar", "CTkProgressBar", (), "progress_color", "primary"),
    ("create_slider", "CTkSlider", (), "button_color", "primary"),
    ("create_scrollable_frame", "CTkScrollableFrame", (), "label_fg_color", "bg_medium"),
    ("create_tabview", "CTkTabview", (), "fg_color", "bg_light"),
    ("create_option_menu", "CTkOptionMenu", (), "button_color", "button_fg"),
    ("create_combo_box", "CTkComboBox", (), "button_color", "button_fg"),
]


@pytest.mark.parametrize("name,widget,args,key,default_key", SWEEP)
def test_override_wins_over_theme_default(name, widget, args, key, default_key):
    """Caller-supplied theme kwarg must reach the widget exactly once."""
    fn = getattr(theme_factory, name)
    with patch.object(theme_factory.ctk, widget) as cls:
        fn(None, *args, **{key: PROBE_COLOR})
        _, kwargs = cls.call_args
    assert kwargs[key] == PROBE_COLOR


@pytest.mark.parametrize("name,widget,args,key,default_key", SWEEP)
def test_theme_default_applies_without_override(name, widget, args, key, default_key):
    """Without caller override, the theme default still applies."""
    fn = getattr(theme_factory, name)
    with patch.object(theme_factory.ctk, widget) as cls:
        fn(None, *args)
        _, kwargs = cls.call_args
    assert kwargs[key] == theme_factory.COLORS.get(default_key)


def test_create_frame_allows_fg_color_override():
    """Caller-supplied fg_color must reach CTkFrame exactly once (original bug)."""
    with patch.object(theme_factory.ctk, "CTkFrame") as frame_cls:
        theme_factory.create_frame(None, fg_color="transparent")
    _, kwargs = frame_cls.call_args
    assert kwargs["fg_color"] == "transparent"


def test_create_button_allows_multi_key_override():
    """Multiple simultaneous overrides must all win (pipeline_tab use case)."""
    with patch.object(theme_factory.ctk, "CTkButton") as button_cls:
        theme_factory.create_button(
            None, text="x", command=lambda: None,
            fg_color="#123456", hover_color="#654321",
        )
    _, kwargs = button_cls.call_args
    assert kwargs["fg_color"] == "#123456"
    assert kwargs["hover_color"] == "#654321"
