"""
Tests para processor.py
"""
import os
import csv
import pytest
import tempfile
from datetime import datetime, timedelta
import types
from pathlib import Path


def load_processor_module():
    """Carga el processor dinámicamente sin conflictos de nombres."""
    tool_dir = Path(__file__).parent
    processor_path = tool_dir / "processor.py"
    namespace = {}
    with open(processor_path, 'r') as f:
        code = compile(f.read(), str(processor_path), 'exec')
        exec(code, namespace)
    return types.SimpleNamespace(**namespace)


processor = load_processor_module()
search_by_name = processor.search_by_name
search_by_date = processor.search_by_date
filter_by_size = processor.filter_by_size
filter_by_extension = processor.filter_by_extension
extract_docx_content = processor.extract_docx_content
extract_pdf_content = processor.extract_pdf_content
extract_xlsx_content = processor.extract_xlsx_content
get_file_content = processor.get_file_content
search_content = processor.search_content
search_all = processor.search_all
export_to_csv = processor.export_to_csv
export_to_txt = processor.export_to_txt


@pytest.fixture
def temp_dir():
    """Crea directorio temporal para pruebas."""
    with tempfile.TemporaryDirectory() as td:
        yield td


@pytest.fixture
def sample_files(temp_dir):
    """Crea archivos de prueba."""
    files = []
    
    txt1 = os.path.join(temp_dir, "test_file.txt")
    with open(txt1, 'w') as f:
        f.write("Hello World\nTest content")
    files.append(txt1)
    
    txt2 = os.path.join(temp_dir, "another_file.txt")
    with open(txt2, 'w') as f:
        f.write("Python programming")
    files.append(txt2)
    
    txt3 = os.path.join(temp_dir, "document.pdf.txt")
    with open(txt3, 'w') as f:
        f.write("PDF content")
    files.append(txt3)
    
    return files


class TestSearchByName:
    """Tests para search_by_name()."""
    
    def test_exact_match(self, sample_files):
        result = search_by_name(sample_files, "test_file.txt", mode="exact")
        assert len(result) == 1
        assert "test_file.txt" in result[0]
    
    def test_exact_case_insensitive(self, sample_files):
        result = search_by_name(sample_files, "TEST_FILE.TXT", mode="exact", case_sensitive=False)
        assert len(result) == 1
    
    def test_exact_case_sensitive(self, sample_files):
        result = search_by_name(sample_files, "TEST_FILE.TXT", mode="exact", case_sensitive=True)
        assert len(result) == 0
    
    def test_contains_match(self, sample_files):
        result = search_by_name(sample_files, "test", mode="contains")
        assert len(result) == 1
        assert "test_file.txt" in result[0]
    
    def test_contains_case_insensitive(self, sample_files):
        result = search_by_name(sample_files, "TEST", mode="contains", case_sensitive=False)
        assert len(result) == 1
    
    def test_regex_match(self, sample_files):
        result = search_by_name(sample_files, r"test_.*\.txt", mode="regex")
        assert len(result) == 1
    
    def test_regex_case_insensitive(self, sample_files):
        result = search_by_name(sample_files, r"TEST_FILE", mode="regex", case_sensitive=False)
        assert len(result) == 1
    
    def test_empty_pattern(self, sample_files):
        result = search_by_name(sample_files, "")
        assert len(result) == len(sample_files)
    
    def test_no_match(self, sample_files):
        result = search_by_name(sample_files, "nonexistent", mode="contains")
        assert len(result) == 0


