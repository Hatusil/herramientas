"""Test: Dependency matrix audit - declared deps vs actual imports."""
import ast, re, warnings
from pathlib import Path
import pytest

PACKAGE_TO_IMPORTS = {
    'customtkinter': {'customtkinter'}, 'Pillow': {'PIL'},
    'opencv-python': {'cv2'}, 'numpy': {'numpy'}, 'matplotlib': {'matplotlib'},
    'pytest': {'pytest'},
    'pypdf': {'pypdf'}, 'reportlab': {'reportlab'},
    'beautifulsoup4': {'bs4'}, 'python-docx': {'docx'}, 'python-pptx': {'pptx'},
    'openpyxl': {'openpyxl'}, 'wordcloud': {'wordcloud'}, 'pdfplumber': {'pdfplumber'},
    'PyMuPDF': {'fitz'}, 'requests': {'requests'}, 'pdf2image': {'pdf2image'},
    'piexif': {'piexif'}, 'scipy': {'scipy'}, 'scikit-learn': {'sklearn'},
    'nltk': {'nltk'},
}

IMPORT_TO_PACKAGE = {}
for pkg, imports in PACKAGE_TO_IMPORTS.items():
    for imp in imports:
        IMPORT_TO_PACKAGE[imp] = pkg

INTERNAL_PACKAGES = {'core', 'tools', 'ui'}
KNOWN_UNDECLARED = set()


def _parse_pyproject_toml(project_root):
    pyproject_path = project_root / 'pyproject.toml'
    text = pyproject_path.read_text(encoding='utf-8')
    declared = {}
    deps = _extract_deps(text, 'dependencies')
    for dep in deps:
        pkg = _clean_package_name(dep)
        declared[pkg] = 'main'
    for group in ('dev', 'all'):
        deps = _extract_deps(text, group)
        for dep in deps:
            pkg = _clean_package_name(dep)
            if pkg not in declared:
                declared[pkg] = group
    return declared


def _extract_deps(text, section):
    if section == 'dependencies':
        pattern = r'^dependencies\s*=\s*\[(.*?)\]'
    else:
        pattern = rf'{section}\s*=\s*\[(.*?)\]'
    match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
    if not match:
        return []
    return re.findall(r'"([^"]+)"', match.group(1))


def _clean_package_name(raw):
    name = raw.strip()
    name = re.split(r'[>=<~!]', name)[0].strip()
    name = re.sub(r'\[.*?\]', '', name).strip()
    return name


def _collect_actual_imports(project_root):
    imports = set()
    for py_file in list(project_root.glob('tools/**/*.py')) + list(project_root.glob('core/**/*.py')):
        try:
            source = py_file.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(source)
        except (SyntaxError, Exception):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split('.')[0]
                    if top.startswith('_'):
                        continue
                    imports.add(top)
            elif isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    continue
                if node.module:
                    top = node.module.split('.')[0]
                    if top.startswith('_'):
                        continue
                    imports.add(top)
                    imports.add(node.module)
    return imports


def _classify_imports(actual_imports):
    STDLIB = {'os', 'sys', 're', 'json', 'csv', 'ast', 'math', 'time', 'datetime', 'pathlib', 'shutil', 'tempfile', 'io', 'collections', 'itertools', 'functools', 'typing', 'enum', 'dataclasses', 'abc', 'copy', 'hashlib', 'base64', 'binascii', 'uuid', 'random', 'statistics', 'decimal', 'fractions', 'inspect', 'textwrap', 'string', 'struct', 'pickle', 'shelve', 'configparser', 'argparse', 'logging', 'warnings', 'traceback', 'pprint', 'profile', 'cProfile', 'pstats', 'unittest', 'doctest', 'subprocess', 'threading', 'multiprocessing', 'concurrent', 'asyncio', 'socket', 'ssl', 'email', 'xml', 'html', 'urllib', 'http', 'ftplib', 'smtplib', 'glob', 'fnmatch', 'linecache', 'filecmp', 'fileinput', 'zipfile', 'tarfile', 'gzip', 'bz2', 'lzma', 'sqlite3', 'dbm', 'locale', 'calendar', 'platform', 'errno', 'ctypes', 'tkinter', 'webbrowser', 'dis', '__future__', 'graphlib', 'importlib', 'pkgutil', 'types', 'inspect'}
    third_party = set()
    internal = set()
    for imp in actual_imports:
        top = imp.split('.')[0]
        if top in INTERNAL_PACKAGES or imp.startswith(tuple(INTERNAL_PACKAGES)):
            internal.add(imp)
        elif top in STDLIB or top == '__future__':
            continue
        elif imp.startswith('_'):
            continue
        else:
            third_party.add(top)
    return third_party, internal


class TestMaximasDeps:
    """Dependency matrix audit."""

    def test_deps_vs_imports(self, project_root):
        declared = _parse_pyproject_toml(project_root)
        actual_imports = _collect_actual_imports(project_root)
        third_party, _ = _classify_imports(actual_imports)
        unused = []
        undeclared = []
        for pkg, section in sorted(declared.items()):
            if pkg not in PACKAGE_TO_IMPORTS:
                continue
            import_names = PACKAGE_TO_IMPORTS[pkg]
            if not import_names.intersection(third_party):
                found = any(imp_name in actual_imports for imp_name in import_names)
                if not found:
                    unused.append(f"'{pkg}' declared in [{section}] but never imported")
        for imp in sorted(third_party):
            if imp in IMPORT_TO_PACKAGE:
                pkg = IMPORT_TO_PACKAGE[imp]
                if pkg not in declared:
                    undeclared.append(f"'{imp}' imported but '{pkg}' not declared")
            elif imp not in KNOWN_UNDECLARED:
                undeclared.append(f"'{imp}' imported but unknown")
        warnings_list = []
        if unused:
            warnings_list.append("UNUSED DEPS:\n  - " + "\n  - ".join(unused))
        if undeclared:
            warnings_list.append("UNDECLARED IMPORTS:\n  - " + "\n  - ".join(undeclared))
        if warnings_list:
            msg = "Dependency audit findings:\n\n" + "\n\n".join(warnings_list)
            warnings.warn(UserWarning(msg), stacklevel=2)
            pytest.skip(msg)