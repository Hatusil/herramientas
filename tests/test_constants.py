"""
Tests for core/constants.py
"""
try:
    import pytest
except ImportError:
    pytest = None
    
from pathlib import Path


class TestConstants:
    """Test suite for core/constants.py"""

    def test_project_root_is_path(self):
        """Test that PROJECT_ROOT is a valid Path."""
        from core import constants
        assert isinstance(constants.PROJECT_ROOT, Path)
        assert constants.PROJECT_ROOT.exists()

    def test_core_dir_exists(self):
        """Test that CORE_DIR points to existing directory."""
        from core import constants
        assert constants.CORE_DIR.exists()

    def test_ui_dir_exists(self):
        """Test that UI_DIR points to existing directory."""
        from core import constants
        assert constants.UI_DIR.exists()

    def test_tools_dir_exists(self):
        """Test that TOOLS_DIR points to existing directory."""
        from core import constants
        assert constants.TOOLS_DIR.exists()

    def test_output_dir_exists_or_created(self):
        """Test that OUTPUT_DIR exists or gets created."""
        from core import constants
        # OUTPUT_DIR should be created if not exists
        assert constants.OUTPUT_DIR.exists()

    def test_app_name_is_string(self):
        """Test APP_NAME is a string."""
        from core import constants
        assert isinstance(constants.APP_NAME, str)
        assert len(constants.APP_NAME) > 0

    def test_app_dimensions_are_integers(self):
        """Test app dimensions are positive integers."""
        from core import constants
        assert isinstance(constants.APP_WIDTH, int)
        assert isinstance(constants.APP_HEIGHT, int)
        assert constants.APP_WIDTH > 0
        assert constants.APP_HEIGHT > 0

    def test_sidebar_width_is_integer(self):
        """Test SIDEBAR_WIDTH is a positive integer."""
        from core import constants
        assert isinstance(constants.SIDEBAR_WIDTH, int)
        assert constants.SIDEBAR_WIDTH > 0

    def test_appearance_mode_is_valid(self):
        """Test APPEARANCE_MODE is valid."""
        from core import constants
        assert constants.APPEARANCE_MODE in ['dark', 'light', 'system']

    def test_audio_lufs_is_negative(self):
        """Test DEFAULT_LUFS is a negative number (dB)."""
        from core import constants
        assert isinstance(constants.DEFAULT_LUFS, (int, float))
        assert constants.DEFAULT_LUFS < 0

    def test_tool_status_constants_are_strings(self):
        """Test TOOL_STATUS constants are defined."""
        from core import constants
        assert constants.TOOL_STATUS_OK == "OK"
        assert constants.TOOL_STATUS_ERROR == "ERROR"
        assert constants.TOOL_STATUS_LOADING == "LOADING"