class TestSearchByDate:
    """Tests para search_by_date()."""
    
    def test_date_from(self, temp_dir):
        files = []
        old_file = os.path.join(temp_dir, "old.txt")
        with open(old_file, 'w') as f:
            f.write("old")
        os.utime(old_file, (1000000000, 1000000000))
        
        new_file = os.path.join(temp_dir, "new.txt")
        with open(new_file, 'w') as f:
            f.write("new")
        
        files = [old_file, new_file]
        
        from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        result = search_by_date(files, date_from=from_date)
        
        assert len(result) == 1
        assert "new.txt" in result[0]
    
    def test_date_to(self, temp_dir):
        files = []
        old_file = os.path.join(temp_dir, "old.txt")
        with open(old_file, 'w') as f:
            f.write("old")
        os.utime(old_file, (1000000000, 1000000000))
        
        new_file = os.path.join(temp_dir, "new.txt")
        with open(new_file, 'w') as f:
            f.write("new")
        
        files = [old_file, new_file]
        
        to_date = (datetime.now() - timedelta(days=365)).strftime("%d/%m/%Y")
        result = search_by_date(files, date_to=to_date)
        
        assert len(result) == 1
        assert "old.txt" in result[0]
    
    def test_date_range(self, temp_dir):
        files = []
        file1 = os.path.join(temp_dir, "file1.txt")
        with open(file1, 'w') as fh:
            fh.write("content")
        # Set to old date (2001) - should be excluded by date_from
        os.utime(file1, (1000000000, 1000000000))
        
        file2 = os.path.join(temp_dir, "file2.txt")
        with open(file2, 'w') as fh:
            fh.write("content")
        # file2 keeps current mtime - should be included
        
        files = [file1, file2]
        
        # date_from is 365 days ago, date_to is in the future - includes file2
        from_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        to_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        result = search_by_date(files, date_from=from_date, date_to=to_date)
        
        # file1 (2001) is older than from_date, file2 (now) is within range
        assert len(result) == 1
        assert "file2.txt" in result[0]
    
    def test_dd_mm_yyyy_format(self, temp_dir):
        files = []
        fpath = os.path.join(temp_dir, "test.txt")
        with open(fpath, 'w') as fh:
            fh.write("test")
        files.append(fpath)
        
        result = search_by_date(files, date_from="01/01/2000")
        assert len(result) == 1


class TestFilterBySize:
    """Tests para filter_by_size()."""
    
    def test_min_size(self, temp_dir):
        small = os.path.join(temp_dir, "small.txt")
        with open(small, 'w') as f:
            f.write("a")
        
        large = os.path.join(temp_dir, "large.txt")
        with open(large, 'w') as f:
            f.write("a" * 1000)
        
        files = [small, large]
        result = filter_by_size(files, min_size=500)
        
        assert len(result) == 1
        assert "large.txt" in result[0]
    
    def test_max_size(self, temp_dir):
        small = os.path.join(temp_dir, "small.txt")
        with open(small, 'w') as f:
            f.write("a")
        
        large = os.path.join(temp_dir, "large.txt")
        with open(large, 'w') as f:
            f.write("a" * 1000)
        
        files = [small, large]
        result = filter_by_size(files, max_size=10)
        
        assert len(result) == 1
        assert "small.txt" in result[0]
    
    def test_min_and_max(self, temp_dir):
        small = os.path.join(temp_dir, "small.txt")
        with open(small, 'w') as f:
            f.write("a")
        
        medium = os.path.join(temp_dir, "medium.txt")
        with open(medium, 'w') as f:
            f.write("a" * 100)
        
        large = os.path.join(temp_dir, "large.txt")
        with open(large, 'w') as f:
            f.write("a" * 1000)
        
        files = [small, medium, large]
        result = filter_by_size(files, min_size=50, max_size=200)
        
        assert len(result) == 1
        assert "medium.txt" in result[0]


