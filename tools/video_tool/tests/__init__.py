"""
Tests for video_tool.processor module - video conversion skip logic.
"""
import pytest
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from processor import convert_video


class TestVideoConvertSkipLogic:
    """Tests for video conversion skip logic."""

    def test_video_convert_skip_same_format(self, tmp_path):
        """Converting MP4 to MP4 should skip the file when same codec."""
        test_file = tmp_path / "test.mp4"
        test_file.write_bytes(b"fake mp4 content for testing")

        result = convert_video([str(test_file)], "mp4")

        assert result['success'] is False
        assert 'skipped' in result
        assert len(result['skipped']) == 1
        assert 'Ya está en formato MP4' in result['skipped'][0]

    def test_video_convert_skips_mkv_same_format(self, tmp_path):
        """Converting MKV to MKV should skip."""
        test_file = tmp_path / "test.mkv"
        test_file.write_bytes(b"fake mkv content for testing")

        result = convert_video([str(test_file)], "mkv")

        assert result['success'] is False
        assert 'skipped' in result

    def test_video_convert_different_format(self, tmp_path):
        """Converting MP4 to AVI should proceed."""
        test_file = tmp_path / "test.mp4"
        test_file.write_bytes(b"fake mp4 content for testing")

        result = convert_video([str(test_file)], "avi")

        assert result['success'] is True
        assert len(result['output_files']) == 1