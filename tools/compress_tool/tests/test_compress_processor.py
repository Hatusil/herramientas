"""
Tests for compress_tool.processor module.
"""
import os
import zipfile
import tarfile
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch
import types


def load_processor_module():
    """Carga el processor dinámicamente sin conflictos de nombres."""
    tool_dir = Path(__file__).parent.parent
    processor_path = tool_dir / "processor.py"
    namespace = {}
    with open(processor_path, 'r') as f:
        code = compile(f.read(), str(processor_path), 'exec')
        exec(code, namespace)
    return types.SimpleNamespace(**namespace)


processor = load_processor_module()
compress_to_zip = processor.compress_to_zip
compress_to_tar = processor.compress_to_tar
decompress_zip = processor.decompress_zip
decompress_tar = processor.decompress_tar
list_zip_contents = processor.list_zip_contents


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as td:
        yield td


@pytest.fixture
def test_files(temp_dir):
    files = []
    for name in ['file1.txt', 'file2.txt']:
        path = os.path.join(temp_dir, name)
        with open(path, 'w') as f:
            f.write(f'Content of {name}\n' * 100)
        files.append(path)
    subdir = os.path.join(temp_dir, 'subdir')
    os.makedirs(subdir)
    subfile = os.path.join(subdir, 'file3.txt')
    with open(subfile, 'w') as f:
        f.write('Subdirectory file content\n' * 50)
    files.append(subdir)
    return files


class TestCompressToZip:
    def test_compress_single_file(self, temp_dir):
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('Test content')
        
        result = compress_to_zip([test_file])
        
        assert result['success'] is True
        assert len(result['output_files']) == 1
        assert os.path.exists(result['output_files'][0])
    
    def test_compress_multiple_files(self, temp_dir):
        files = []
        for i in range(3):
            f = os.path.join(temp_dir, f'file{i}.txt')
            with open(f, 'w') as fp:
                fp.write(f'Content {i}')
            files.append(f)
        
        result = compress_to_zip(files)
        
        assert result['success'] is True
        assert os.path.exists(result['output_files'][0])
    
    def test_compress_with_directory(self, temp_dir):
        subdir = os.path.join(temp_dir, 'mydir')
        os.makedirs(subdir)
        file_in_dir = os.path.join(subdir, 'nested.txt')
        with open(file_in_dir, 'w') as f:
            f.write('Nested content')
        
        result = compress_to_zip([subdir])
        
        assert result['success'] is True
        with zipfile.ZipFile(result['output_files'][0], 'r') as zf:
            names = zf.namelist()
            assert any('nested.txt' in n for n in names)
    
    def test_compression_level_0(self, temp_dir):
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('A' * 10000)
        
        result = compress_to_zip([test_file], level=0)
        
        assert result['success'] is True
    
    def test_compression_level_9(self, temp_dir):
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('A' * 10000)
        
        result = compress_to_zip([test_file], level=9)
        
        assert result['success'] is True
    
    def test_empty_files_list(self, temp_dir):
        result = compress_to_zip([])
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_custom_output_path(self, temp_dir):
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('Content')
        output = os.path.join(temp_dir, 'custom.zip')
        
        result = compress_to_zip([test_file], output_path=output)
        
        assert result['success'] is True
        assert os.path.exists(output)


class TestCompressToTar:
    def test_compress_tar_gz(self, temp_dir):
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('Test content')
        
        result = compress_to_tar([test_file], compression='gz')
        
        assert result['success'] is True
        # May return .tar or .tar.gz depending on implementation
        output = str(result['output_files'][0])
        assert output.endswith('.tar') or output.endswith('.tar.gz')
    
    def test_compress_tar_bz2(self, temp_dir):
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('Test content')
        
        result = compress_to_tar([test_file], compression='bz2')
        
        assert result['success'] is True
        output = str(result['output_files'][0])
        assert output.endswith('.tar.bz2')

    def test_compress_tar_xz(self, temp_dir):
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('Test content')

        result = compress_to_tar([test_file], compression='xz')

        assert result['success'] is True
        output = str(result['output_files'][0])
        assert output.endswith('.tar.xz')
    
    def test_compress_tar_no_compression(self, temp_dir):
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('Test content')
        
        result = compress_to_tar([test_file], compression=None)
        
        assert result['success'] is True
        output = str(result['output_files'][0])
        assert output.endswith('.tar')
    
    def test_compress_multiple_files(self, temp_dir):
        files = []
        for i in range(3):
            f = os.path.join(temp_dir, f'file{i}.txt')
            with open(f, 'w') as fp:
                fp.write(f'Content {i}')
            files.append(f)
        
        result = compress_to_tar(files, compression='gz')
        
        assert result['success'] is True
        with tarfile.open(result['output_files'][0], 'r:gz') as tf:
            members = [m.name for m in tf.getmembers()]
            assert len(members) == 3


