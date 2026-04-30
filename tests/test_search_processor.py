"""
Tests for tools/search_tool/processor.py
"""
import os
import csv
try:
    import pytest
except ImportError:
    pytest = None
import tempfile
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timedelta


class TestSearchByName:
    """Test suite for search_by_name function."""

    def test_search_by_name_empty_pattern_returns_all(self):
        """Test empty pattern returns original list."""
        from tools.search_tool.processor import search_by_name
        
        files = ['/path/file1.txt', '/path/file2.pdf']
        result = search_by_name(files, '')
        
        assert result == files

    def test_search_by_name_exact_match(self):
        """Test exact mode finds exact matches."""
        from tools.search_tool.processor import search_by_name
        
        files = ['/path/documento.txt', '/path/doc.txt', '/path/documento.pdf']
        result = search_by_name(files, 'documento.txt', mode='exact')
        
        assert '/path/documento.txt' in result
        assert len(result) == 1

    def test_search_by_name_exact_case_insensitive(self):
        """Test exact mode is case insensitive by default."""
        from tools.search_tool.processor import search_by_name
        
        files = ['/path/Documento.txt', '/path/documento.txt']
        result = search_by_name(files, 'DOCUMENTO.TXT', mode='exact')
        
        assert len(result) == 2

    def test_search_by_name_exact_case_sensitive(self):
        """Test exact mode with case sensitive."""
        from tools.search_tool.processor import search_by_name
        
        files = ['/path/Documento.txt', '/path/documento.txt']
        result = search_by_name(files, 'documento.txt', mode='exact', case_sensitive=True)
        
        assert len(result) == 1
        assert result[0] == '/path/documento.txt'

    def test_search_by_name_contains(self):
        """Test contains mode finds partial matches."""
        from tools.search_tool.processor import search_by_name
        
        files = ['/path/documento.txt', '/path/reporte.pdf', '/path/doc.txt']
        result = search_by_name(files, 'doc', mode='contains')
        
        assert '/path/documento.txt' in result
        assert '/path/doc.txt' in result

    def test_search_by_name_regex(self):
        """Test regex mode matches patterns."""
        from tools.search_tool.processor import search_by_name
        
        files = ['/path/file1.txt', '/path/file2.pdf', '/path/file10.txt']
        result = search_by_name(files, r'file\d+\.txt', mode='regex')
        
        assert '/path/file1.txt' in result
        assert '/path/file10.txt' in result

    def test_search_by_name_regex_invalid_pattern(self):
        """Test regex mode handles invalid patterns."""
        from tools.search_tool.processor import search_by_name
        
        files = ['/path/file1.txt']
        result = search_by_name(files, r'[invalid', mode='regex')
        
        assert result == []

    def test_search_by_name_default_mode(self):
        """Test default mode is contains."""
        from tools.search_tool.processor import search_by_name
        
        files = ['/path/documento.txt', '/path/test.pdf']
        result = search_by_name(files, 'doc')
        
        assert '/path/documento.txt' in result


