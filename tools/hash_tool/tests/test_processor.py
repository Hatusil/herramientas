"""
Tests for hash_tool.processor module.
"""
import tempfile
import pytest
import unittest.mock
from pathlib import Path
import sys
from pathlib import Path as PathHelper

sys.path.insert(0, str(PathHelper(__file__).parent.parent))
from processor import calculate_hash, calculate_all_hashes, verify_hash, calculate_file_hash_list


class TestProcessDispatch:
    """Tests for action dispatch in HashTool.process()."""
    
    def test_action_calculate_dispatch(self):
        """Test that 'calculate' action dispatches to calculate_hash."""
        from tools.hash_tool import HashTool
        import tools.hash_tool.processor as proc
        
        tool = HashTool()
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'test content')
            tmp_path = tmp.name
        
        try:
            with unittest.mock.patch.object(proc, 'calculate_hash', return_value={'success': True, 'hash': 'abc123'}) as mock_calc:
                result = tool.process([tmp_path], {'action': 'calculate'})
                
                assert mock_calc.called
                assert result['success'] is True
        finally:
            Path(tmp_path).unlink()
    
    def test_action_all_dispatch(self):
        """Test that 'all' action dispatches to calculate_all_hashes."""
        from tools.hash_tool import HashTool
        import tools.hash_tool.processor as proc
        
        tool = HashTool()
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'test content')
            tmp_path = tmp.name
        
        try:
            with unittest.mock.patch.object(proc, 'calculate_all_hashes', return_value={'success': True, 'hashes': {}}) as mock_all:
                result = tool.process([tmp_path], {'action': 'all'})
                
                assert mock_all.called
                assert result['success'] is True
        finally:
            Path(tmp_path).unlink()
    
    def test_action_verify_dispatch(self):
        """Test that 'verify' action dispatches to verify_hash."""
        from tools.hash_tool import HashTool
        import tools.hash_tool.processor as proc
        
        tool = HashTool()
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'test content')
            tmp_path = tmp.name
        
        try:
            with unittest.mock.patch.object(proc, 'verify_hash', return_value={'success': True, 'matches': True}) as mock_verify:
                result = tool.process([tmp_path], {'action': 'verify', 'expected_hash': 'abc123'})
                
                assert mock_verify.called
                assert result['success'] is True
        finally:
            Path(tmp_path).unlink()
    
    def test_action_list_dispatch(self):
        """Test that 'list' action dispatches to calculate_file_hash_list."""
        from tools.hash_tool import HashTool
        import tools.hash_tool.processor as proc
        
        tool = HashTool()
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'test content')
            tmp_path = tmp.name
        
        try:
            with unittest.mock.patch.object(proc, 'calculate_file_hash_list', return_value={'success': True, 'files': []}) as mock_list:
                result = tool.process([tmp_path], {'action': 'list'})
                
                assert mock_list.called
                assert result['success'] is True
        finally:
            Path(tmp_path).unlink()
    
    def test_action_calculate_requires_file(self):
        """Test that 'calculate' without files returns error."""
        from tools.hash_tool import HashTool
        
        tool = HashTool()
        result = tool.process([], {'action': 'calculate'})
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_unknown_action_error(self):
        """Test that unknown action returns proper error."""
        from tools.hash_tool import HashTool
        
        tool = HashTool()
        result = tool.process(['/fake/file.txt'], {'action': 'invalid_action'})
        
        assert result['success'] is False
        assert result['error'] == 'Unknown action: invalid_action'
    
    def test_default_action_is_calculate(self):
        """Test that default action is 'calculate'."""
        from tools.hash_tool import HashTool
        import tools.hash_tool.processor as proc
        
        tool = HashTool()
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'test content')
            tmp_path = tmp.name
        
        try:
            with unittest.mock.patch.object(proc, 'calculate_hash', return_value={'success': True, 'hash': 'abc123'}) as mock_calc:
                result = tool.process([tmp_path], {})  # No action specified
                
                assert mock_calc.called
                assert result['success'] is True
        finally:
            Path(tmp_path).unlink()


# Basic processor function tests (keeping existing tests structure)
class TestCalculateHash:
    """Tests for calculate_hash function."""
    
    def test_calculate_hash_basic(self):
        """Test basic hash calculation."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'hello world')
            tmp_path = tmp.name
        
        try:
            result = calculate_hash(tmp_path, algorithm='sha256')
            assert result['success'] is True
            assert 'hash' in result
            assert result['algorithm'] == 'sha256'
        finally:
            Path(tmp_path).unlink()
    
    def test_calculate_hash_md5(self):
        """Test MD5 hash calculation."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'test content')
            tmp_path = tmp.name
        
        try:
            result = calculate_hash(tmp_path, algorithm='md5')
            assert result['success'] is True
            assert result['algorithm'] == 'md5'
        finally:
            Path(tmp_path).unlink()
    
    def test_calculate_hash_nonexistent_file(self):
        """Test hash of nonexistent file."""
        result = calculate_hash('/nonexistent/file.txt')
        
        assert result['success'] is False
        assert 'error' in result


class TestVerifyHash:
    """Tests for verify_hash function."""
    
    def test_verify_hash_match(self):
        """Test hash verification with matching hash."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'hello world')
            tmp_path = tmp.name
        
        try:
            # First calculate the hash
            calc_result = calculate_hash(tmp_path, algorithm='sha256')
            expected = calc_result['hash']
            
            # Now verify
            result = verify_hash(tmp_path, expected, algorithm='sha256')
            assert result['success'] is True
            assert result['matches'] is True
        finally:
            Path(tmp_path).unlink()
    
    def test_verify_hash_mismatch(self):
        """Test hash verification with non-matching hash."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'hello world')
            tmp_path = tmp.name
        
        try:
            result = verify_hash(tmp_path, 'wronghash123', algorithm='sha256')
            assert result['success'] is True
            assert result['matches'] is False
        finally:
            Path(tmp_path).unlink()