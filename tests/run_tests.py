#!/usr/bin/env python3
"""
Simple test runner for herramientas tests.
Runs tests without requiring pytest installed.
"""
import sys
import os
import tempfile
import shutil
import types

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockCallable:
    """A callable that can be used as a class base."""
    def __init__(self, name="MockClass"):
        self._name = name
    
    def __call__(self, *args, **kwargs):
        return MockCallable()
    
    def __str__(self):
        return f"<MockClass {self._name}>"


class MockModule:
    """Mock module that returns proper callable classes."""
    def __init__(self, name="mock"):
        self._name = name
        self._classes = {}
    
    def __getattr__(self, name):
        if name not in self._classes:
            self._classes[name] = type(name, (MockCallable,), {})
        return self._classes[name]


class MockPytestFixture:
    def __call__(self, func=None, *, scope="function", params=None):
        if func is None:
            return lambda f: f
        return func


class MockPytestMark:
    class skip:
        def __init__(self, reason=""):
            self.reason = reason
        
        def __call__(self, func):
            # Wrap the function to preserve the skip info
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            wrapper.reason = self.reason
            wrapper.__wrapped__ = self
            return wrapper


class MockPytestRaises:
    """Mock for pytest.raises - context manager for testing exceptions."""
    def __init__(self, expected_exception=Exception):
        self.expected_exception = expected_exception
        self._entered = False
    
    def __enter__(self):
        self._entered = True
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            raise AssertionError(f"DExpected {self.expected_exception.__name__} to be raised")
        if not issubclass(exc_type, self.expected_exception):
            raise AssertionError(f"Expected {self.expected_exception.__name__}, got {exc_type.__name__}")
        return True


class MockPytest:
    fixture = MockPytestFixture()
    mark = MockPytestMark()
    pytest = MockPytestMark()
    
    @staticmethod
    def raises(expected_exception=Exception):
        return MockPytestRaises(expected_exception)


sys.modules['pytest'] = MockPytest()

# Better PIL mock that returns proper Image class
class MockPIL:
    class Image:
        class Resampling:
            LANCZOS = 0
        @staticmethod
        def open(path):
            return MockPIL._MockImage()
        def convert(self, mode):
            return self
        def resize(self, size, resample):
            return self
        @staticmethod
        def new(mode, size, color=0):
            return MockPIL._MockImage()
        def paste(self, img, pos, mask=None):
            pass
    
    class _MockImage:
        def __init__(self):
            self.size = (100, 100)
        
        def save(self, path=None, format=None):
            pass
    
    class ImageDraw:
        @staticmethod
        def Draw(size):
            return MockPIL._MockDraw()
    
    class _MockDraw:
        def ellipse(self, *args, **kwargs):
            pass

    # Add __version__ for compatibility
    __version__ = "10.0.0"


# Mock tkinter with proper classes
class MockTkinter:
    class Tk:
        def __init__(self, *args, **kwargs):
            pass
    class Frame:
        def __init__(self, *args, **kwargs):
            pass
    class Label:
        def __init__(self, *args, **kwargs):
            pass
    class Button:
        def __init__(self, *args, **kwargs):
            pass
    class Entry:
        def __init__(self, *args, **kwargs):
            pass
    class Text:
        def __init__(self, *args, **kwargs):
            pass
    class Listbox:
        def __init__(self, *args, **kwargs):
            pass
    class Scrollbar:
        def __init__(self, *args, **kwargs):
            pass
    class filedialog:
        class askopenfilename:
            def __init__(self, *args, **kwargs):
                pass
        class asksaveasfilename:
            def __init__(self, *args, **kwargs):
                pass
        class askdirectory:
            def __init__(self, *args, **kwargs):
                pass
    class messagebox:
        @staticmethod
        def showinfo(*args, **kwargs):
            pass
        @staticmethod
        def showerror(*args, **kwargs):
            pass
        @staticmethod
        def askyesno(*args, **kwargs):
            return True


