"""
Tests for processor.py - duplicate detection functions.
"""
import tempfile
import pytest
from pathlib import Path
from processor import find_duplicates_by_hash, find_duplicates_by_size


@pytest.fixture
def temp_folder():
    """Create a temporary folder with test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestFindDuplicatesByHash:
    """Tests for find_duplicates_by_hash function."""

    def test_no_duplicates(self, temp_folder):
        """Test that unique files are NOT marked as duplicates."""
        file1 = Path(temp_folder) / "file1.txt"
        file2 = Path(temp_folder) / "file2.txt"
        
        file1.write_text("unique content 1")
        file2.write_text("unique content 2")
        
        result = find_duplicates_by_hash(temp_folder, extensions=['.txt'])
        
        assert result['success'] is True
        assert result['count'] == 0
        assert result['total_duplicates'] == 0

    def test_single_duplicate(self, temp_folder):
        """Test that duplicates are correctly identified."""
        file1 = Path(temp_folder) / "file1.txt"
        file2 = Path(temp_folder) / "file2.txt"
        file3 = Path(temp_folder) / "file3.txt"
        
        content = "same content"
        file1.write_text(content)
        file2.write_text(content)
        file3.write_text("different content")
        
        result = find_duplicates_by_hash(temp_folder, extensions=['.txt'])
        
        assert result['success'] is True
        assert result['count'] == 1
        assert result['total_duplicates'] == 1

    def test_multiple_duplicates(self, temp_folder):
        """Test multiple groups of duplicates."""
        file1 = Path(temp_folder) / "dup1_a.txt"
        file2 = Path(temp_folder) / "dup1_b.txt"
        file3 = Path(temp_folder) / "dup2_a.txt"
        file4 = Path(temp_folder) / "dup2_b.txt"
        file5 = Path(temp_folder) / "unique.txt"
        
        file1.write_text("content A")
        file2.write_text("content A")
        file3.write_text("content B")
        file4.write_text("content B")
        file5.write_text("unique")
        
        result = find_duplicates_by_hash(temp_folder, extensions=['.txt'])
        
        assert result['success'] is True
        assert result['count'] == 2
        assert result['total_duplicates'] == 2

    def test_nonexistent_folder(self):
        """Test handling of non-existent folder."""
        result = find_duplicates_by_hash("/nonexistent/folder")
        
        assert result['success'] is False
        assert 'error' in result

    def test_extension_filter(self, temp_folder):
        """Test that extensions are correctly filtered."""
        file1 = Path(temp_folder) / "image.jpg"
        file2 = Path(temp_folder) / "image.png"
        file3 = Path(temp_folder) / "document.txt"
        
        content = "same content"
        file1.write_bytes(content.encode())
        file2.write_bytes(content.encode())
        file3.write_text("same content")
        
        result_jpg = find_duplicates_by_hash(temp_folder, extensions=['.jpg'])
        result_txt = find_duplicates_by_hash(temp_folder, extensions=['.txt'])
        
        assert result_jpg['count'] == 0
        assert result_txt['count'] == 1

    def test_empty_folder(self, temp_folder):
        """Test empty folder returns no duplicates."""
        result = find_duplicates_by_hash(temp_folder, extensions=['.txt'])
        
        assert result['success'] is True
        assert result['count'] == 0


class TestFindDuplicatesBySize:
    """Tests for find_duplicates_by_size function."""

    def test_no_duplicates_by_size(self, temp_folder):
        """Test that files with different sizes are NOT marked as duplicates."""
        file1 = Path(temp_folder) / "file1.txt"
        file2 = Path(temp_folder) / "file2.txt"
        
        file1.write_text("short")
        file2.write_text("much longer content here")
        
        result = find_duplicates_by_size(temp_folder)
        
        assert result['success'] is True
        assert result['count'] == 0
        assert result['total_files'] == 0

    def test_potential_duplicates_by_size(self, temp_folder):
        """Test that files with same size are identified as potential duplicates."""
        file1 = Path(temp_folder) / "file1.txt"
        file2 = Path(temp_folder) / "file2.txt"
        file3 = Path(temp_folder) / "file3.txt"
        
        file1.write_text("same size")
        file2.write_text("same size")
        file3.write_text("different")
        
        result = find_duplicates_by_size(temp_folder)
        
        assert result['success'] is True
        assert result['count'] >= 1

    def test_multiple_groups_by_size(self, temp_folder):
        """Test multiple groups of files with same size."""
        file1 = Path(temp_folder) / "dup1_a.txt"
        file2 = Path(temp_folder) / "dup1_b.txt"
        file3 = Path(temp_folder) / "dup2_a.txt"
        file4 = Path(temp_folder) / "dup2_b.txt"
        
        file1.write_text("aaaa")
        file2.write_text("aaaa")
        file3.write_text("bbbb")
        file4.write_text("bbbb")
        
        result = find_duplicates_by_size(temp_folder)
        
        assert result['success'] is True
        assert result['count'] == 2

    def test_nonexistent_folder_size(self):
        """Test handling of non-existent folder."""
        result = find_duplicates_by_size("/nonexistent/folder")
        
        assert result['success'] is False
        assert 'error' in result

    def test_ignores_empty_files(self, temp_folder):
        """Test that empty files are ignored."""
        file1 = Path(temp_folder) / "empty.txt"
        file2 = Path(temp_folder) / "content.txt"
        
        file1.write_text("")
        file2.write_text("content")
        
        result = find_duplicates_by_size(temp_folder)
        
        assert result['success'] is True

    def test_empty_folder_size(self, temp_folder):
        """Test empty folder returns no potential duplicates."""
        result = find_duplicates_by_size(temp_folder)
        
        assert result['success'] is True
        assert result['count'] == 0