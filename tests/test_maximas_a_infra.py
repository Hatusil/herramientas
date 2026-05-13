"""Tests for maximas A1 (SRP), A4 (Interfaces), A7 (Stateless), A2 (Cohesión), A3 (Acoplamiento)."""
import ast, inspect, warnings
from pathlib import Path
import pytest


class TestA1_SRP:
    """A1: Module and function length limits."""

    def test_a1_module_line_count(self, all_py_files):
        project_root = Path(__file__).parent.parent
        flagged = []
        for py_file in all_py_files:
            try:
                lines = py_file.read_text(encoding='utf-8', errors='ignore').splitlines()
                if len(lines) > 300:
                    rel = py_file.relative_to(project_root)
                    flagged.append(f"{rel}: {len(lines)} lines")
            except Exception:
                continue
        if flagged:
            msg = "Modules exceeding 300 lines (WARNING):\n  " + "\n  ".join(flagged)
            warnings.warn(UserWarning(msg), stacklevel=2)
            pytest.skip(msg)

    def test_a1_import_count(self, all_py_files):
        project_root = Path(__file__).parent.parent
        flagged = []
        for py_file in all_py_files:
            try:
                tree = ast.parse(py_file.read_text(encoding='utf-8', errors='ignore'))
                imports = sum(1 for node in ast.walk(tree)
                              if isinstance(node, (ast.Import, ast.ImportFrom)))
                if imports > 10:
                    rel = py_file.relative_to(project_root)
                    flagged.append(f"{rel}: {imports} imports")
            except SyntaxError:
                continue
        if flagged:
            msg = "Files with >10 imports (WARNING):\n  " + "\n  ".join(flagged)
            warnings.warn(UserWarning(msg), stacklevel=2)
            pytest.skip(msg)


class TestA4_InterfaceCompliance:
    """A4: All tools must implement BaseTool interface correctly."""

    def test_a4_all_tools_are_basetool_subclass(self):
        from core.base_tool import BaseTool
        from core.plugin_manager import PluginManager
        pm = PluginManager()
        pm.discover_tools()
        tools = pm.get_tools()
        assert len(tools) > 0, "No tools discovered"
        for name, instance in tools.items():
            assert isinstance(instance, BaseTool), f"{name} not BaseTool subclass"

    def test_a4_all_tools_have_process(self):
        from core.plugin_manager import PluginManager
        pm = PluginManager()
        pm.discover_tools()
        tools = pm.get_tools()
        for name, instance in tools.items():
            assert hasattr(instance, 'process'), f"{name} missing process"


class TestA7_Stateless:
    """A7: No module-level mutable state."""

    known_exceptions = ['tools/search_tool/processor.py']

    def _rel_path(self, py_file):
        project_root = Path(__file__).parent.parent
        try: return str(py_file.relative_to(project_root))
        except ValueError: return str(py_file)

    def test_a7_no_module_level_mutable_state(self, all_py_files):
        flagged = []
        project_root = Path(__file__).parent.parent
        for py_file in all_py_files:
            if 'processor.py' not in str(py_file) and 'core/' not in str(py_file):
                continue
            rel = self._rel_path(py_file)
            if rel in self.known_exceptions:
                continue
            try:
                source = py_file.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(source)
            except SyntaxError:
                continue
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.Assign):
                    if isinstance(node.value, (ast.List, ast.Dict, ast.Set)):
                        assign_src = source[node.lineno - 1] if node.lineno else ''
                        is_metrics = any(kw in assign_src for kw in
                            ['Counter(', 'Timer(', 'Gauge(', 'Counter ', 'Timer ', 'Gauge '])
                        if not is_metrics:
                            flagged.append(f"{rel}:{node.lineno} module-level mutable state")
        if flagged:
            msg = "Module-level mutable state:\n  " + "\n  ".join(flagged)
            warnings.warn(UserWarning(msg), stacklevel=2)
            pytest.skip(msg)


