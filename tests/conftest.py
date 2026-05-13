"""Shared fixtures for all tests."""
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def temp_dir():
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def mock_files(temp_dir):
    files = []
    test_files = [
        'documento.txt', 'reporte.pdf', 'presentacion.pptx',
        'datos.xlsx', 'notas.docx', 'imagen.gif', 'video.mp4', 'audio.mp3',
    ]
    for filename in test_files:
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write(f"Content of {filename}")
        files.append(filepath)
    subdir = os.path.join(temp_dir, 'subdir')
    os.makedirs(subdir)
    with open(os.path.join(subdir, 'nested.txt'), 'w') as f:
        f.write("Nested file content")
    files.append(os.path.join(subdir, 'nested.txt'))
    return files


@pytest.fixture
def mock_tool_module():
    mock_module = MagicMock()
    class MockTool:
        def __init__(self): self.ui = None
        def get_name(self): return "MockTool"
        def get_icon(self): return "icon"
        def get_description(self): return "A mock tool for testing"
        def build_ui(self, parent_frame): pass
        def process(self, files, options): return {'success': True}
    mock_module.MockTool = MockTool
    return mock_module


@pytest.fixture
def mock_tools_dir(temp_dir, monkeypatch):
    tools_path = Path(temp_dir) / 'tools'
    tools_path.mkdir()
    monkeypatch.setattr('core.constants.TOOLS_DIR', tools_path)
    return tools_path


@pytest.fixture
def project_root():
    return Path(__file__).parent.parent


@pytest.fixture
def tool_names(project_root):
    tools_dir = project_root / "tools"
    names = []
    for d in sorted(tools_dir.iterdir()):
        if d.is_dir() and not d.name.startswith('_'):
            if (d / "__init__.py").exists() and (d / "processor.py").exists():
                names.append(d.name)
    return sorted(names)


@pytest.fixture
def all_py_files(project_root):
    return (
        list(project_root.glob("tools/**/*.py")) +
        list(project_root.glob("core/**/*.py"))
    )


@pytest.fixture
def mock_violation_file(tmp_path):
    lines = [
        '"""Mock violation file for maxima audit tests."""',
        '',
        '# Module-level mutable state (A7 violation)',
        '_cache = {}', '_results = []', '_seen = set()',
        '',
        '# Hardcoded Windows path (E19 violation)',
        'WINDOWS_PATH = "C:\\\\Users\\\\test\\\\documents"',
        '',
        '# Heavy operation without async wrapper (A9 violation)',
        'import subprocess',
        '', '', 'def long_function():',
    ]
    for i in range(55):
        lines.append(f'    x_{i} = {i}')
    lines.append('    result = subprocess.run(["ls"], capture_output=True)')
    lines.append('    return result')
    lines.append('')
    for i in range(225):
        lines.append(f'# Padding line {i + 1}')
    file_path = tmp_path / "violation.py"
    file_path.write_text('\n'.join(lines))
    return file_path


@pytest.fixture
def maxima_config(project_root):
    return {
        'max_line_length': 300, 'max_function_length': 50,
        'max_class_length': 300, 'max_imports': 10,
        'max_identifier_length': 30,
        'project_root': project_root,
        'tools_dir': project_root / 'tools',
        'core_dir': project_root / 'core',
        'known_exceptions': {
            'a7_mutable_state': ['tools/search_tool/processor.py'],
            'e19_hardcoded_paths': ['core/constants.py'],
            'r0_long_functions': [
                'tools/audio_tool/processor.py',
                'tools/search_tool/processor.py',
            ],
            'r0_long_modules': [
                'tools/audio_tool/processor.py',
                'tools/search_tool/processor.py',
                'tools/text_tool/ui.py',
            ],
        },
    }


@pytest.fixture
def sample_search_results():
    return [
        {'path': '/test/file1.txt', 'name': 'file1.txt', 'size': 1024,
         'modified': '29/04/2026 10:00', 'matches': 2},
        {'path': '/test/file2.pdf', 'name': 'file2.pdf', 'size': 2048,
         'modified': '29/04/2026 11:00', 'matches': 0},
        {'path': '/test/file3.docx', 'name': 'file3.docx', 'size': 512,
         'modified': '29/04/2026 12:00', 'matches': 5},
    ]