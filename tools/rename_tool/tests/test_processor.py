"""
Tests for rename_tool.processor module.
"""
import os
import tempfile
import pytest
from unittest.mock import patch
from pathlib import Path, Path as PathHelper
import sys

sys.path.insert(0, str(PathHelper(__file__).parent.parent))
from processor import (
    rename_with_prefix,
    rename_with_suffix,
    rename_replace,
    rename_numbered,
    rename_case,
    rename_regex
)


class TestProcessDispatch:
    """Tests for action dispatch in RenameTool.process()."""
    
    def test_action_prefix_dispatch(self, temp_dir):
        """Test that 'prefix' action dispatches to rename_with_prefix."""
        from tools.rename_tool import RenameTool
        import tools.rename_tool.processor as proc
        
        tool = RenameTool()
        
        # Create test files
        test_file = os.path.join(temp_dir, 'file1.txt')
        Path(test_file).touch()
        
        with patch.object(proc, 'rename_with_prefix', return_value={'success': True, 'renamed': []}) as mock_prefix:
            result = tool.process([test_file], {'action': 'prefix', 'prefix': 'new_'})
            
            assert mock_prefix.called
            assert result['success'] is True
    
    def test_action_suffix_dispatch(self, temp_dir):
        """Test that 'suffix' action dispatches to rename_with_suffix."""
        from tools.rename_tool import RenameTool
        import tools.rename_tool.processor as proc
        
        tool = RenameTool()
        
        test_file = os.path.join(temp_dir, 'file1.txt')
        Path(test_file).touch()
        
        with patch.object(proc, 'rename_with_suffix', return_value={'success': True, 'renamed': []}) as mock_suffix:
            result = tool.process([test_file], {'action': 'suffix', 'suffix': '_old'})
            
            assert mock_suffix.called
            assert result['success'] is True
    
    def test_action_replace_dispatch(self, temp_dir):
        """Test that 'replace' action dispatches to rename_replace."""
        from tools.rename_tool import RenameTool
        import tools.rename_tool.processor as proc
        
        tool = RenameTool()
        
        test_file = os.path.join(temp_dir, 'file1.txt')
        Path(test_file).touch()
        
        with patch.object(proc, 'rename_replace', return_value={'success': True, 'renamed': []}) as mock_replace:
            result = tool.process([test_file], {'action': 'replace', 'find': 'old', 'replace': 'new'})
            
            assert mock_replace.called
            assert result['success'] is True
    
    def test_action_numbered_dispatch(self, temp_dir):
        """Test that 'numbered' action dispatches to rename_numbered."""
        from tools.rename_tool import RenameTool
        import tools.rename_tool.processor as proc
        
        tool = RenameTool()
        
        test_file = os.path.join(temp_dir, 'file1.txt')
        Path(test_file).touch()
        
        with patch.object(proc, 'rename_numbered', return_value={'success': True, 'renamed': []}) as mock_numbered:
            result = tool.process([test_file], {'action': 'numbered', 'start': 1})
            
            assert mock_numbered.called
            assert result['success'] is True
    
    def test_action_case_dispatch(self, temp_dir):
        """Test that 'case' action dispatches to rename_case."""
        from tools.rename_tool import RenameTool
        import tools.rename_tool.processor as proc
        
        tool = RenameTool()
        
        test_file = os.path.join(temp_dir, 'file1.txt')
        Path(test_file).touch()
        
        with patch.object(proc, 'rename_case', return_value={'success': True, 'renamed': []}) as mock_case:
            result = tool.process([test_file], {'action': 'case', 'case': 'lower'})
            
            assert mock_case.called
            assert result['success'] is True
    
    def test_action_regex_dispatch(self, temp_dir):
        """Test that 'regex' action dispatches to rename_regex."""
        from tools.rename_tool import RenameTool
        import tools.rename_tool.processor as proc
        
        tool = RenameTool()
        
        test_file = os.path.join(temp_dir, 'file1.txt')
        Path(test_file).touch()
        
        with patch.object(proc, 'rename_regex', return_value={'success': True, 'renamed': []}) as mock_regex:
            result = tool.process([test_file], {'action': 'regex', 'pattern': r'file(\d+)', 'replace': r'file_$1'})
            
            assert mock_regex.called
            assert result['success'] is True
    
    def test_unknown_action_error(self, temp_dir):
        """Test that unknown action returns proper error."""
        from tools.rename_tool import RenameTool
        
        tool = RenameTool()
        
        test_file = os.path.join(temp_dir, 'file1.txt')
        Path(test_file).touch()
        
        result = tool.process([test_file], {'action': 'invalid_action'})
        
        assert result['success'] is False
        assert result['error'] == 'Unknown action: invalid_action'
    
    def test_default_action_is_prefix(self, temp_dir):
        """Test that default action is 'prefix'."""
        from tools.rename_tool import RenameTool
        import tools.rename_tool.processor as proc
        
        tool = RenameTool()
        
        test_file = os.path.join(temp_dir, 'file1.txt')
        Path(test_file).touch()
        
        with patch.object(proc, 'rename_with_prefix', return_value={'success': True, 'renamed': []}) as mock_prefix:
            result = tool.process([test_file], {})  # No action specified
            
            assert mock_prefix.called
            assert result['success'] is True


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as td:
        yield td


class TestRenameWithPrefix:
    """Tests for rename_with_prefix function."""
    
    def test_prefix_basic(self, temp_dir):
        """Test adding prefix to files."""
        file1 = os.path.join(temp_dir, 'file1.txt')
        Path(file1).touch()
        
        result = rename_with_prefix([file1], prefix='new_')
        
        assert result['success'] is True
        assert len(result['renamed']) == 1
    
    def test_prefix_multiple_files(self, temp_dir):
        """Test adding prefix to multiple files."""
        files = []
        for i in range(3):
            f = os.path.join(temp_dir, f'file{i}.txt')
            Path(f).touch()
            files.append(f)
        
        result = rename_with_prefix(files, prefix='test_')
        
        assert result['success'] is True
        assert len(result['renamed']) == 3


class TestRenameWithSuffix:
    """Tests for rename_with_suffix function."""
    
    def test_suffix_basic(self, temp_dir):
        """Test adding suffix to files."""
        file1 = os.path.join(temp_dir, 'file1.txt')
        Path(file1).touch()
        
        result = rename_with_suffix([file1], suffix='_old')
        
        assert result['success'] is True
        assert len(result['renamed']) == 1


class TestRenameReplace:
    """Tests for rename_replace function."""
    
    def test_replace_basic(self, temp_dir):
        """Test replacing text in filenames."""
        file1 = os.path.join(temp_dir, 'old_name.txt')
        Path(file1).touch()
        
        result = rename_replace([file1], find='old', replace='new')
        
        assert result['success'] is True
        assert len(result['renamed']) == 1


class TestRenameCase:
    """Tests for rename_case function."""
    
    def test_case_lower(self, temp_dir):
        """Test converting to lowercase."""
        file1 = os.path.join(temp_dir, 'FILE.txt')
        Path(file1).touch()
        
        result = rename_case([file1], case='lower')
        
        assert result['success'] is True
    
    def test_case_upper(self, temp_dir):
        """Test converting to uppercase."""
        file1 = os.path.join(temp_dir, 'file.txt')
        Path(file1).touch()
        
        result = rename_case([file1], case='upper')
        
        assert result['success'] is True