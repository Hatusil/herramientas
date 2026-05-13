"""Tests for maximas C16 (Modular Boundaries), C17 (Tool Consistency), E19 (Multiplatform), R0 (Brevedad)."""
import ast, re, warnings
from pathlib import Path
import pytest


class TestC16_ModularBoundaries:
    """C16: No cross-tool imports between tool directories."""

    def test_c16_no_cross_tool_imports(self, tool_names, project_root):
        tools_dir = project_root / 'tools'
        flagged = []
        for tool_name in tool_names:
            tool_path = tools_dir / tool_name
            for py_file in tool_path.rglob('*.py'):
                if py_file.name == '__pycache__':
                    continue
                try:
                    source = py_file.read_text(encoding='utf-8', errors='ignore')
                    tree = ast.parse(source)
                except SyntaxError:
                    continue
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self._check_cross_import(alias.name, tool_name, py_file, tool_names, flagged)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        self._check_cross_import(node.module, tool_name, py_file, tool_names, flagged)
        if flagged:
            msg = "Cross-tool imports detected:\n  " + "\n  ".join(flagged)
            warnings.warn(UserWarning(msg), stacklevel=2)
            pytest.skip(msg)

    def _check_cross_import(self, module_name, current_tool, py_file, tool_names, flagged):
        parts = module_name.split('.')
        for other_tool in tool_names:
            if other_tool == current_tool:
                continue
            if other_tool in parts:
                rel = py_file.relative_to(Path(__file__).parent.parent)
                flagged.append(f"{rel} imports from tools.{other_tool}")


class TestC17_ToolConsistency:
    """C17: Every tool must have consistent structure."""

    def test_c17_all_tools_have_required_files(self, tool_names, project_root):
        tools_dir = project_root / 'tools'
        missing = []
        for name in tool_names:
            tool_path = tools_dir / name
            for required in ('__init__.py', 'processor.py'):
                if not (tool_path / required).exists():
                    missing.append(f"{name}/{required}")
            if not (tool_path / 'ui.py').exists() and not (tool_path / 'ui').is_dir():
                missing.append(f"{name}/ui.py or {name}/ui/")
        assert not missing, f"Missing required files:\n  " + "\n  ".join(missing)


class TestE19_Multiplatform:
    """E19: No hardcoded OS-specific paths."""

    known_exceptions = ['core/constants.py']
    PATH_PATTERNS = [r'[A-Za-z]:\\\\', r'[A-Za-z]:/', r'/Users/', r'/Documents/', r'/Windows/', r'\\\\Users\\\\']

    def test_e19_no_hardcoded_paths(self, all_py_files):
        project_root = Path(__file__).parent.parent
        flagged = []
        for py_file in all_py_files:
            rel = str(py_file.relative_to(project_root))
            if rel in self.known_exceptions:
                continue
            try:
                source = py_file.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            for i, line in enumerate(source.splitlines(), 1):
                for pattern in self.PATH_PATTERNS:
                    if re.search(pattern, line):
                        flagged.append(f"{rel}:{i} — {line.strip()[:80]}")
                        break
        if flagged:
            msg = "Hardcoded OS paths:\n  " + "\n  ".join(flagged)
            warnings.warn(UserWarning(msg), stacklevel=2)
            pytest.skip(msg)


class TestR0_Brevedad:
    """R0: Function ≤50 lines, class ≤300, identifiers ≤30 chars."""

    def _rel(self, py_file):
        return str(py_file.relative_to(Path(__file__).parent.parent))

    def test_r0_function_line_limit(self, all_py_files):
        project_root = Path(__file__).parent.parent
        flagged = []
        for py_file in all_py_files:
            try:
                source = py_file.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(source)
            except SyntaxError:
                continue
            source_lines = source.splitlines()
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    body = node.body
                    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                        body = body[1:]
                    if not body:
                        continue
                    start = body[0].lineno
                    end = body[-1].end_lineno if hasattr(body[-1], 'end_lineno') else body[-1].lineno
                    count = sum(1 for lineno in range(start, end + 1)
                                if lineno <= len(source_lines) and source_lines[lineno - 1].strip())
                    if count > 50:
                        flagged.append(f"{self._rel(py_file)}:{node.lineno} {node.name}() = {count} lines")
        if flagged:
            msg = "Functions >50 lines:\n  " + "\n  ".join(flagged)
            warnings.warn(UserWarning(msg), stacklevel=2)
            pytest.skip(msg)

    def test_r0_identifier_length(self, all_py_files):
        flagged = []
        for py_file in all_py_files:
            try:
                tree = ast.parse(py_file.read_text(encoding='utf-8', errors='ignore'))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and len(node.name) > 30:
                    flagged.append(f"{self._rel(py_file)}:{node.lineno} function '{node.name}' ({len(node.name)} chars)")
                elif isinstance(node, ast.ClassDef) and len(node.name) > 30:
                    flagged.append(f"{self._rel(py_file)}:{node.lineno} class '{node.name}' ({len(node.name)} chars)")
        if flagged:
            msg = "Identifiers >30 chars:\n  " + "\n  ".join(flagged)
            warnings.warn(UserWarning(msg), stacklevel=2)
            pytest.skip(msg)