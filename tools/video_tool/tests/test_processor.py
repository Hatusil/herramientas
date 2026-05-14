"""
Tests for video_tool.processor module - video conversion skip logic.
"""
import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from tools.video_tool.processor import convert_video


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


class TestProcessDispatch:
    """Tests for action dispatch in VideoTool.process()."""
    
    def test_action_audio_dispatch(self, tmp_path):
        """Test that 'audio' action dispatches to extract_audio."""
        from tools.video_tool import VideoTool
        import tools.video_tool.processor as proc
        
        tool = VideoTool()
        
        test_file = tmp_path / "test.mp4"
        test_file.write_bytes(b"fake video")
        
        with patch.object(proc, 'extract_audio', return_value={'success': True, 'output_files': []}) as mock_audio:
            result = tool.process([str(test_file)], {'action': 'audio'})
            
            assert mock_audio.called
            assert result['success'] is True
    
    def test_action_audio_requires_file(self):
        """Test that 'audio' without files returns error."""
        from tools.video_tool import VideoTool
        
        tool = VideoTool()
        result = tool.process([], {'action': 'audio'})
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_action_convert_dispatch(self, tmp_path):
        """Test that 'convert' action dispatches to convert_video."""
        from tools.video_tool import VideoTool
        import tools.video_tool.processor as proc
        
        tool = VideoTool()
        
        test_file = tmp_path / "test.mp4"
        test_file.write_bytes(b"fake video")
        
        with patch.object(proc, 'convert_video', return_value={'success': True, 'output_files': []}) as mock_convert:
            result = tool.process([str(test_file)], {'action': 'convert', 'output_format': 'avi'})
            
            assert mock_convert.called
            assert result['success'] is True
    
    def test_action_info_dispatch(self, tmp_path):
        """Test that 'info' action dispatches to get_video_info."""
        from tools.video_tool import VideoTool
        import tools.video_tool.processor as proc
        
        tool = VideoTool()
        
        test_file = tmp_path / "test.mp4"
        test_file.write_bytes(b"fake video")
        
        with patch.object(proc, 'get_video_info', return_value={'success': True}) as mock_info:
            result = tool.process([str(test_file)], {'action': 'info'})
            
            assert mock_info.called
            assert result['success'] is True
    
    def test_action_info_requires_file(self):
        """Test that 'info' without files returns error."""
        from tools.video_tool import VideoTool
        
        tool = VideoTool()
        result = tool.process([], {'action': 'info'})
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_unknown_action_error(self, tmp_path):
        """Test that unknown action returns proper error."""
        from tools.video_tool import VideoTool
        
        tool = VideoTool()
        
        test_file = tmp_path / "test.mp4"
        test_file.write_bytes(b"fake video")
        
        result = tool.process([str(test_file)], {'action': 'invalid_action'})
        
        assert result['success'] is False
        assert result['error'] == 'Unknown action: invalid_action'
    
    def test_default_action_is_convert(self, tmp_path):
        """Test that default action is 'convert'."""
        from tools.video_tool import VideoTool
        import tools.video_tool.processor as proc
        
        tool = VideoTool()
        
        test_file = tmp_path / "test.mp4"
        test_file.write_bytes(b"fake video")
        
        with patch.object(proc, 'convert_video', return_value={'success': True, 'output_files': []}) as mock_convert:
            result = tool.process([str(test_file)], {})  # No action specified
            
            assert mock_convert.called
            assert result['success'] is True