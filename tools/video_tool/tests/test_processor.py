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
    """Tests for video conversion skip logic.
    
    Note: Video skip logic requires get_video_info() to return success=True.
    When ffprobe fails, conversion is attempted instead of skipping.
    """

    def test_video_convert_skip_same_fmt(self, tmp_path, monkeypatch):
        """Converting MP4 to MP4 should skip when video_info succeeds."""
        test_file = tmp_path / "test.mp4"
        test_file.write_bytes(b"fake mp4 content for testing")
        
        # Mock get_video_info to return success (simulating working ffprobe)
        from processor import get_video_info as original_get_info
        def mock_get_info(path):
            return {'success': True, 'format': 'mov,mp4', 'video_codec': 'h264', 'audio_codec': 'aac'}
        monkeypatch.setattr('processor.get_video_info', mock_get_info)

        result = convert_video([str(test_file)], "mp4")

        assert result['success'] is False
        assert 'skipped' in result
        assert len(result['skipped']) == 1
        assert 'Ya está en formato MP4' in result['skipped'][0]

    def test_video_convert_different_format(self, tmp_path):
        """Converting MP4 to AVI should proceed."""
        test_file = tmp_path / "test.mp4"
        test_file.write_bytes(b"fake mp4 content for testing")

        result = convert_video([str(test_file)], "avi")

        # Will fail due to no ffmpeg, but skip logic should NOT trigger
        assert 'skipped' not in result or len(result.get('skipped', [])) == 0