"""
Tests for audio_tool.processor module - convert audio skip logic.
"""
import pytest
import os
import types
from pathlib import Path


def load_processor_module():
    """Carga el processor dinámicamente sin conflictos de nombres."""
    tool_dir = Path(__file__).parent.parent
    processor_path = tool_dir / "processor.py"
    namespace = {}
    with open(processor_path, 'r') as f:
        code = compile(f.read(), str(processor_path), 'exec')
        exec(code, namespace)
    return types.SimpleNamespace(**namespace)


processor = load_processor_module()
convert_audio = processor.convert_audio


class TestConvertAudioSkipLogic:
    """Tests for audio conversion skip logic."""

    @pytest.mark.skip(reason="FFmpeg not installed in test environment")
    def test_convert_skip_same_format(self, tmp_path):
        """Converting MP3 to MP3 should skip the file."""
        test_file = tmp_path / "test.mp3"
        test_file.write_bytes(b"fake mp3 content for testing")

        result = convert_audio([str(test_file)], "mp3", quality=192)

        assert result['success'] is True
        assert 'skipped' in result
        assert len(result['skipped']) == 1
        assert 'Ya está en formato MP3' in result['skipped'][0]

    @pytest.mark.skip(reason="FFmpeg not installed")
    def test_convert_skip_different_quality(self, tmp_path):
        """MP3 128k to 320k conversion should proceed (different bitrate)."""
        test_file = tmp_path / "test_128k.mp3"
        test_file.write_bytes(b"fake mp3 content for testing")

        result = convert_audio([str(test_file)], "mp3", quality=320)

        assert result['success'] is True
        assert len(result['output_files']) == 1

    @pytest.mark.skip(reason="FFmpeg not installed in test environment")
    def test_convert_skip_same_format_wav(self, tmp_path):
        """Converting WAV to WAV should skip."""
        test_file = tmp_path / "test.wav"
        test_file.write_bytes(b"fake wav content for testing")

        result = convert_audio([str(test_file)], "wav")

        assert result['success'] is True
        assert 'skipped' in result

    @pytest.mark.skip(reason="FFmpeg not installed")
    def test_convert_different_format(self, tmp_path):
        """Converting MP3 to WAV should proceed."""
        test_file = tmp_path / "test.mp3"
        test_file.write_bytes(b"fake mp3 content for testing")

        result = convert_audio([str(test_file)], "wav")

        assert result['success'] is True
        assert len(result['output_files']) == 1