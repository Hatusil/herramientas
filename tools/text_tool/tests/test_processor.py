"""
Tests for text_tool.processor module.
"""
import pytest

from tools.text_tool.processor import analyze_stats, extract_text_from_file


class TestAnalyzeStats:
    """Tests for analyze_stats function."""

    def test_analyze_stats_basic(self):
        """analyze_stats returns dict with stats from text."""
        text = "hello world hello"

        result = analyze_stats(text)

        assert result['success'] is True
        assert result['total_words'] == 3

    def test_analyze_stats_empty(self):
        """analyze_stats handles empty text."""
        result = analyze_stats("")

        assert result['success'] is True
        assert result['total_words'] == 0


class TestExtractText:
    """Tests for text extraction."""

    def test_extract_text_from_file_txt(self, tmp_path):
        """extract_text_from_file reads txt files."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        result = extract_text_from_file(str(test_file))
        assert result['success'] is True
        assert "Test content" in result['text']

    def test_extract_text_from_file_nonexistent(self):
        """extract_text_from_file handles missing file."""
        result = extract_text_from_file("/nonexistent/file.txt")
        assert result['success'] is False