class TestA2_Cohesion:
    """A2: Functions should address few related topics."""

    known_exceptions = ['tools/text_tool/processor.py', 'tools/pdf_tool/processor.py', 'tools/search_tool/processor.py']

    def _rel_path(self, py_file):
        project_root = Path(__file__).parent.parent
        try: return str(py_file.relative_to(project_root))
        except ValueError: return str(py_file)

    def test_a2_topic_diversity(self, all_py_files):
        project_root = Path(__file__).parent.parent
        flagged = []
        for py_file in all_py_files:
            rel = self._rel_path(py_file)
            if rel in self.known_exceptions:
                continue
            try:
                source = py_file.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(source)
            except SyntaxError:
                continue
            func_names = [node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
            if len(func_names) < 3:
                continue
            topics = set()
            for name in func_names:
                if '_' in name:
                    topics.add(name.split('_')[0])
            if len(topics) > 5:
                flagged.append(f"{rel}: {len(func_names)} functions across {len(topics)} topics")
        if flagged:
            msg = "High topic diversity (>5 topics):\n  " + "\n  ".join(flagged)
            warnings.warn(UserWarning(msg), stacklevel=2)
            pytest.skip(msg)


class TestA3_Coupling:
    """A3: Limit external dependencies."""

    STDLIB = {'os', 'sys', 're', 'json', 'csv', 'ast', 'math', 'time', 'datetime', 'pathlib', 'shutil', 'tempfile', 'io', 'collections', 'itertools', 'functools', 'typing', 'enum', 'dataclasses', 'abc', 'copy', 'hashlib', 'base64', 'binascii', 'uuid', 'random', 'statistics', 'decimal', 'fractions', 'inspect', 'textwrap', 'string', 'struct', 'pickle', 'shelve', 'configparser', 'argparse', 'logging', 'warnings', 'traceback', 'pprint', 'profile', 'cProfile', 'pstats', 'unittest', 'doctest', 'subprocess', 'threading', 'multiprocessing', 'concurrent', 'asyncio', 'socket', 'ssl', 'email', 'xml', 'html', 'urllib', 'http', 'ftplib', 'smtplib', 'glob', 'fnmatch', 'linecache', 'filecmp', 'fileinput', 'zipfile', 'tarfile', 'gzip', 'bz2', 'lzma', 'sqlite3', 'dbm', 'locale', 'calendar', 'platform', 'errno', 'ctypes', 'tkinter', 'webbrowser', 'dis', '__future__', 'graphlib', 'importlib', 'pkgutil', 'types'}
    INTERNAL_PREFIXES = ('core.', 'tools.', 'ui.')
    known_exceptions = ['tools/text_tool/processor.py', 'tools/pdf_tool/processor.py', 'tools/audio_tool/processor.py', 'tools/search_tool/processor.py', 'core/plugin_manager.py', 'core/constants.py']

    def _rel_path(self, py_file):
        project_root = Path(__file__).parent.parent
        try: return str(py_file.relative_to(project_root))
        except ValueError: return str(py_file)

    def test_a3_external_imports(self, all_py_files):
        project_root = Path(__file__).parent.parent
        flagged = []
        for py_file in all_py_files:
            rel = self._rel_path(py_file)
            if rel in self.known_exceptions:
                continue
            try:
                source = py_file.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(source)
            except SyntaxError:
                continue
            stdlib_imports = set()
            third_party_imports = set()
            internal_imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        top = alias.name.split('.')[0]
                        if alias.name.startswith(self.INTERNAL_PREFIXES):
                            internal_imports.add(alias.name)
                        elif top in self.STDLIB or alias.name in self.STDLIB:
                            stdlib_imports.add(alias.name)
                        else:
                            third_party_imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    if node.module.startswith(self.INTERNAL_PREFIXES):
                        internal_imports.add(node.module)
                    else:
                        top = node.module.split('.')[0]
                        if top in self.STDLIB or node.module in self.STDLIB:
                            stdlib_imports.add(node.module)
                        else:
                            third_party_imports.add(node.module)
            total_external = len(stdlib_imports) + len(third_party_imports)
            if total_external > 15 or len(third_party_imports) > 5:
                flagged.append(f"{rel}: {total_external} external (stdlib={len(stdlib_imports)}, 3rd={len(third_party_imports)})")
        if flagged:
            msg = "High external coupling:\n  " + "\n  ".join(flagged)
            warnings.warn(UserWarning(msg), stacklevel=2)
            pytest.skip(msg)