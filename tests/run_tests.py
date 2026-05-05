#!/usr/bin/env python3
"""
Simple test runner for herramientas tests.
Runs tests without requiring pytest installed.
"""
import sys
import os
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock problematic dependencies
class MockModule:
    def __getattr__(self, name):
        return lambda *args, **kwargs: None

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
            pass
    
    class ImageDraw:
        @staticmethod
        def Draw(size):
            return MockPIL._MockDraw()
    
    class _MockDraw:
        def ellipse(self, *args, **kwargs):
            pass

sys.modules['customtkinter'] = MockModule()
sys.modules['tkinter'] = MockModule()
sys.modules['tkinter.ttk'] = MockModule()
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


def get_fixtures(method_name):
    """Get fixtures needed for a test method."""
    result = {}
    if 'temp_dir' in method_name:
        result['temp_dir'] = fixtures.temp_dir()
    if 'mock_files' in method_name:
        result['mock_files'] = fixtures.mock_files(result.get('temp_dir', fixtures.temp_dir()))
    if 'sample_search_results' in method_name:
        result['sample_search_results'] = fixtures.sample_search_results()
    return result


def run_test_class(cls, name):
    """Run all test methods in a class."""
    passed = 0
    failed = 0
    errors = []
    
    for method_name in dir(cls):
        if method_name.startswith('test_'):
            try:
                instance = cls()
                # Get fixtures for this method
                fixture_kwargs = get_fixtures(method_name)
                
                # Call setup if it exists and needs fixtures
                setup = getattr(instance, 'setup', None)
                if setup:
                    if 'temp_dir' in fixture_kwargs:
                        instance.temp_dir = fixture_kwargs['temp_dir']
                    if 'mock_files' in fixture_kwargs:
                        instance.mock_files = fixture_kwargs['mock_files']
                    if 'sample_search_results' in fixture_kwargs:
                        instance.sample_search_results = fixture_kwargs['sample_search_results']
                    setup()
                
                # Call test with fixtures
                if fixture_kwargs:
                    getattr(instance, method_name)(**fixture_kwargs)
                else:
                    getattr(instance, method_name)()
                passed += 1
                print(f'  ✓ {method_name}')
            except Exception as e:
                failed += 1
                print(f'  ✗ {method_name}: {str(e)[:80]}')
                errors.append((method_name, str(e)))
    
    return passed, failed, errors


def main():
    print('Running herramientas test suite...\n')
    
    total_passed = 0
    total_failed = 0
    
    # Test constants
    print('=== test_constants.py ===')
    from tests import test_constants
    for cls_name in dir(test_constants):
        cls = getattr(test_constants, cls_name)
        if isinstance(cls, type) and cls_name.startswith('Test'):
            print(f'\n{cls_name}:')
            passed, failed, errors = run_test_class(cls, cls_name)
            total_passed += passed
            total_failed += failed
    
    # Test base_tool
    print('\n=== test_base_tool.py ===')
    from tests import test_base_tool
    for cls_name in dir(test_base_tool):
        cls = getattr(test_base_tool, cls_name)
        if isinstance(cls, type) and cls_name.startswith('Test'):
            print(f'\n{cls_name}:')
            passed, failed, errors = run_test_class(cls, cls_name)
            total_passed += passed
            total_failed += failed
    
    # Test plugin_manager
    print('\n=== test_plugin_manager.py ===')
    from tests import test_plugin_manager
    for cls_name in dir(test_plugin_manager):
        cls = getattr(test_plugin_manager, cls_name)
        if isinstance(cls, type) and cls_name.startswith('Test'):
            print(f'\n{cls_name}:')
            passed, failed, errors = run_test_class(cls, cls_name)
            total_passed += passed
            total_failed += failed
    
    # Test search_processor
    print('\n=== test_search_processor.py ===')
    from tests import test_search_processor
    for cls_name in dir(test_search_processor):
        cls = getattr(test_search_processor, cls_name)
        if isinstance(cls, type) and cls_name.startswith('Test'):
            print(f'\n{cls_name}:')
            passed, failed, errors = run_test_class(cls, cls_name)
            total_passed += passed
            total_failed += failed
    
    # Cleanup
    fixtures.cleanup()
    
    print('\n\n=== RESULTS ===')
    print(f'Passed: {total_passed}')
    print(f'Failed: {total_failed}')
    print(f'Total: {total_passed + total_failed}')
    
    return 0 if total_failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())