"""
Tests for hash_tool/processor.py
"""
import pytest
import tempfile
import os
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools' / 'hash_tool'))
from processor import calculate_hash, calculate_all_hashes, verify_hash, calculate_file_hash_list


@pytest.fixture
def temp_file():
    """Create a temporary file with known content."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Hello, World!")
        temp_path = f.name
    
    yield temp_path
    
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_files():
    """Create multiple temporary files."""
    files = []
    for i in range(3):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'_{i}.txt') as f:
            f.write(f"Content {i}")
            files.append(f.name)
    
    yield files
    
    for fp in files:
        if os.path.exists(fp):
            os.unlink(fp)


class TestCalculateHash:
    """Tests for calculate_hash() function."""
    
    def test_calculate_hash_md5(self, temp_file):
        """Test MD5 hash calculation."""
        result = calculate_hash(temp_file, 'md5')
        
        assert result['success'] is True
        assert result['algorithm'] == 'md5'
        assert result['hash'] == '65a8e27d8879283831b664bd8b7f0ad4'
    
    def test_calculate_hash_sha1(self, temp_file):
        """Test SHA1 hash calculation."""
        result = calculate_hash(temp_file, 'sha1')
        
        assert result['success'] is True
        assert result['algorithm'] == 'sha1'
        assert result['hash'] == '0a0a9f2a6772942557ab5355d76af442f8f65e01'
    
    def test_calculate_hash_sha256(self, temp_file):
        """Test SHA256 hash calculation."""
        result = calculate_hash(temp_file, 'sha256')
        
        assert result['success'] is True
        assert result['algorithm'] == 'sha256'
        assert result['hash'] == 'dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f'
    
    def test_calculate_hash_sha512(self, temp_file):
        """Test SHA512 hash calculation."""
        result = calculate_hash(temp_file, 'sha512')
        
        assert result['success'] is True
        assert result['algorithm'] == 'sha512'
    
    def test_calculate_hash_default_algorithm(self, temp_file):
        """Test default algorithm is sha256."""
        result = calculate_hash(temp_file)
        
        assert result['success'] is True
        assert result['algorithm'] == 'sha256'
    
    def test_calculate_hash_file_not_found(self):
        """Test with non-existent file."""
        result = calculate_hash('/nonexistent/file.txt')
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_calculate_hash_unsupported_algorithm(self, temp_file):
        """Test with unsupported algorithm."""
        result = calculate_hash(temp_file, 'invalid_algo')
        
        assert result['success'] is False
        assert 'error' in result


class TestCalculateAllHashes:
    """Tests for calculate_all_hashes() function."""
    
    def test_calculate_all_hashes_success(self, temp_file):
        """Test calculating all hash types."""
        result = calculate_all_hashes(temp_file)
        
        assert result['success'] is True
        assert 'hashes' in result
        assert 'md5' in result['hashes']
        assert 'sha1' in result['hashes']
        assert 'sha256' in result['hashes']
        assert 'sha512' in result['hashes']
        assert result['file_name'] == os.path.basename(temp_file)
    
    def test_calculate_all_hashes_file_not_found(self):
        """Test with non-existent file."""
        result = calculate_all_hashes('/nonexistent/file.txt')
        
        assert result['success'] is False
        assert 'error' in result


class TestVerifyHash:
    """Tests for verify_hash() function."""
    
    def test_verify_hash_match(self, temp_file):
        """Test hash verification with correct hash."""
        expected_hash = 'dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f'
        result = verify_hash(temp_file, expected_hash, 'sha256')
        
        assert result['success'] is True
        assert result['match'] is True
        assert result['expected'] == expected_hash
        assert result['actual'] == expected_hash
    
    def test_verify_hash_no_match(self, temp_file):
        """Test hash verification with incorrect hash."""
        result = verify_hash(temp_file, 'wronghash123', 'sha256')
        
        assert result['success'] is True
        assert result['match'] is False
        assert result['expected'] == 'wronghash123'
    
    def test_verify_hash_case_insensitive(self, temp_file):
        """Test hash verification is case insensitive."""
        expected_hash = 'DFFD6021BB2BD5B0AF676290809EC3A53191DD81C7F70A4B28688A362182986F'
        result = verify_hash(temp_file, expected_hash, 'sha256')
        
        assert result['success'] is True
        assert result['match'] is True
    
    def test_verify_hash_md5(self, temp_file):
        """Test hash verification with MD5."""
        expected_hash = '65a8e27d8879283831b664bd8b7f0ad4'
        result = verify_hash(temp_file, expected_hash, 'md5')
        
        assert result['success'] is True
        assert result['match'] is True
        assert result['algorithm'] == 'md5'
    
    def test_verify_hash_file_not_found(self):
        """Test with non-existent file."""
        result = verify_hash('/nonexistent/file.txt', 'somehash', 'sha256')
        
        assert result['success'] is False


class TestCalculateFileHashList:
    """Tests for calculate_file_hash_list() function."""
    
    def test_calculate_file_hash_list_multiple_files(self, temp_files):
        """Test batch processing multiple files."""
        result = calculate_file_hash_list(temp_files, 'sha256')
        
        assert result['success'] is True
        assert result['count'] == 3
        assert len(result['files']) == 3
    
    def test_calculate_file_hash_list_single_file(self, temp_file):
        """Test batch processing with single file."""
        result = calculate_file_hash_list([temp_file], 'sha256')
        
        assert result['success'] is True
        assert result['count'] == 1
        assert len(result['files']) == 1
    
    def test_calculate_file_hash_list_with_nonexistent(self, temp_file):
        """Test batch processing with mix of existing and non-existing files."""
        result = calculate_file_hash_list([temp_file, '/nonexistent/file.txt'], 'sha256')
        
        assert result['success'] is True
        assert result['count'] == 1
    
    def test_calculate_file_hash_list_all_nonexistent(self):
        """Test batch processing with only non-existent files."""
        result = calculate_file_hash_list(['/nonexistent/1.txt', '/nonexistent/2.txt'], 'sha256')
        
        assert result['success'] is True
        assert result['count'] == 0
        assert len(result['files']) == 0
    
    def test_calculate_file_hash_list_empty_list(self):
        """Test with empty file list."""
        result = calculate_file_hash_list([], 'sha256')
        
        assert result['success'] is True
        assert result['count'] == 0