class MockCustomTkinter:
    class CTk:
        def __init__(self, *args, **kwargs):
            pass
    class CTkFrame:
        def __init__(self, *args, **kwargs):
            pass
    class CTkButton:
        def __init__(self, *args, **kwargs):
            pass
    class CTkLabel:
        def __init__(self, *args, **kwargs):
            pass
    class CTkEntry:
        def __init__(self, *args, **kwargs):
            pass
    class CTkTextbox:
        def __init__(self, *args, **kwargs):
            pass
    class CTkScrollableFrame:
        def __init__(self, *args, **kwargs):
            pass
    class CTkTabview:
        def __init__(self, *args, **kwargs):
            pass
    class CTkProgressBar:
        def __init__(self, *args, **kwargs):
            pass
    class CTkSlider:
        def __init__(self, *args, **kwargs):
            pass
    class CTkSwitch:
        def __init__(self, *args, **kwargs):
            pass
    class CTkOptionMenu:
        def __init__(self, *args, **kwargs):
            pass
    class CTkFont:
        def __init__(self, *args, **kwargs):
            pass
    
    class CTkToplevel:
        def __init__(self, *args, **kwargs):
            pass
    
    @staticmethod
    def set_appearance_mode(theme):
        pass
    
    @staticmethod
    def set_default_color_theme(theme):
        pass


sys.modules['customtkinter'] = MockCustomTkinter()
sys.modules['tkinter'] = MockTkinter()
sys.modules['tkinter.ttk'] = MockModule('ttk')
sys.modules['PIL'] = MockPIL()


# Simple fixture implementation
class Fixtures:
    def __init__(self):
        self._temp_dirs = []
    
    def temp_dir(self):
        tmpdir = tempfile.mkdtemp()
        self._temp_dirs.append(tmpdir)
        return tmpdir
    
    def cleanup(self):
        for d in self._temp_dirs:
            shutil.rmtree(d, ignore_errors=True)
    
    def mock_files(self, temp_dir):
        """Create mock files in temp directory."""
        files = []
        
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
    
    def sample_search_results(self):
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


fixtures = Fixtures()


def get_class_fixtures(cls):
    """Get fixtures defined as @pytest.fixture methods in the test class."""
    result = {}
    for name in dir(cls):
        attr = getattr(cls, name, None)
        # Check for @pytest.fixture decorator (has _pytestfixture_function marker)
        if callable(attr) and hasattr(attr, '_pytestfixture_function'):
            try:
                result[name] = attr(cls)
            except Exception:
                pass
        # Also check for fixture marker via __name__ (newer pytest versions)
        elif callable(attr) and hasattr(attr, '__name__') and hasattr(attr, '_pytestfixturemarker'):
            try:
                result[name] = attr(cls)
            except Exception:
                pass
    return result


def get_fixtures_from_method_signature(method):
    """Get fixture values based on method signature."""
    import inspect
    result = {}
    
    try:
        sig = inspect.signature(method)
    except (ValueError, TypeError):
        return result
    
    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue
        # Check for known fixture names in the parameter
        if param_name == 'temp_dir':
            result['temp_dir'] = fixtures.temp_dir()
        elif param_name == 'mock_files':
            temp_dir = result.get('temp_dir') or fixtures.temp_dir()
            result['mock_files'] = fixtures.mock_files(temp_dir)
        elif param_name == 'sample_search_results':
            result['sample_search_results'] = fixtures.sample_search_results()
    
    return result


def run_test_class(cls, name):
    """Run all test methods in a class."""
    passed = 0
    failed = 0
    skipped = 0
    errors = []
    
    # Get class-level fixtures (methods decorated with @pytest.fixture)
    class_fixtures = get_class_fixtures(cls)
    
    for method_name in dir(cls):
        if method_name.startswith('test_'):
            try:
                method = getattr(cls, method_name)
                
                # Check for pytest.mark.skip decorator
                if hasattr(method, '__wrapped__') and hasattr(method.__wrapped__, 'reason'):
                    print(f'  ⊘ {method_name} (skipped: {method.__wrapped__.reason})')
                    skipped += 1
                    continue
                if hasattr(method, 'reason') and isinstance(method, MockPytestMark.skip):
                    print(f'  ⊘ {method_name} (skipped)')
                    skipped += 1
                    continue
                
                instance = cls()
                
                # First, inject class-level fixture methods into the instance
                for fixture_name, fixture_value in class_fixtures.items():
                    setattr(instance, fixture_name, lambda: fixture_value)
                
                # Get fixtures from method signature
                method_fixtures = get_fixtures_from_method_signature(method)
                
                # Merge fixtures - class fixtures take precedence for same name
                all_fixtures = {**method_fixtures}
                
                # Check if we need fixtures but don't have them
                if not all_fixtures:
                    # Try to get them from method name pattern
                    if 'temp_dir' in method_name:
                        all_fixtures['temp_dir'] = fixtures.temp_dir()
                    if 'mock_files' in method_name:
                        temp_dir = all_fixtures.get('temp_dir') or fixtures.temp_dir()
                        all_fixtures['mock_files'] = fixtures.mock_files(temp_dir)
                    if 'sample_search_results' in method_name:
                        all_fixtures['sample_search_results'] = fixtures.sample_search_results()
                
                # Call setup if it exists
                setup = getattr(instance, 'setup', None)
                if setup:
                    setup()
                
                # Call test with fixtures
                if all_fixtures:
                    getattr(instance, method_name)(**all_fixtures)
                else:
                    getattr(instance, method_name)()
                passed += 1
                print(f'  ✓ {method_name}')
            except Exception as e:
                failed += 1
                print(f'  ✗ {method_name}: {str(e)[:80]}')
                errors.append((method_name, str(e)))
    
    return passed, failed, skipped, errors