class TestFilterByExtension:
    """Tests para filter_by_extension()."""
    
    def test_single_extension(self, temp_dir):
        txt_file = os.path.join(temp_dir, "file.txt")
        with open(txt_file, 'w') as f:
            f.write("text")
        
        pdf_file = os.path.join(temp_dir, "file.pdf")
        with open(pdf_file, 'w') as f:
            f.write("pdf")
        
        files = [txt_file, pdf_file]
        result = filter_by_extension(files, ['txt'])
        
        assert len(result) == 1
        assert result[0].endswith('.txt')
    
    def test_multiple_extensions(self, temp_dir):
        txt_file = os.path.join(temp_dir, "file.txt")
        with open(txt_file, 'w') as f:
            f.write("text")
        
        pdf_file = os.path.join(temp_dir, "file.pdf")
        with open(pdf_file, 'w') as f:
            f.write("pdf")
        
        doc_file = os.path.join(temp_dir, "file.doc")
        with open(doc_file, 'w') as f:
            f.write("doc")
        
        files = [txt_file, pdf_file, doc_file]
        result = filter_by_extension(files, ['txt', 'pdf'])
        
        assert len(result) == 2
    
    def test_extension_with_dot(self, temp_dir):
        fpath = os.path.join(temp_dir, "file.txt")
        with open(fpath, 'w') as fh:
            fh.write("test")
        
        result = filter_by_extension([fpath], ['.txt'])
        assert len(result) == 1
    
    def test_case_insensitive(self, temp_dir):
        fpath = os.path.join(temp_dir, "file.TXT")
        with open(fpath, 'w') as fh:
            fh.write("test")
        
        result = filter_by_extension([fpath], ['txt'])
        assert len(result) == 1
    
    def test_empty_extensions(self, sample_files):
        result = filter_by_extension(sample_files, [])
        assert len(result) == len(sample_files)


class TestExtractContent:
    """Tests para funciones de extracción de contenido."""
    
    def test_extract_txt_content(self, temp_dir):
        fpath = os.path.join(temp_dir, "test.txt")
        with open(fpath, 'w') as fh:
            fh.write("Hello World\nTest content")
        
        content = get_file_content(fpath)
        assert "Hello World" in content
        assert "Test content" in content
    
    def test_extract_docx_not_available(self, temp_dir):
        f = os.path.join(temp_dir, "test.docx")
        with open(f, 'w') as f:
            f.write("dummy")
        
        content = extract_docx_content(f)
        assert content == ""
    
    def test_extract_pdf_not_available(self, temp_dir):
        f = os.path.join(temp_dir, "test.pdf")
        with open(f, 'w') as f:
            f.write("dummy")
        
        content = extract_pdf_content(f)
        assert content == ""
    
    def test_extract_xlsx_not_available(self, temp_dir):
        f = os.path.join(temp_dir, "test.xlsx")
        with open(f, 'w') as f:
            f.write("dummy")
        
        content = extract_xlsx_content(f)
        assert content == ""


class TestSearchContent:
    """Tests para search_content()."""
    
    def test_search_content_case_insensitive(self, temp_dir):
        fpath = os.path.join(temp_dir, "test.txt")
        with open(fpath, 'w') as fh:
            fh.write("Hello World\nTest content Hello again")
        
        result = search_content([fpath], "hello", case_sensitive=False)
        
        assert len(result) == 1
        assert result[fpath]['matches'] == 2
    
    def test_search_content_case_sensitive(self, temp_dir):
        fpath = os.path.join(temp_dir, "test.txt")
        with open(fpath, 'w') as fh:
            fh.write("hello world\ntest content hello again")
        
        result = search_content([fpath], "hello", case_sensitive=True)
        
        assert len(result) == 1
        assert result[fpath]['matches'] == 2
    
    def test_search_content_no_match(self, temp_dir):
        fpath = os.path.join(temp_dir, "test.txt")
        with open(fpath, 'w') as fh:
            fh.write("Hello World")
        
        result = search_content([fpath], "nonexistent")
        assert len(result) == 0