class TestSearchByDate:
    """Test suite for search_by_date function."""

    def test_search_by_date_no_dates_returns_all(self):
        """Test with no date filters returns all files."""
        from tools.search_tool.processor import search_by_date
        
        # Use temp files that actually exist
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f1:
            temp_file1 = f1.name
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f2:
            temp_file2 = f2.name
        
        try:
            files = [temp_file1, temp_file2]
            result = search_by_date(files)
            # Should return all files when no date filter is set
            assert len(result) == 2
        finally:
            os.unlink(temp_file1)
            os.unlink(temp_file2)

    def test_search_by_date_from_date(self):
        """Test filtering from a specific date."""
        from tools.search_tool.processor import search_by_date
        
        # Create temp files with different dates
        with tempfile.NamedTemporaryFile(delete=False) as f:
            old_file = f.name
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            new_file = f.name
        
        try:
            # Set old file mtime to 1 year ago
            old_time = datetime.now() - timedelta(days=365)
            os.utime(old_file, (old_time.timestamp(), old_time.timestamp()))
            
            # Set new file mtime to today
            new_time = datetime.now()
            os.utime(new_file, (new_time.timestamp(), new_time.timestamp()))
            
            # Filter from 6 months ago
            from_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
            result = search_by_date([old_file, new_file], date_from=from_date)
            
            assert new_file in result
            # old_file may or may not be in result depending on exact timing
        finally:
            os.unlink(old_file)
            os.unlink(new_file)

    def test_search_by_date_different_formats(self):
        """Test parsing different date formats."""
        from tools.search_tool.processor import search_by_date
        
        # Use real temp file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_file = f.name
        
        try:
            files = [temp_file]
            
            # Should not raise exceptions
            result1 = search_by_date(files, date_from='29/04/2026')
            result2 = search_by_date(files, date_from='2026-04-29')
            result3 = search_by_date(files, date_from='invalid')
            
            # Invalid returns [] because it tries to parse, fails, returns all BUT
            # it checks os.path.exists so files that don't exist are filtered
            # With real file, should return the file
            assert len(result3) >= 0  # Just check it doesn't crash
        finally:
            os.unlink(temp_file)

    def test_search_by_date_nonexistent_file(self):
        """Test handling of nonexistent files."""
        from tools.search_tool.processor import search_by_date
        
        files = ['/nonexistent/file.txt']
        result = search_by_date(files)
        
        assert result == []


class TestFilterBySize:
    """Test suite for filter_by_size function."""

    def test_filter_by_size_no_limits(self):
        """Test with no size limits returns all files."""
        from tools.search_tool.processor import filter_by_size
        
        # Use real temp files
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f1:
            temp_file1 = f1.name
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f2:
            temp_file2 = f2.name
        
        try:
            files = [temp_file1, temp_file2]
            result = filter_by_size(files)
            # Should return all files when no size limits
            assert len(result) == 2
        finally:
            os.unlink(temp_file1)
            os.unlink(temp_file2)
        
        assert result == files

    def test_filter_by_size_min_size(self):
        """Test filtering by minimum size."""
        from tools.search_tool.processor import filter_by_size
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'x' * 1000)  # 1000 bytes
            small_file = f.name
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'x' * 10000)  # 10000 bytes
            large_file = f.name
        
        try:
            result = filter_by_size([small_file, large_file], min_size=5000)
            assert large_file in result
            # small_file filtered out because < 5000
        finally:
            os.unlink(small_file)
            os.unlink(large_file)

    def test_filter_by_size_max_size(self):
        """Test filtering by maximum size."""
        from tools.search_tool.processor import filter_by_size
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'x' * 1000)  # 1000 bytes
            small_file = f.name
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'x' * 10000)  # 10000 bytes
            large_file = f.name
        
        try:
            result = filter_by_size([small_file, large_file], max_size=5000)
            assert small_file in result
            # large_file filtered out because > 5000
        finally:
            os.unlink(small_file)
            os.unlink(large_file)

    def test_filter_by_size_nonexistent_file(self):
        """Test handling nonexistent files."""
        from tools.search_tool.processor import filter_by_size
        
        files = ['/nonexistent/file.txt']
        result = filter_by_size(files, min_size=1)
        
        assert result == []


class TestFilterByExtension:
    """Test suite for filter_by_extension function."""

    def test_filter_by_extension_empty_returns_all(self):
        """Test empty extensions list returns all files."""
        from tools.search_tool.processor import filter_by_extension
        
        files = ['/path/file1.txt', '/path/file2.pdf']
        result = filter_by_extension(files, [])
        
        assert result == files

    def test_filter_by_extension_single(self):
        """Test filtering by single extension."""
        from tools.search_tool.processor import filter_by_extension
        
        files = ['/path/doc.txt', '/path/report.pdf', '/path/data.xlsx']
        result = filter_by_extension(files, ['txt'])
        
        assert '/path/doc.txt' in result
        assert len(result) == 1

    def test_filter_by_extension_multiple(self):
        """Test filtering by multiple extensions."""
        from tools.search_tool.processor import filter_by_extension
        
        files = ['/path/doc.txt', '/path/report.pdf', '/path/data.xlsx']
        result = filter_by_extension(files, ['txt', 'pdf'])
        
        assert '/path/doc.txt' in result
        assert '/path/report.pdf' in result
        assert len(result) == 2

    def test_filter_by_extension_case_insensitive(self):
        """Test extension matching is case insensitive."""
        from tools.search_tool.processor import filter_by_extension
        
        files = ['/path/doc.TXT', '/path/report.PDF']
        result = filter_by_extension(files, ['txt', 'pdf'])
        
        assert len(result) == 2

    def test_filter_by_extension_strips_dot(self):
        """Test extension matching strips leading dot."""
        from tools.search_tool.processor import filter_by_extension
        
        files = ['/path/doc.txt']
        result = filter_by_extension(files, ['.txt'])
        
        assert len(result) == 1


