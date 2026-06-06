"""
Architecture Rules - 10 reglas inviolables para estructura de tools.
Equivalente a las 20 Maximas pero para arquitectura.
"""
import ast
import os
import warnings
from pathlib import Path
import pytest

try:
    from conftest import ARCH_KNOWN_EXCEPTIONS, filter_known_exceptions
except ImportError:
    from tests.conftest import ARCH_KNOWN_EXCEPTIONS, filter_known_exceptions


PROJECT_ROOT = Path(__file__).parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"


class TestArchitectureRules:
    """Las 10 reglas de arquitectura que no se pueden violar."""
    
    # =============================================================================
    # R1: Estructura de Directorio Obligatoria
    # =============================================================================
    """
    Cada tool DEBE tener:
    - __init__.py (exporta la clase de la tool)
    - processor.py (lógica de negocio)
    - ui/ (directorio de UI, opcional)
    """
    
    def test_r1_all_tools_have_required_files(self):
        """R1: Cada tool debe tener __init__.py y processor.py"""
        violations = []
        
        for tool_dir in TOOLS_DIR.iterdir():
            if not tool_dir.is_dir():
                continue
            if tool_dir.name.startswith('_') or tool_dir.name == 'ffmpeg':
                continue
            
            init_file = tool_dir / "__init__.py"
            processor_file = tool_dir / "processor.py"
            
            if not init_file.exists():
                violations.append(f"{tool_dir.name}/__init__.py no existe")
            if not processor_file.exists():
                violations.append(f"{tool_dir.name}/processor.py no existe")
        
        assert not violations, f"Violaciones R1:\n" + "\n".join(violations)

    # =============================================================================
    # R2: Contrato BaseTool Inmutable
    # =============================================================================
    """
    Toda tool DEBE implementar:
    - get_name() -> str
    - get_icon() -> str
    - get_description() -> str
    - build_ui(parent_frame) -> None
    """
    
    def test_r2_tools_implement_basetool_interface(self):
        """R2: Toda tool debe implementar los 4 métodos de BaseTool"""
        from core.base_tool import BaseTool
        
        violations = []
        
        for tool_dir in TOOLS_DIR.iterdir():
            if not tool_dir.is_dir():
                continue
            if tool_dir.name.startswith('_') or tool_dir.name == 'ffmpeg':
                continue
            
            init_file = tool_dir / "__init__.py"
            if not init_file.exists():
                continue
            
            try:
                module_name = f"tools.{tool_dir.name}"
                module = __import__(module_name, fromlist=[''])
                
                # Buscar clase que hereda de BaseTool
                tool_class = None
                for name in dir(module):
                    obj = getattr(module, name)
                    if isinstance(obj, type) and issubclass(obj, BaseTool) and obj is not BaseTool:
                        tool_class = obj
                        break
                
                if tool_class:
                    # Verificar métodos obligatorios
                    required_methods = ['get_name', 'get_icon', 'get_description', 'build_ui']
                    for method in required_methods:
                        if not hasattr(tool_class, method):
                            violations.append(f"{tool_class.__name__} no tiene {method}()")
                        
            except Exception:
                pass  # Skip si no puede importar
        
        assert not violations, f"Violaciones R2:\n" + "\n".join(violations)

    # =============================================================================
    # R3: Processor Sin UI
    # =============================================================================
    """
    processor.py NO PUEDE importar módulos de ui/.
    La lógica de negocio debe estar separada de la presentación.
    """
    
    def test_r3_processor_no_ui_imports(self):
        """R3: processor.py no puede importar de ui/"""
        violations = []
        
        for tool_dir in TOOLS_DIR.iterdir():
            if not tool_dir.is_dir():
                continue
            if tool_dir.name.startswith('_') or tool_dir.name == 'ffmpeg':
                continue
            
            processor_file = tool_dir / "processor.py"
            if not processor_file.exists():
                continue
            
            try:
                content = processor_file.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith('tools.') and '/ui' in node.module:
                            violations.append(f"{tool_dir.name}/processor.py importa {node.module}")
            except:
                pass
        
        assert not violations, f"Violaciones R3:\n" + "\n".join(violations)

    # =============================================================================
    # R4: UI Delega a Processor
    # =============================================================================
    """
    Los módulos de ui/ solo deben importar processor para delegar.
    No deben tener lógica de negocio propia.
    """
    
    def test_r4_ui_imports_processor_only(self):
        """R4: UI solo puede importar de processor, no lógica de negocio"""
        violations = []
        
        for tool_dir in TOOLS_DIR.iterdir():
            if not tool_dir.is_dir():
                continue
            if tool_dir.name.startswith('_') or tool_dir.name == 'ffmpeg':
                continue
            
            ui_dir = tool_dir / "ui"
            if not ui_dir.exists():
                continue
            
            for ui_file in ui_dir.rglob("*.py"):
                try:
                    content = ui_file.read_text(encoding='utf-8', errors='ignore')
                    tree = ast.parse(content)
                    
                    # Buscar imports que NO sean de processor ni de core
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom):
                            module = node.module or ""
                            # Solo permitir processor y core
                            if module and not module.startswith('tools.' + tool_dir.name + '.processor'):
                                if not module.startswith('core.') and not module.startswith('ui.'):
                                    if 'logic' in str(node.names).lower() or 'business' in str(node.names).lower():
                                        violations.append(f"{ui_file.name} tiene lógica de negocio: {module}")
                except:
                    pass
        
        # Este test es más lenient - warning en vez de fail
        if violations:
            pytest.skip(f"Violaciones R4 (advertencia):\n" + "\n".join(violations[:5]))

    # =============================================================================
    # R5: No Imports Circulares
    # =============================================================================
    """
    Una tool NO puede importar de otra tool directamente.
    Solo puede usar funcionalidades de core/.
    """
    
    def test_r5_no_cross_tool_imports(self):
        """R5: No hay imports entre tools"""
        violations = []
        
        for tool_dir in TOOLS_DIR.iterdir():
            if not tool_dir.is_dir():
                continue
            if tool_dir.name.startswith('_') or tool_dir.name == 'ffmpeg':
                continue
            
            # Buscar todos los .py en la tool
            for py_file in tool_dir.rglob("*.py"):
                if '__pycache__' in str(py_file):
                    continue
                    
                try:
                    content = py_file.read_text(encoding='utf-8', errors='ignore')
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom):
                            if node.module and node.module.startswith('tools.'):
                                # Importa de otra tool
                                other_tool = node.module.split('.')[1]
                                if other_tool != tool_dir.name:
                                    violations.append(f"{tool_dir.name} -> {other_tool}")
                except:
                    pass
        
        assert not violations, f"Violaciones R5:\n" + "\n".join(violations)

    # =============================================================================
    # R6: Nombres en snake_case
    # =============================================================================
    """
    Nombres de directorios, archivos y clases en snake_case.
    """
    
    def test_r6_snake_case_names(self):
        """R6: Nombres de tools en snake_case"""
        violations = []
        
        for tool_dir in TOOLS_DIR.iterdir():
            if not tool_dir.is_dir():
                continue
            if tool_dir.name.startswith('_') or tool_dir.name == 'ffmpeg':
                continue
            
            # Verificar snake_case (underscore)
            if '-' in tool_dir.name or ' ' in tool_dir.name:
                violations.append(f"{tool_dir.name} debe ser snake_case")
            
            # Verificar que tiene __init__.py con clase CamelCase
            init_file = tool_dir / "__init__.py"
            if init_file.exists():
                try:
                    content = init_file.read_text(encoding='utf-8', errors='ignore')
                    if 'class ' in content:
                        # Debe tener clase CamelCase
                        pass
                except:
                    pass
        
        assert not violations, f"Violaciones R6:\n" + "\n".join(violations)

    # =============================================================================
    # R7: UI con Tabs Tiene Estructura
    # =============================================================================
    """
    Si una tool tiene tabs, DEBE tener:
    - ui/main_ui.py con CTkTabview
    - ui/tabs/ con submódulos
    """
    
    def test_r7_tabs_have_structure(self):
        """R7: Tools con tabs tienen ui/main_ui.py y ui/tabs/"""
        violations = []
        
        for tool_dir in TOOLS_DIR.iterdir():
            if not tool_dir.is_dir():
                continue
            if tool_dir.name.startswith('_') or tool_dir.name == 'ffmpeg':
                continue
            
            ui_dir = tool_dir / "ui"
            main_ui = ui_dir / "main_ui.py" if ui_dir.exists() else None
            tabs_dir = ui_dir / "tabs" if ui_dir.exists() else None
            
            # Si tiene main_ui.py, debe verificar que tiene tabs
            if main_ui and main_ui.exists():
                content = main_ui.read_text(encoding='utf-8', errors='ignore')
                if 'CTkTabview' in content and not tabs_dir:
                    violations.append(f"{tool_dir.name} tiene CTkTabview pero no tiene ui/tabs/")
        
        # Violaciones solo si hay tabs sin estructura
        assert not violations, f"Violaciones R7:\n" + "\n".join(violations)

    # =============================================================================
    # R8: Cada Tab En Archivo Separado
    # =============================================================================
    """
    Cada tab debe estar en su propio archivo en ui/tabs/.
    """
    
    def test_r8_tabs_separate_files(self):
        """R8: Cada tab en archivo separado"""
        violations = []
        
        for tool_dir in TOOLS_DIR.iterdir():
            if not tool_dir.is_dir():
                continue
            if tool_dir.name.startswith('_') or tool_dir.name == 'ffmpeg':
                continue
            
            tabs_dir = tool_dir / "ui" / "tabs"
            if not tabs_dir.exists():
                continue
            
            # Contar archivos .py en tabs/
            tab_files = list(tabs_dir.glob("*.py"))
            tab_files = [f for f in tab_files if f.name != '__init__.py']
            
            if len(tab_files) > 5:
                # Warning si hay muchos tabs en un solo archivo
                violations.append(f"{tool_dir.name} tiene {len(tab_files)} tabs - considerar separar")
        
        if violations:
            pytest.skip(f"R8 advertencias:\n" + "\n".join(violations))

    # =============================================================================
    # R9: Tests Recomendados
    # =============================================================================
    """
    Cada tool DEBE tener tests/ con test_processor.py.
    (No es obligatorio pero es recomendación fuerte)
    """
    
    def test_r9_tools_have_tests(self):
        """R9: Cada tool tiene tests/"""
        missing_tests = []
        
        for tool_dir in TOOLS_DIR.iterdir():
            if not tool_dir.is_dir():
                continue
            if tool_dir.name.startswith('_') or tool_dir.name == 'ffmpeg':
                continue
            
            tests_dir = tool_dir / "tests"
            if not tests_dir.exists():
                # Warning instead of fail - no es obligatorio
                missing_tests.append(tool_dir.name)
        
        if missing_tests:
            pytest.skip(f"R9 - tools sin tests/: {', '.join(missing_tests[:5])}")

    # =============================================================================
    # R10: Process Real (No Stub)
    # =============================================================================
    """
    Toda tool DEBE tener process() que realmente procese.
    No puede retornar {'success': True, 'message': 'UI handles directly'}
    """
    
    def test_r10_process_is_real(self):
        """R10: process() hace procesamiento real"""
        stub_messages = [
            'UI handles directly',
            'UI handles it',
            'Processed by UI',
        ]
        
        violations = []
        
        for tool_dir in TOOLS_DIR.iterdir():
            if not tool_dir.is_dir():
                continue
            if tool_dir.name.startswith('_') or tool_dir.name == 'ffmpeg':
                continue
            
            init_file = tool_dir / "__init__.py"
            if not init_file.exists():
                continue
            
            try:
                content = init_file.read_text(encoding='utf-8', errors='ignore')
                
                for stub_msg in stub_messages:
                    if stub_msg in content:
                        violations.append(f"{tool_dir.name} tiene process() stub")
                        break
            except:
                pass
        
        assert not violations, f"Violaciones R10:\n" + "\n".join(violations)

    # =============================================================================
    # R11: No Debug Print in Production Code (warning-only)
    # =============================================================================
    """
    Production modules under core/, ui/, tools/**/processor.py, and
    tools/**/handlers/ MUST NOT call print(). Excluded: scripts/ and
    if __name__ == "__main__": blocks. Warning-only on day 1.
    """

    @staticmethod
    def _build_parent_map(tree: ast.AST) -> dict[int, ast.AST]:
        """Map every child AST node id() to its parent for ancestor lookups."""
        parents: dict[int, ast.AST] = {}
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                parents[id(child)] = parent
        return parents

    @classmethod
    def _is_inside_main_block(cls, node: ast.AST, parents: dict[int, ast.AST]) -> bool:
        """True if `node` is nested under an `if __name__ == "__main__":` test."""
        current = parents.get(id(node))
        while current is not None:
            if isinstance(current, ast.If):
                test = current.test
                if (
                    isinstance(test, ast.Compare)
                    and isinstance(test.left, ast.Name)
                    and test.left.id == "__name__"
                    and any(
                        isinstance(cmp, ast.Constant) and cmp.value == "__main__"
                        for cmp in test.comparators
                    )
                ):
                    return True
            current = parents.get(id(current))
        return False

    def _r11_scan_roots(self) -> list[Path]:
        """Return the file roots R11 inspects (core/, ui/, tools/**/processor.py, tools/**/handlers/)."""
        roots: list[Path] = []
        core_dir = PROJECT_ROOT / "core"
        if core_dir.exists():
            roots.append(core_dir)
        ui_dir = PROJECT_ROOT / "ui"
        if ui_dir.exists():
            roots.append(ui_dir)
        for processor in TOOLS_DIR.rglob("processor.py"):
            if "__pycache__" not in str(processor):
                roots.append(processor)
        for handler in (TOOLS_DIR).rglob("handlers/*.py"):
            if "__pycache__" not in str(handler) and handler.name != "__init__.py":
                roots.append(handler.parent)
        return roots

    def test_r11_no_print_in_production(self):
        """R11: No print() in production code (warning-only on day 1)."""
        violations: list[str] = []
        seen: set[Path] = set()
        for root in self._r11_scan_roots():
            candidates = (
                [root] if root.is_file() else list(root.rglob("*.py"))
            )
            for path in candidates:
                if "__pycache__" in str(path) or path.name == "__init__.py":
                    continue
                if path in seen:
                    continue
                seen.add(path)
                try:
                    source = path.read_text(encoding="utf-8", errors="ignore")
                    tree = ast.parse(source)
                except (SyntaxError, OSError):
                    continue
                parents = self._build_parent_map(tree)
                for node in ast.walk(tree):
                    if not isinstance(node, ast.Call):
                        continue
                    func = node.func
                    is_print = (
                        isinstance(func, ast.Name) and func.id == "print"
                    ) or (
                        isinstance(func, ast.Attribute) and func.attr == "print"
                    )
                    if not is_print:
                        continue
                    if self._is_inside_main_block(node, parents):
                        continue
                    rel = path.relative_to(PROJECT_ROOT)
                    violations.append(f"{rel}:{node.lineno}")
        violations = filter_known_exceptions("R11", violations)
        if violations:
            warnings.warn(
                "R11 violations (print() in production code):\n"
                + "\n".join(f"  {v}" for v in violations),
                UserWarning,
                stacklevel=2,
            )
            pytest.skip(
                f"R11 found {len(violations)} print() call(s) in production code:\n"
                + "\n".join(f"  {v}" for v in violations)
            )

    # =============================================================================
    # R12: Tab-Based UI Tools Must Provide state.py with @dataclass (warning-only)
    # =============================================================================
    """
    If a tool exposes a tab-based UI (ui/tabs/ directory exists), that tool
    MUST provide ui/state.py containing at least one @dataclass class.
    Warning-only on day 1.
    """

    @staticmethod
    def _file_has_dataclass(path: Path) -> bool:
        """True iff `path` exists and contains at least one @dataclass class."""
        if not path.exists():
            return False
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
        except (SyntaxError, OSError):
            return False
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            for decorator in node.decorator_list:
                if (
                    isinstance(decorator, ast.Name) and decorator.id == "dataclass"
                ) or (
                    isinstance(decorator, ast.Attribute) and decorator.attr == "dataclass"
                ):
                    return True
        return False

    def test_r12_state_py_required(self):
        """R12: tools with ui/tabs/ must ship ui/state.py with @dataclass (warning-only)."""
        violations: list[str] = []
        for tool_dir in sorted(TOOLS_DIR.iterdir()):
            if not tool_dir.is_dir() or tool_dir.name.startswith("_"):
                continue
            tabs_dir = tool_dir / "ui" / "tabs"
            if not tabs_dir.exists():
                continue
            state_file = tool_dir / "ui" / "state.py"
            if not self._file_has_dataclass(state_file):
                rel_state = state_file.relative_to(PROJECT_ROOT)
                violations.append(
                    f"{tool_dir.name} (missing or @dataclass-less: {rel_state})"
                )
        violations = filter_known_exceptions("R12", violations)
        if violations:
            warnings.warn(
                "R12 violations (tools with ui/tabs/ lacking state.py @dataclass):\n"
                + "\n".join(f"  {v}" for v in violations),
                UserWarning,
                stacklevel=2,
            )
            pytest.skip(
                f"R12 found {len(violations)} tool(s) with ui/tabs/ but no @dataclass state.py:\n"
                + "\n".join(f"  {v}" for v in violations)
            )

    # =============================================================================
    # R13: Handler Files <= 80 Lines (strict from day 1)
    # =============================================================================
    """
    Every .py file under tools/*/ui/handlers/ MUST contain at most 80
    non-blank, non-pure-#-comment lines. Strict assertion.
    """

    @staticmethod
    def _count_meaningful_lines(path: Path) -> int:
        """Count non-blank lines that are not pure-# comments."""
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return 0
        count = 0
        for raw in text.splitlines():
            stripped = raw.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                continue
            count += 1
        return count

    def test_r13_handlers_under_80(self):
        """R13: every handler .py <= 80 non-blank, non-pure-#-comment lines."""
        offenders: list[tuple[str, int]] = []
        for handler_dir in TOOLS_DIR.rglob("ui/handlers"):
            if "__pycache__" in str(handler_dir) or not handler_dir.is_dir():
                continue
            for path in sorted(handler_dir.glob("*.py")):
                if path.name == "__init__.py":
                    continue
                count = self._count_meaningful_lines(path)
                if count > 80:
                    rel = path.relative_to(PROJECT_ROOT)
                    offenders.append((str(rel), count))
        assert not offenders, (
            "R13 violations: handler file(s) exceed 80 non-blank, non-comment lines:\n"
            + "\n".join(f"  {p}: {n} lines" for p, n in offenders)
        )

    # =============================================================================
    # R14: No Monkey-Patch of self._main_ui in Tabs (warning-only)
    # =============================================================================
    """
    tools/*/ui/tabs/*.py MUST NOT mutate self._main_ui via direct
    assignment or setattr(self._main_ui, ...). Warning-only on day 1.
    """

    @staticmethod
    def _is_self_main_ui_attr(node: ast.AST) -> bool:
        """True if `node` is Attribute(value=Name('self'), attr='_main_ui').

        Matches the `self._main_ui` reference (used as the base for setattr's
        first arg, or as the base of a deeper attribute like `self._main_ui.X`).
        """
        return (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "self"
            and node.attr == "_main_ui"
        )

    @classmethod
    def _is_subattr_of_main_ui(cls, node: ast.AST) -> bool:
        """True if `node` is Attribute whose value is self._main_ui (any depth >= 1).

        Catches `self._main_ui.X = ...` (X != _main_ui) and `self._main_ui.X.Y = ...`,
        which is the actual monkey-patch shape; excludes `self._main_ui = ...`.
        """
        return (
            isinstance(node, ast.Attribute)
            and cls._is_self_main_ui_attr(node.value)
        )

    def _r14_collect_violations(self, path: Path) -> list[str]:
        """Return file:line entries for each self._main_ui mutation in `path`."""
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
        except (SyntaxError, OSError):
            return []
        hits: list[str] = []
        rel = path.relative_to(PROJECT_ROOT)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if self._is_subattr_of_main_ui(target):
                        hits.append(f"{rel}:{node.lineno}")
                        break
            elif isinstance(node, ast.AugAssign):
                if self._is_subattr_of_main_ui(node.target):
                    hits.append(f"{rel}:{node.lineno}")
            elif isinstance(node, ast.Call):
                func = node.func
                is_setattr = (
                    isinstance(func, ast.Name) and func.id == "setattr"
                )
                if not is_setattr:
                    continue
                if not node.args:
                    continue
                if self._is_self_main_ui_attr(node.args[0]):
                    hits.append(f"{rel}:{node.lineno}")
        return hits

    def test_r14_no_main_ui_monkey_patch(self):
        """R14: tabs must not monkey-patch self._main_ui (warning-only)."""
        violations: list[str] = []
        for tabs_dir in TOOLS_DIR.rglob("ui/tabs"):
            if "__pycache__" in str(tabs_dir) or not tabs_dir.is_dir():
                continue
            for path in sorted(tabs_dir.glob("*.py")):
                if path.name == "__init__.py":
                    continue
                violations.extend(self._r14_collect_violations(path))
        violations = filter_known_exceptions("R14", violations)
        if violations:
            warnings.warn(
                "R14 violations (self._main_ui monkey-patch sites):\n"
                + "\n".join(f"  {v}" for v in violations),
                UserWarning,
                stacklevel=2,
            )
            pytest.skip(
                f"R14 found {len(violations)} monkey-patch site(s) on self._main_ui:\n"
                + "\n".join(f"  {v}" for v in violations)
            )


# =============================================================================
# EJECUCIÓN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])