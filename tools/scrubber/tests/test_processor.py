"""
Tests for scrubber.processor module.
"""
import pytest

from tools.scrubber.processor import get_image_metadata, clean_image_metadata, MAX_SCRUB_SIZE_MB


class TestImageMetadata:
    """Tests for image metadata functions."""

    def test_get_image_metadata_returns_dict(self):
        """get_image_metadata returns dict structure."""
        result = get_image_metadata("/nonexistent.jpg")
        
        assert isinstance(result, dict)
        assert 'success' in result

    def test_get_image_metadata_nonexistent(self, tmp_path):
        """get_image_metadata handles nonexistent file."""
        result = get_image_metadata(str(tmp_path / "nonexistent.jpg"))
        
        assert result['success'] is False


class TestCleanImageMetadata:
    """Tests for clean_image_metadata function."""

    def test_clean_image_metadata_returns_dict(self, tmp_path):
        """clean_image_metadata returns dict structure."""
        # Create fake image file
        fake_image = tmp_path / "test.jpg"
        fake_image.write_bytes(b"fake jpg")

        result = clean_image_metadata(str(fake_image), {})

        assert isinstance(result, dict)
        assert 'success' in result

    def test_clean_image_metadata_nonexistent(self):
        """clean_image_metadata handles nonexistent file."""
        result = clean_image_metadata("/nonexistent/file.jpg", {})

        assert result['success'] is False


class TestConstants:
    """Tests for module constants."""

    def test_max_scrub_size_is_int(self):
        """MAX_SCRUB_SIZE_MB should be an integer."""
        assert isinstance(MAX_SCRUB_SIZE_MB, int)
        assert MAX_SCRUB_SIZE_MB > 0