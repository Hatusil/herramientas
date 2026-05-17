"""
Tests for image_tool.processor module.
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from processor import _ok, _fail, _image_to_dict, CV2_AVAILABLE


class TestImageHelpers:
    """Tests for helper functions."""

    def test_ok_returns_success(self):
        """_ok helper returns success dict."""
        result = _ok("test message")
        assert result['success'] is True
        assert result['message'] == "test message"

    def test_fail_returns_error(self):
        """_fail helper returns error dict."""
        result = _fail("test error")
        assert result['success'] is False
        assert 'test error' in result['error']

    def test_image_to_dict_format(self):
        """_image_to_dict returns expected format."""
        # Mock image without actual image processing
        mock_image = "mock_image_data"
        result = _image_to_dict(mock_image)
        assert 'image' in result
        assert result['image'] == mock_image


class TestImageAvailability:
    """Tests for library availability."""

    def test_cv2_available_is_bool(self):
        """CV2_AVAILABLE should be a boolean."""
        assert isinstance(CV2_AVAILABLE, bool)