def main():
    print('Running herramienta test suite...\n')
    
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    
    # Test constants
    print('=== test_constants.py ===')
    from tests import test_constants
    for cls_name in dir(test_constants):
        cls = getattr(test_constants, cls_name)
        if isinstance(cls, type) and cls_name.startswith('Test'):
            print(f'\n{cls_name}:')
            passed, failed, skipped, errors = run_test_class(cls, cls_name)
            total_passed += passed
            total_failed += failed
            total_skipped += skipped
    
    # Test base_tool
    print('\n=== test_base_tool.py ===')
    from tests import test_base_tool
    for cls_name in dir(test_base_tool):
        cls = getattr(test_base_tool, cls_name)
        if isinstance(cls, type) and cls_name.startswith('Test'):
            print(f'\n{cls_name}:')
            passed, failed, skipped, errors = run_test_class(cls, cls_name)
            total_passed += passed
            total_failed += failed
            total_skipped += skipped
    
    # Test plugin_manager
    print('\n=== test_plugin_manager.py ===')
    from tests import test_plugin_manager
    for cls_name in dir(test_plugin_manager):
        cls = getattr(test_plugin_manager, cls_name)
        if isinstance(cls, type) and cls_name.startswith('Test'):
            print(f'\n{cls_name}:')
            passed, failed, skipped, errors = run_test_class(cls, cls_name)
            total_passed += passed
            total_failed += failed
            total_skipped += skipped
    
    # Test search_processor
    print('\n=== test_search_processor.py ===')
    from tests import test_search_processor
    for cls_name in dir(test_search_processor):
        cls = getattr(test_search_processor, cls_name)
        if isinstance(cls, type) and cls_name.startswith('Test'):
            print(f'\n{cls_name}:')
            passed, failed, skipped, errors = run_test_class(cls, cls_name)
            total_passed += passed
            total_failed += failed
            total_skipped += skipped
    
    # Test hash_processor
    print('\n=== test_hash_processor.py ===')
    from tests import test_hash_processor
    for cls_name in dir(test_hash_processor):
        cls = getattr(test_hash_processor, cls_name)
        if isinstance(cls, type) and cls_name.startswith('Test'):
            print(f'\n{cls_name}:')
            passed, failed, skipped, errors = run_test_class(cls, cls_name)
            total_passed += passed
            total_failed += failed
            total_skipped += skipped
    
    # Test rename_processor
    print('\n=== test_rename_processor.py ===')
    from tests import test_rename_processor
    for cls_name in dir(test_rename_processor):
        cls = getattr(test_rename_processor, cls_name)
        if isinstance(cls, type) and cls_name.startswith('Test'):
            print(f'\n{cls_name}:')
            passed, failed, skipped, errors = run_test_class(cls, cls_name)
            total_passed += passed
            total_failed += failed
            total_skipped += skipped
    
    # Test scrubber_processor
    print('\n=== test_scrubber_processor.py ===')
    from tests import test_scrubber_processor
    for cls_name in dir(test_scrubber_processor):
        cls = getattr(test_scrubber_processor, cls_name)
        if isinstance(cls, type) and cls_name.startswith('Test'):
            print(f'\n{cls_name}:')
            passed, failed, skipped, errors = run_test_class(cls, cls_name)
            total_passed += passed
            total_failed += failed
            total_skipped += skipped
    
    # Cleanup
    fixtures.cleanup()
    
    print('\n\n=== RESULTS ===')
    print(f'Passed: {total_passed}')
    print(f'Failed: {total_failed}')
    print(f'Skipped: {total_skipped}')
    print(f'Total: {total_passed + total_failed + total_skipped}')
    
    return 0 if total_failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())