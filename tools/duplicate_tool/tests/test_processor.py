"""
Tests for processor.py - duplicate detection functions.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import tempfile
import pytest
from unittest.mock import patch
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


class TestProcessDispatch:
    """Tests for action dispatch in DuplicateTool.process()."""
    
    def test_action_hash_dispatch(self):
        """Test that 'hash' action dispatches to find_duplicates_async."""
        from tools.duplicate_tool import DuplicateTool
        import tools.duplicate_tool.processor as proc
        
        tool = DuplicateTool()
        
        with patch.object(proc, 'find_duplicates_async', return_value={'success': True, 'count': 0}) as mock_hash:
            result = tool.process(['/fake/folder'], {'action': 'hash', 'folder_path': '/fake/folder'})
            
            assert mock_hash.called
            assert result['success'] is True
    
    def test_action_async_dispatch(self):
        """Test that 'async' action dispatches to find_duplicates_async."""
        from tools.duplicate_tool import DuplicateTool
        import tools.duplicate_tool.processor as proc
        
        tool = DuplicateTool()
        
        with patch.object(proc, 'find_duplicates_async', return_value={'success': True, 'count': 0}) as mock_async:
            result = tool.process(['/fake/folder'], {'action': 'async', 'folder_path': '/fake/folder'})
            
            assert mock_async.called
            assert result['success'] is True
    
    def test_action_size_dispatch(self):
        """Test that 'size' action dispatches to find_duplicates_by_size."""
        from tools.duplicate_tool import DuplicateTool
        import tools.duplicate_tool.processor as proc
        
        tool = DuplicateTool()
        
        with patch.object(proc, 'find_duplicates_by_size', return_value={'success': True, 'count': 0}) as mock_size:
            result = tool.process(['/fake/folder'], {'action': 'size', 'folder_path': '/fake/folder'})
            
            assert mock_size.called
            assert result['success'] is True
    
    def test_folder_path_fallback(self):
        """Test that folder_path falls back to files[0] if it's a directory."""
        from tools.duplicate_tool import DuplicateTool
        import tools.duplicate_tool.processor as proc
        import tempfile
        import os
        
        tool = DuplicateTool()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(proc, 'find_duplicates_async', return_value={'success': True, 'count': 0}) as mock_hash:
                result = tool.process([tmpdir], {})  # No folder_path, uses files[0]
                
                assert mock_hash.called
                # Verify it was called with the directory path
                args, kwargs = mock_hash.call_args
                assert args[0] == tmpdir
    
    def test_folder_path_required(self):
        """Test that missing folder_path returns error."""
        from tools.duplicate_tool import DuplicateTool
        
        tool = DuplicateTool()
        result = tool.process(['/fake/file.txt'], {})  # Not a directory
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_unknown_action_error(self):
        """Test that unknown action returns proper error."""
        from tools.duplicate_tool import DuplicateTool
        
        tool = DuplicateTool()
        result = tool.process(['/fake/folder'], {'action': 'invalid_action', 'folder_path': '/fake/folder'})
        
        assert result['success'] is False
        assert result['error'] == 'Unknown action: invalid_action'
    
    def test_default_action_is_hash(self):
        """Test that default action is 'hash'."""
        from tools.duplicate_tool import DuplicateTool
        import tools.duplicate_tool.processor as proc
        
        tool = DuplicateTool()
        
        with patch.object(proc, 'find_duplicates_async', return_value={'success': True, 'count': 0}) as mock_hash:
            result = tool.process(['/fake/folder'], {'folder_path': '/fake/folder'})
            
            assert mock_hash.called
            assert result['success'] is True