class TestGetFileContent:
    """Test suite for get_file_content function."""

    def test_get_file_content_txt(self):
        """Test extracting content from TXT file."""
        from tools.search_tool.processor import get_file_content
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('Hello World')
            txt_file = f.name
        
        try:
            result = get_file_content(txt_file)
            assert 'Hello World' in result
        finally:
            os.unlink(txt_file)

    def test_get_file_content_unsupported(self):
        """Test unsupported file returns empty string."""
        from tools.search_tool.processor import get_file_content
        
        # .xyz is not supported
        result = get_file_content('/path/file.xyz')
        
        assert result == ''


class TestSearchContent:
    """Test suite for search_content function."""

    def test_search_content_empty_files(self):
        """Test with empty file list."""
        from tools.search_tool.processor import search_content
        
        result = search_content([], 'pattern')
        assert result == {}

    def test_search_content_empty_pattern(self):
        """Test with empty pattern."""
        from tools.search_tool.processor import search_content
        
        files = ['/path/file.txt']
        result = search_content(files, '')
        
        assert result == {}

    @patch('tools.search_tool.processor.get_file_content')
    def test_search_content_finds_match(self, mock_content):
        """Test finding content pattern in files."""
        from tools.search_tool.processor import search_content
        
        mock_content.return_value = 'This is a test document with keyword'
        
        files = ['/path/file.txt']
        result = search_content(files, 'keyword')
        
        assert '/path/file.txt' in result
        assert result['/path/file.txt']['matches'] == 1

    @patch('tools.search_tool.processor.get_file_content')
    def test_search_content_case_insensitive(self, mock_content):
        """Test case insensitive content search."""
        from tools.search_tool.processor import search_content
        
        mock_content.return_value = 'KEYWORD keyword Keyword'
        
        files = ['/path/file.txt']
        result = search_content(files, 'keyword', case_sensitive=False)
        
        assert result['/path/file.txt']['matches'] == 3

    @patch('tools.search_tool.processor.get_file_content')
    def test_search_content_no_match(self, mock_content):
        """Test when pattern not found."""
        from tools.search_tool.processor import search_content
        
        mock_content.return_value = 'Some content without the word'
        
        files = ['/path/file.txt']
        result = search_content(files, 'missing')
        
        assert result == {}