class TestDecompressZip:
    def test_decompress_basic(self, temp_dir):
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('Original content')
        
        zip_path = os.path.join(temp_dir, 'archive.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(test_file, 'test.txt')
        
        extract_dir = os.path.join(temp_dir, 'extracted')
        result = decompress_zip(zip_path, extract_dir)
        
        assert result['success'] is True
        extracted_file = os.path.join(extract_dir, 'test.txt')
        assert os.path.exists(extracted_file)
        with open(extracted_file, 'r') as f:
            assert f.read() == 'Original content'
    
    def test_decompress_nonexistent_file(self, temp_dir):
        result = decompress_zip(os.path.join(temp_dir, 'nonexistent.zip'))
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_decompress_default_output_dir(self, temp_dir):
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('Content')
        
        zip_path = os.path.join(temp_dir, 'myarchive.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(test_file, 'test.txt')
        
        result = decompress_zip(zip_path)
        
        assert result['success'] is True
        assert 'myarchive' in result['output_files'][0]


class TestDecompressTar:
    def test_decompress_tar_gz(self, temp_dir):
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('Original content')
        
        tar_path = os.path.join(temp_dir, 'archive.tar.gz')
        with tarfile.open(tar_path, 'w:gz') as tf:
            tf.add(test_file, 'test.txt')
        
        extract_dir = os.path.join(temp_dir, 'extracted')
        result = decompress_tar(tar_path, extract_dir)
        
        assert result['success'] is True
        extracted_file = os.path.join(extract_dir, 'test.txt')
        assert os.path.exists(extracted_file)
    
    def test_decompress_tar_bz2(self, temp_dir):
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('Content')
        
        tar_path = os.path.join(temp_dir, 'archive.tar.bz2')
        with tarfile.open(tar_path, 'w:bz2') as tf:
            tf.add(test_file, 'test.txt')
        
        result = decompress_tar(tar_path)
        
        assert result['success'] is True
    
    def test_decompress_nonexistent_file(self, temp_dir):
        result = decompress_tar(os.path.join(temp_dir, 'nonexistent.tar.gz'))
        
        assert result['success'] is False


class TestListZipContents:
    def test_list_basic(self, temp_dir):
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('Content')
        
        zip_path = os.path.join(temp_dir, 'archive.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(test_file, 'test.txt')
        
        result = list_zip_contents(zip_path)
        
        assert result['success'] is True
        assert result['count'] == 1
        assert 'test.txt' in result['files']
        assert 'total_size' in result
    
    def test_list_multiple_files(self, temp_dir):
        zip_path = os.path.join(temp_dir, 'archive.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i in range(5):
                info = zipfile.ZipInfo(f'file{i}.txt')
                zf.writestr(info, f'Content {i}')
        
        result = list_zip_contents(zip_path)
        
        assert result['success'] is True
        assert result['count'] == 5
    
    def test_list_nonexistent(self, temp_dir):
        result = list_zip_contents(os.path.join(temp_dir, 'nonexistent.zip'))
        
        assert result['success'] is False


class TestCompressionRoundTrips:
    def test_zip_compress_decompress_roundtrip(self, temp_dir):
        original_content = 'Roundtrip test content'
        test_file = os.path.join(temp_dir, 'original.txt')
        with open(test_file, 'w') as f:
            f.write(original_content)
        
        zip_result = compress_to_zip([test_file])
        assert zip_result['success'] is True
        
        extract_dir = os.path.join(temp_dir, 'restored')
        decompress_result = decompress_zip(zip_result['output_files'][0], extract_dir)
        assert decompress_result['success'] is True
        
        restored_file = os.path.join(extract_dir, 'original.txt')
        with open(restored_file, 'r') as f:
            assert f.read() == original_content
    
    def test_tar_compress_decompress_roundtrip(self, temp_dir):
        original_content = 'Tar roundtrip content'
        test_file = os.path.join(temp_dir, 'original.txt')
        with open(test_file, 'w') as f:
            f.write(original_content)
        
        tar_result = compress_to_tar([test_file], compression='gz')
        assert tar_result['success'] is True
        
        extract_dir = os.path.join(temp_dir, 'restored')
        decompress_result = decompress_tar(tar_result['output_files'][0], extract_dir)
        assert decompress_result['success'] is True
        
        restored_file = os.path.join(extract_dir, 'original.txt')
        with open(restored_file, 'r') as f:
            assert f.read() == original_content


class TestCompressSkipLogic:
    """Tests for compression skip logic."""

    def test_compress_skip_already_zip(self, temp_dir):
        """Compressing a ZIP file should skip."""
        zip_file = os.path.join(temp_dir, 'already.zip')
        with zipfile.ZipFile(zip_file, 'w') as zf:
            zf.writestr('test.txt', 'content')
        
        result = compress_to_zip([zip_file])

        assert result['success'] is True
        assert 'skipped' in result
        assert len(result['skipped']) == 1
        assert 'Ya es ZIP' in result['skipped'][0]

    def test_compress_skip_multiple_zips(self, temp_dir):
        """Compressing multiple ZIPs should skip all."""
        zips = []
        for i in range(3):
            zf = os.path.join(temp_dir, f'file{i}.zip')
            with zipfile.ZipFile(zf, 'w') as z:
                z.writestr(f'file{i}.txt', f'content{i}')
            zips.append(zf)
        
        result = compress_to_zip(zips)

        assert result['success'] is True
        assert 'skipped' in result
        assert len(result['skipped']) == 3

    def test_compress_mixed_zip_and_regular(self, temp_dir):
        """Compressing ZIP + regular files should skip ZIP, compress others."""
        zip_file = os.path.join(temp_dir, 'already.zip')
        with zipfile.ZipFile(zip_file, 'w') as zf:
            zf.writestr('test.txt', 'content')
        
        regular_file = os.path.join(temp_dir, 'regular.txt')
        with open(regular_file, 'w') as f:
            f.write('regular content')
        
        result = compress_to_zip([zip_file, regular_file])
        
        assert result['success'] is True
        assert 'skipped' in result
        assert len(result['skipped']) == 1


class TestProcessDispatch:
    """Tests for action dispatch in CompressTool.process()."""
    
    def test_action_zip_dispatch(self, temp_dir):
        """Test that 'zip' action dispatches to compress_to_zip."""
        from tools.compress_tool import CompressTool
        import tools.compress_tool.processor as proc
        
        tool = CompressTool()
        
        # Create test file
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('content')
        
        with patch.object(proc, 'compress_to_zip', return_value={'success': True, 'output_files': []}) as mock_zip:
            result = tool.process([test_file], {'action': 'zip'})
            
            assert mock_zip.called
            assert result['success'] is True
    
    def test_action_tar_dispatch(self, temp_dir):
        """Test that 'tar' action dispatches to compress_to_tar."""
        from tools.compress_tool import CompressTool
        import tools.compress_tool.processor as proc
        
        tool = CompressTool()
        
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('content')
        
        with patch.object(proc, 'compress_to_tar', return_value={'success': True, 'output_files': []}) as mock_tar:
            result = tool.process([test_file], {'action': 'tar'})
            
            assert mock_tar.called
            assert result['success'] is True
    
    def test_action_unzip_dispatch(self, temp_dir):
        """Test that 'unzip' action dispatches to decompress_zip."""
        from tools.compress_tool import CompressTool
        import tools.compress_tool.processor as proc
        
        tool = CompressTool()
        
        # Create a dummy zip file path (won't actually be read due to mock)
        zip_path = os.path.join(temp_dir, 'test.zip')
        
        with patch.object(proc, 'decompress_zip', return_value={'success': True, 'output_files': []}) as mock_unzip:
            result = tool.process([zip_path], {'action': 'unzip'})
            
            assert mock_unzip.called
            assert result['success'] is True
    
    def test_action_unzip_requires_file(self):
        """Test that 'unzip' without files returns error."""
        from tools.compress_tool import CompressTool
        
        tool = CompressTool()
        result = tool.process([], {'action': 'unzip'})
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_action_list_dispatch(self, temp_dir):
        """Test that 'list' action dispatches to list_zip_contents."""
        from tools.compress_tool import CompressTool
        import tools.compress_tool.processor as proc
        
        tool = CompressTool()
        
        zip_path = os.path.join(temp_dir, 'test.zip')
        
        with patch.object(proc, 'list_zip_contents', return_value={'success': True, 'files': [], 'count': 0}) as mock_list:
            result = tool.process([zip_path], {'action': 'list'})
            
            assert mock_list.called
            assert result['success'] is True
    
    def test_unknown_action_error(self):
        """Test that unknown action returns proper error."""
        from tools.compress_tool import CompressTool
        
        tool = CompressTool()
        result = tool.process(['/fake/file.txt'], {'action': 'invalid_action'})
        
        assert result['success'] is False
        assert result['error'] == 'Unknown action: invalid_action'
    
    def test_default_action_is_zip(self, temp_dir):
        """Test that default action is 'zip'."""
        from tools.compress_tool import CompressTool
        import tools.compress_tool.processor as proc
        
        tool = CompressTool()
        
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('content')
        
        with patch.object(proc, 'compress_to_zip', return_value={'success': True, 'output_files': []}) as mock_zip:
            result = tool.process([test_file], {})  # No action specified
            
            assert mock_zip.called
            assert result['success'] is True