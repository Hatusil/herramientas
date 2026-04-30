"""
Tests for rename_tool/processor.py
"""
import os
import tempfile
import shutil

import pytest

from tools.rename_tool.processor import (
    rename_with_prefix,
    rename_with_suffix,
    rename_replace,
    rename_numbered,
    rename_case,
    rename_regex,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for file operations."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def sample_files(temp_dir):
    """Create sample files for testing."""
    files = [
        'documento.txt',
        'reporte.pdf',
        'presentacion.pptx',
        'image.png',
        'video.mp4',
    ]
    result = []
    for name in files:
        path = os.path.join(temp_dir, name)
        with open(path, 'w') as f:
            f.write(f"content of {name}")
        result.append(path)
    return result


@pytest.fixture
def no_extension_file(temp_dir):
    """Create a file without extension."""
    path = os.path.join(temp_dir, 'README')
    with open(path, 'w') as f:
        f.write("readme content")
    return path


@pytest.fixture
def multiple_dots_file(temp_dir):
    """Create a file with multiple dots in name."""
    path = os.path.join(temp_dir, 'archive.tar.gz')
    with open(path, 'w') as f:
        f.write("archive content")
    return path


@pytest.fixture
def hidden_file(temp_dir):
    """Create a hidden file (starts with dot)."""
    path = os.path.join(temp_dir, '.hidden')
    with open(path, 'w') as f:
        f.write("hidden content")
    return path


@pytest.fixture
def uppercase_file(temp_dir):
    """Create a file with uppercase extension."""
    path = os.path.join(temp_dir, 'image.PNG')
    with open(path, 'w') as f:
        f.write("uppercase ext")
    return path


class TestRenameWithPrefix:
    """Tests for rename_with_prefix function."""

    def test_add_prefix_simple(self, sample_files):
        """Test adding a simple prefix."""
        result = rename_with_prefix(sample_files, prefix="new_")
        assert result['success'] is True
        assert len(result['renamed']) == 5
        renamed_names = [os.path.basename(r[1]) for r in result['renamed']]
        assert 'new_documento.txt' in renamed_names
        assert 'new_reporte.pdf' in renamed_names

    def test_add_prefix_multiple(self, sample_files):
        """Test adding a prefix with multiple characters."""
        result = rename_with_prefix(sample_files, prefix="backup_")
        assert result['success'] is True
        renamed_names = [os.path.basename(r[1]) for r in result['renamed']]
        assert 'backup_documento.txt' in renamed_names
        assert 'backup_video.mp4' in renamed_names

    def test_add_prefix_empty_list(self, temp_dir):
        """Test with empty file list."""
        result = rename_with_prefix([], prefix="pre_")
        assert result['success'] is False

    def test_add_prefix_to_no_extension(self, no_extension_file):
        """Test prefix on file without extension."""
        result = rename_with_prefix([no_extension_file], prefix="pre_")
        assert result['success'] is True
        new_name = os.path.basename(result['renamed'][0][1])
        assert new_name == "pre_README"

    def test_add_prefix_to_multiple_dots(self, multiple_dots_file):
        """Test prefix on file with multiple dots."""
        result = rename_with_prefix([multiple_dots_file], prefix="pre_")
        assert result['success'] is True
        new_name = os.path.basename(result['renamed'][0][1])
        assert new_name == "pre_archive.tar.gz"


class TestRenameWithSuffix:
    """Tests for rename_with_suffix function."""

    def test_add_suffix_simple(self, sample_files):
        """Test adding a simple suffix."""
        result = rename_with_suffix(sample_files, suffix="_v1")
        assert result['success'] is True
        renamed_names = [os.path.basename(r[1]) for r in result['renamed']]
        assert 'documento_v1.txt' in renamed_names
        assert 'reporte_v1.pdf' in renamed_names

    def test_add_suffix_before_extension(self, sample_files):
        """Test suffix is added before the extension."""
        result = rename_with_suffix(sample_files, suffix="_backup")
        renamed_names = [os.path.basename(r[1]) for r in result['renamed']]
        assert 'documento_backup.txt' in renamed_names

    def test_add_suffix_no_extension(self, no_extension_file):
        """Test suffix on file without extension."""
        result = rename_with_suffix([no_extension_file], suffix="_old")
        assert result['success'] is True
        new_name = os.path.basename(result['renamed'][0][1])
        assert new_name == "README_old"

    def test_add_suffix_multiple_dots(self, multiple_dots_file):
        """Test suffix on file with multiple dots."""
        result = rename_with_suffix([multiple_dots_file], suffix="_2")
        assert result['success'] is True
        new_name = os.path.basename(result['renamed'][0][1])
        assert new_name == 'archive.tar_2.gz'


class TestRenameReplace:
    """Tests for rename_replace function."""

    def test_replace_simple_text(self, sample_files):
        """Test simple text replacement."""
        result = rename_replace(sample_files, find="documento", replace="doc")
        assert result['success'] is True
        renamed_names = [os.path.basename(r[1]) for r in result['renamed']]
        assert 'doc.txt' in renamed_names

    def test_replace_extension(self, sample_files):
        """Test replacing text in extension."""
        result = rename_replace(sample_files, find="txt", replace="text")
        renamed_names = [os.path.basename(r[1]) for r in result['renamed']]
        assert 'documento.text' in renamed_names

    def test_replace_not_found(self, sample_files):
        """Test replacement when text not found."""
        result = rename_replace(sample_files, find="xyz", replace="abc")
        # Success is False when nothing is renamed
        assert result['success'] is False
        assert len(result['renamed']) == 0

    def test_replace_multiple_occurrences(self, temp_dir):
        """Test replacing multiple occurrences in same name."""
        files = [os.path.join(temp_dir, "test_test.txt")]
        with open(files[0], 'w') as f:
            f.write("content")
        result = rename_replace(files, find="test", replace="prod")
        assert result['success'] is True
        new_name = os.path.basename(result['renamed'][0][1])
        assert new_name == "prod_prod.txt"


class TestRenameNumbered:
    """Tests for rename_numbered function."""

    def test_numbered_default_start(self, sample_files):
        """Test numbering with default start (1)."""
        result = rename_numbered(sample_files)
        assert result['success'] is True
        renamed_names = [os.path.basename(r[1]) for r in result['renamed']]
        assert 'documento_1.txt' in renamed_names
        assert 'reporte_2.pdf' in renamed_names

    def test_numbered_custom_start(self, sample_files):
        """Test numbering with custom start value."""
        result = rename_numbered(sample_files, start=10)
        renamed_names = [os.path.basename(r[1]) for r in result['renamed']]
        assert 'documento_10.txt' in renamed_names
        assert 'reporte_11.pdf' in renamed_names

    def test_numbered_custom_pattern(self, sample_files):
        """Test numbering with custom pattern."""
        result = rename_numbered(sample_files, pattern="{n}_{name}")
        renamed_names = [os.path.basename(r[1]) for r in result['renamed']]
        assert '1_documento.txt' in renamed_names
        assert '2_reporte.pdf' in renamed_names

    def test_numbered_no_extension(self, no_extension_file):
        """Test numbering on file without extension."""
        result = rename_numbered([no_extension_file], pattern="file_{n}")
        assert result['success'] is True
        new_name = os.path.basename(result['renamed'][0][1])
        assert new_name == 'file_1'

    def test_numbered_different_pattern(self, sample_files):
        """Test numbering with different pattern placeholder."""
        result = rename_numbered(sample_files, pattern="img_{n:03d}")
        renamed_names = [os.path.basename(r[1]) for r in result['renamed']]
        assert 'img_001.txt' in renamed_names


class TestRenameCase:
    """Tests for rename_case function."""

    def test_case_lower(self, sample_files):
        """Test converting to lowercase."""
        result = rename_case(sample_files, case="lower")
        assert result['success'] is True
        renamed_names = [os.path.basename(r[1]) for r in result['renamed']]
        assert 'documento.txt' in renamed_names

    def test_case_upper(self, sample_files):
        """Test converting to uppercase."""
        result = rename_case(sample_files, case="upper")
        renamed_names = [os.path.basename(r[1]) for r in result['renamed']]
        assert 'DOCUMENTO.TXT' in renamed_names
        assert 'REPORTE.PDF' in renamed_names

    def test_case_title(self, sample_files):
        """Test converting to title case."""
        result = rename_case(sample_files, case="title")
        renamed_names = [os.path.basename(r[1]) for r in result['renamed']]
        assert 'Documento.Txt' in renamed_names

    def test_case_upper_preserve_extension(self, uppercase_file):
        """Test uppercase preserves extension case."""
        result = rename_case([uppercase_file], case="upper")
        new_name = os.path.basename(result['renamed'][0][1])
        assert new_name == 'IMAGE.PNG'

    def test_case_invalid_case(self, sample_files):
        """Test with invalid case type."""
        result = rename_case(sample_files, case="invalid")
        # Success is False when nothing is renamed (invalid case type)
        assert result['success'] is False
        assert len(result['renamed']) == 0


class TestRenameRegex:
    """Tests for rename_regex function."""

    def test_regex_simple_replace(self, sample_files):
        """Test simple regex replacement."""
        result = rename_regex(sample_files, pattern=r"doc\w+", replace="document")
        assert result['success'] is True
        renamed_names = [os.path.basename(r[1]) for r in result['renamed']]
        assert 'document.txt' in renamed_names

    def test_regex_capture_groups(self, temp_dir):
        """Test regex with capture groups."""
        files = [os.path.join(temp_dir, "file_2024_01.txt")]
        with open(files[0], 'w') as f:
            f.write("content")
        result = rename_regex(files, pattern=r"(\d{4})_(\d{2})", replace=r"y\1m\2")
        assert result['success'] is True
        new_name = os.path.basename(result['renamed'][0][1])
        assert new_name == 'file_y2024m01.txt'

    def test_regex_invalid_pattern(self, sample_files):
        """Test with invalid regex pattern."""
        result = rename_regex(sample_files, pattern=r"[invalid", replace="test")
        assert result['success'] is False
        assert 'error' in result

    def test_regex_no_match(self, sample_files):
        """Test regex that doesn't match anything."""
        result = rename_regex(sample_files, pattern=r"xyz\d+", replace="replaced")
        assert result['success'] is True
        for r in result['renamed']:
            original = os.path.basename(r[0])
            renamed = os.path.basename(r[1])
            assert original == renamed

    def test_regex_remove_text(self, temp_dir):
        """Test regex to remove text."""
        files = [os.path.join(temp_dir, "prefix_oldname.txt")]
        with open(files[0], 'w') as f:
            f.write("content")
        result = rename_regex(files, pattern=r"prefix_", replace="")
        assert result['success'] is True
        new_name = os.path.basename(result['renamed'][0][1])
        assert new_name == 'oldname.txt'


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_file_list(self, temp_dir):
        """Test all functions with empty file list."""
        assert rename_with_prefix([], "pre_")['success'] is False
        assert rename_with_suffix([], "_suf")['success'] is False
        assert rename_replace([], "a", "b")['success'] is False
        assert rename_numbered([])['success'] is False
        assert rename_case([], "lower")['success'] is False
        assert rename_regex([], "a", "b")['success'] is False

    def test_file_without_extension(self, no_extension_file):
        """Test functions on file without extension."""
        result = rename_with_prefix([no_extension_file], "pre_")
        new_name = os.path.basename(result['renamed'][0][1])
        assert new_name == "pre_README"

    def test_multiple_dots_filename(self, multiple_dots_file):
        """Test functions on file with multiple dots."""
        result = rename_with_suffix([multiple_dots_file], "_v1")
        new_name = os.path.basename(result['renamed'][0][1])
        assert new_name == "archive.tar_v1.gz"

    def test_hidden_file(self, hidden_file):
        """Test functions on hidden file (starts with dot)."""
        result = rename_with_prefix([hidden_file], "new_")
        assert result['success'] is True

    def test_error_handling(self, temp_dir):
        """Test error handling with non-existent file."""
        non_existent = os.path.join(temp_dir, "does_not_exist.txt")
        result = rename_with_prefix([non_existent], "pre_")
        assert len(result['errors']) > 0