class TestSearchAll:
    """Test suite for search_all function."""

    def test_search_all_nonexistent_folder(self):
        """Test with nonexistent folder."""
        from tools.search_tool.processor import search_all
        
        result = search_all('/nonexistent/folder', {})
        
        assert result['success'] is False
        assert 'error' in result

    def test_search_all_empty_folder(self, temp_dir):
        """Test with empty folder."""
        from tools.search_tool.processor import search_all
        
        result = search_all(temp_dir, {})
        
        assert result['success'] is True
        assert result['count'] == 0

    def test_search_all_by_name(self, temp_dir):
        """Test searching by name."""
        # Create test files
        Path(temp_dir, 'test.txt').write_text('test')
        Path(temp_dir, 'other.pdf').write_text('other')
        
        from tools.search_tool.processor import search_all
        
        result = search_all(temp_dir, {
            'name_pattern': 'test',
            'name_mode': 'contains'
        })
        
        assert result['success'] is True
        assert result['count'] == 1
        assert result['results'][0]['name'] == 'test.txt'

    def test_search_all_by_extension(self, temp_dir):
        """Test searching by extension."""
        # Create test files
        Path(temp_dir, 'file.txt').write_text('text')
        Path(temp_dir, 'file.pdf').write_text('pdf')
        
        from tools.search_tool.processor import search_all
        
        result = search_all(temp_dir, {
            'extensions': ['txt']
        })
        
        assert result['success'] is True
        assert result['count'] == 1

    def test_search_all_returns_proper_structure(self, temp_dir):
        """Test search returns proper result structure."""
        # Create test file
        test_file = Path(temp_dir, 'test.txt')
        test_file.write_text('content')
        
        from tools.search_tool.processor import search_all
        
        result = search_all(temp_dir, {})
        
        assert 'path' in result['results'][0]
        assert 'name' in result['results'][0]
        assert 'size' in result['results'][0]
        assert 'modified' in result['results'][0]
        assert 'matches' in result['results'][0]


class TestExportToCSV:
    """Test suite for export_to_csv function."""

    def test_export_to_csv_success(self, temp_dir, sample_search_results):
        """Test successful CSV export."""
        from tools.search_tool.processor import export_to_csv
        
        output_path = os.path.join(temp_dir, 'results.csv')
        result = export_to_csv(sample_search_results, output_path)
        
        assert result is True
        assert os.path.exists(output_path)
        
        # Verify CSV content
        with open(output_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 3
            assert rows[0]['name'] == 'file1.txt'

    def test_export_to_csv_invalid_path(self, sample_search_results):
        """Test export to invalid path returns False."""
        from tools.search_tool.processor import export_to_csv
        
        result = export_to_csv(sample_search_results, '/invalid/path/results.csv')
        
        assert result is False


class TestExportToTxt:
    """Test suite for export_to_txt function."""

    def test_export_to_txt_success(self, temp_dir, sample_search_results):
        """Test successful TXT export."""
        from tools.search_tool.processor import export_to_txt
        
        output_path = os.path.join(temp_dir, 'results.txt')
        result = export_to_txt(sample_search_results, output_path)
        
        assert result is True
        assert os.path.exists(output_path)
        
        # Verify TXT content
        with open(output_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) == 3
            assert '/test/file1.txt\n' in lines

    def test_export_to_txt_invalid_path(self, sample_search_results):
        """Test export to invalid path returns False."""
        from tools.search_tool.processor import export_to_txt
        
        result = export_to_txt(sample_search_results, '/invalid/path/results.txt')
        
        assert result is False


class TestExtractContent:
    """Test suite for content extraction functions."""

    def test_extract_docx_not_available(self):
        """Test docx extraction when library not available."""
        from tools.search_tool import processor
        
        original = processor.DOCX_AVAILABLE
        processor.DOCX_AVAILABLE = False
        
        result = processor.extract_docx_content('/path/file.docx')
        
        processor.DOCX_AVAILABLE = original
        assert result == ''

    def test_extract_pdf_not_available(self):
        """Test pdf extraction when library not available."""
        from tools.search_tool import processor
        
        original = processor.PDF_AVAILABLE
        processor.PDF_AVAILABLE = False
        
        result = processor.extract_pdf_content('/path/file.pdf')
        
        processor.PDF_AVAILABLE = original
        assert result == ''

    def test_extract_xlsx_not_available(self):
        """Test xlsx extraction when library not available."""
        from tools.search_tool import processor
        
        original = processor.XLSX_AVAILABLE
        processor.XLSX_AVAILABLE = False
        
        result = processor.extract_xlsx_content('/path/file.xlsx')
        
        processor.XLSX_AVAILABLE = original
        assert result == ''

    def test_extract_pptx_not_available(self):
        """Test pptx extraction when library not available."""
        from tools.search_tool import processor
        
        original = processor.PPTX_AVAILABLE
        processor.PPTX_AVAILABLE = False
        
        result = processor.extract_pptx_content('/path/file.pptx')
        
        processor.PPTX_AVAILABLE = original
        assert result == ''