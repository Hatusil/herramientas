"""
Tests for search_tool.processor module.
"""
import pytest

from tools.search_tool.processor import search_by_name, filter_by_extension, get_file_content


class TestSearchByName:
    """Tests for search_by_name function."""

    def test_search_by_name_empty_files(self):
        """search_by_name returns empty list for empty input."""
        result = search_by_name([], "test")
        assert result == []

    def test_search_by_name_no_pattern(self):
        """search_by_name returns all files when no pattern."""
        files = ["/path/file1.txt", "/path/file2.txt"]
        result = search_by_name(files, None)
        assert result == files


class TestFilterByExtension:
    """Tests for filter_by_extension function."""

    def test_filter_by_extension_empty(self):
        """filter_by_extension returns empty for empty input."""
        result = filter_by_extension([], ["txt"])
        assert result == []

    def test_filter_by_extension_single(self):
        """filter_by_extension filters by extension."""
        files = ["/path/file.txt", "/path/file.pdf"]
        result = filter_by_extension(files, ["txt"])
        assert len(result) == 1
        assert result[0].endswith(".txt")


class TestGetFileContent:
    """Tests for get_file_content function."""

    def test_get_file_content_txt(self, tmp_path):
        """get_file_content reads text files."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello World")
        
        result = get_file_content(str(test_file))
        assert "Hello World" in result

    def test_get_file_content_unsupported(self, tmp_path):
        """get_file_content returns empty for unsupported format."""
        test_file = tmp_path / "test.xyz"
        result = get_file_content(str(test_file))
        assert result == ""