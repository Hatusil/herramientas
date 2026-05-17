"""
Tests for text_tool.processor module.
"""
import pytest

from tools.text_tool.processor import analyze_stats, extract_text_from_file


class TestAnalyzeStats:
    """Tests for analyze_stats function."""

    def test_analyze_stats_basic(self, tmp_path):
        """analyze_stats returns dict with stats."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world hello")
        
        result = analyze_stats([str(test_file)])
        
        assert result['success'] is True
        assert 'stats' in result

    def test_analyze_stats_empty(self):
        """analyze_stats handles empty file list."""
        result = analyze_stats([])
        
        assert result['success'] is False


class TestExtractText:
    """Tests for text extraction."""

    def test_extract_text_from_file_txt(self, tmp_path):
        """extract_text_from_file reads txt files."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")
        
        result = extract_text_from_file(str(test_file))
        assert "Test content" in result

    def test_extract_text_from_file_nonexistent(self):
        """extract_text_from_file handles missing file."""
        result = extract_text_from_file("/nonexistent/file.txt")
        assert result == ""