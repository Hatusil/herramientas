"""Tests for maximas A8 (Idempotencia), A9 (Async), A12 (Observabilidad)."""
import ast
from pathlib import Path
import pytest


class TestA8_Idempotency:
    """A8: Processor functions must produce identical output when called twice."""

    def test_a8_hash_tool_deterministic(self, tmp_path):
        from tools.hash_tool.processor import calculate_hash
        test_file = tmp_path / "sample.txt"
        test_file.write_text("Hello, world! 42")
        result1 = calculate_hash(str(test_file), algorithm='sha256')
        result2 = calculate_hash(str(test_file), algorithm='sha256')
        assert result1['success'] is True
        assert result2['success'] is True
        assert result1['hash'] == result2['hash']

    def test_a8_rename_tool_deterministic(self, tmp_path):
        from tools.rename_tool.processor import rename_with_prefix
        test_file = tmp_path / "document.txt"
        test_file.write_text("content")
        files = [str(test_file)]
        result1 = rename_with_prefix(files, prefix="v2_")
        result2 = rename_with_prefix(files, prefix="v2_")
        assert result1['success'] is True
        assert result2['success'] is True
        for key in ('success', 'renamed', 'errors'):
            assert result1[key] == result2[key]


class TestA9_Async:
    """A9: Heavy operations must have async wrappers."""

    ASYNC_KEYWORDS = {'ThreadPoolExecutor', 'asyncio', 'run_in_background', 'async def'}

    def test_a9_heavy_ops_have_async_wrapper(self, all_py_files):
        project_root = Path(__file__).parent.parent
        flagged = []
        for py_file in all_py_files:
            if 'processor.py' not in str(py_file):
                continue
            try:
                source = py_file.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(source)
            except SyntaxError:
                continue
            has_sync_blocking = False
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if (isinstance(node.func.value, ast.Name) and node.func.value.id == 'subprocess'
                            and node.func.attr == 'run'):
                        has_sync_blocking = True
                        break
                    if (isinstance(node.func.value, ast.Name)
                            and node.func.value.id in ('time', 'asyncio')
                            and node.func.attr == 'sleep'):
                        has_sync_blocking = True
                        break
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'sleep':
                    has_sync_blocking = True
                    break
            if not has_sync_blocking:
                continue
            has_async = any(kw in source for kw in self.ASYNC_KEYWORDS)
            if not has_async:
                flagged.append(str(py_file.relative_to(project_root)))
        if flagged:
            pytest.fail("Files with sync blocking ops but NO async wrapper:\n  " + "\n  ".join(flagged))


class TestA12_Observability:
    """A12: Files using threading must also import from core.metrics."""

    def test_a12_metrics_used_with_threading(self, all_py_files):
        project_root = Path(__file__).parent.parent
        flagged = []
        for py_file in all_py_files:
            if 'processor.py' not in str(py_file):
                continue
            try:
                source = py_file.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(source)
            except SyntaxError:
                continue
            has_threading = False
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id == 'ThreadPoolExecutor':
                    has_threading = True
                    break
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in ('threading', 'concurrent.futures'):
                            has_threading = True
                            break
                if isinstance(node, ast.ImportFrom) and node.module == 'concurrent.futures':
                    has_threading = True
                    break
            if not has_threading:
                continue
            has_metrics = False
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module and 'core.metrics' in node.module:
                    has_metrics = True
                    break
            if not has_metrics:
                has_metrics = any(kw in source for kw in ['Counter(', 'Timer(', 'Gauge(', 'increment('])
            if not has_metrics:
                flagged.append(str(py_file.relative_to(project_root)))
        if flagged:
            pytest.fail("Files using threading WITHOUT metrics:\n  " + "\n  ".join(flagged))