class TestSearchAll:
    """Tests para search_all()."""
    
    def test_search_all_basic(self, temp_dir):
        f = os.path.join(temp_dir, "test.txt")
        with open(f, 'w') as f:
            f.write("content")
        
        result = search_all(temp_dir, {})
        
        assert result['success'] is True
        assert result['count'] >= 1
    
    def test_search_all_by_name(self, temp_dir):
        f = os.path.join(temp_dir, "specific.txt")
        with open(f, 'w') as f:
            f.write("content")
        
        other = os.path.join(temp_dir, "other.txt")
        with open(other, 'w') as f:
            f.write("content")
        
        result = search_all(temp_dir, {
            'name_pattern': 'specific',
            'name_mode': 'contains'
        })
        
        assert result['success'] is True
        assert any('specific.txt' in r['path'] for r in result['results'])
    
    def test_search_all_by_extension(self, temp_dir):
        txt_file = os.path.join(temp_dir, "file.txt")
        with open(txt_file, 'w') as f:
            f.write("text")
        
        pdf_file = os.path.join(temp_dir, "file.pdf")
        with open(pdf_file, 'w') as f:
            f.write("pdf")
        
        result = search_all(temp_dir, {
            'extensions': ['txt']
        })
        
        assert result['success'] is True
        assert all(r['name'].endswith('.txt') for r in result['results'])
    
    def test_search_all_by_size(self, temp_dir):
        small = os.path.join(temp_dir, "small.txt")
        with open(small, 'w') as f:
            f.write("a")
        
        large = os.path.join(temp_dir, "large.txt")
        with open(large, 'w') as f:
            f.write("a" * 1000)
        
        result = search_all(temp_dir, {
            'min_size': 500
        })
        
        assert result['success'] is True
        assert all(r['size'] >= 500 for r in result['results'])
    
    def test_search_all_content_search(self, temp_dir):
        f = os.path.join(temp_dir, "test.txt")
        with open(f, 'w') as f:
            f.write("Hello World Test")
        
        result = search_all(temp_dir, {
            'search_content': True,
            'content_pattern': 'Hello'
        })
        
        assert result['success'] is True
        assert result['content_matches']
    
    def test_search_all_invalid_folder(self):
        result = search_all("/nonexistent/folder", {})
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_search_all_combined_options(self, temp_dir):
        txt_file = os.path.join(temp_dir, "searchable.txt")
        with open(txt_file, 'w') as f:
            f.write("target content")
        
        other = os.path.join(temp_dir, "other.txt")
        with open(other, 'w') as f:
            f.write("other")
        
        result = search_all(temp_dir, {
            'name_pattern': 'searchable',
            'name_mode': 'contains',
            'extensions': ['txt'],
            'search_content': True,
            'content_pattern': 'target'
        })
        
        assert result['success'] is True
        assert len(result['results']) == 1
        assert result['results'][0]['matches'] > 0


class TestExport:
    """Tests para funciones de exportación."""
    
    def test_export_to_csv(self, temp_dir):
        results = [
            {'path': '/path/file1.txt', 'name': 'file1.txt', 'size': 100, 'modified': '01/01/2024', 'matches': 0},
            {'path': '/path/file2.txt', 'name': 'file2.txt', 'size': 200, 'modified': '02/01/2024', 'matches': 1},
        ]
        
        output = os.path.join(temp_dir, "export.csv")
        success = export_to_csv(results, output)
        
        assert success is True
        assert os.path.exists(output)
        
        with open(output, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
    
    def test_export_to_txt(self, temp_dir):
        results = [
            {'path': '/path/file1.txt', 'name': 'file1.txt', 'size': 100, 'modified': '01/01/2024', 'matches': 0},
            {'path': '/path/file2.txt', 'name': 'file2.txt', 'size': 200, 'modified': '02/01/2024', 'matches': 1},
        ]
        
        output = os.path.join(temp_dir, "export.txt")
        success = export_to_txt(results, output)
        
        assert success is True
        assert os.path.exists(output)
        
        with open(output, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 2
            assert '/path/file1.txt' in lines[0]
    
    def test_export_csv_invalid_path(self):
        result = export_to_csv([], "/invalid/path/file.csv")
        assert result is False
    
    def test_export_txt_invalid_path(self):
        result = export_to_txt([], "/invalid/path/file.txt")
        assert result is False


class TestGetFileContent:
    """Tests para get_file_content()."""
    
    def test_get_file_content_txt(self, temp_dir):
        fpath = os.path.join(temp_dir, "test.txt")
        with open(fpath, 'w') as fh:
            fh.write("Test content")
        
        content = get_file_content(fpath)
        assert "Test content" in content
    
    def test_get_file_content_unknown_ext(self, temp_dir):
        fpath = os.path.join(temp_dir, "test.xyz")
        with open(fpath, 'w') as fh:
            fh.write("content")
        
        content = get_file_content(fpath)
        assert content == ""
    
    def test_get_file_content_nonexistent(self):
        content = get_file_content("/nonexistent/file.txt")
        assert content == ""


if __name__ == '__main__':
    pytest.main([__file__, '-v'])