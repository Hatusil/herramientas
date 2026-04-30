"""
Pytest configuration and fixtures for herramientas tests.
"""
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for file operations."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def mock_files(temp_dir):
    """Create mock files in temp directory."""
    files = []
    
    # Create test files
    test_files = [
        'documento.txt',
        'reporte.pdf',
        'presentacion.pptx',
        'datos.xlsx',
        'notas.docx',
        'imagen.gif',
        'video.mp4',
        'audio.mp3',
    ]
    
    for filename in test_files:
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write(f"Content of {filename}")
        files.append(filepath)
    
    # Create subdirectory with files
    subdir = os.path.join(temp_dir, 'subdir')
    os.makedirs(subdir)
    with open(os.path.join(subdir, 'nested.txt'), 'w') as f:
        f.write("Nested file content")
    files.append(os.path.join(subdir, 'nested.txt'))
    
    return files


@pytest.fixture
def mock_tool_module():
    """Create a mock tool module with a BaseTool subclass."""
    mock_module = MagicMock()
    
    # Create a mock tool class
    class MockTool:
        def __init__(self):
            self.ui = None
        
        def get_name(self):
            return "MockTool"
        
        def get_icon(self):
            return "🔧"
        
        def get_description(self):
            return "A mock tool for testing"
        
        def build_ui(self, parent_frame):
            pass
        
        def process(self, files, options):
            return {'success': True}
    
    mock_module.MockTool = MockTool
    return mock_module


@pytest.fixture
def mock_tools_dir(temp_dir, monkeypatch):
    """Create a temporary tools directory structure for testing."""
    tools_path = Path(temp_dir) / 'tools'
    tools_path.mkdir()
    
    # Patch the TOOLS_DIR constant
    monkeypatch.setattr('core.constants.TOOLS_DIR', tools_path)
    
    return tools_path


@pytest.fixture
def sample_search_results():
    """Sample search results for export tests."""
    return [
        {
            'path': '/test/file1.txt',
            'name': 'file1.txt',
            'size': 1024,
            'modified': '29/04/2026 10:00',
            'matches': 2
        },
        {
            'path': '/test/file2.pdf',
            'name': 'file2.pdf',
            'size': 2048,
            'modified': '29/04/2026 11:00',
            'matches': 0
        },
        {
            'path': '/test/file3.docx',
            'name': 'file3.docx',
            'size': 512,
            'modified': '29/04/2026 12:00',
            'matches': 5
        },
    ]