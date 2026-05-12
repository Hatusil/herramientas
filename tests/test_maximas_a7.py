"""
Tests for Maxima A7: No module-level mutable state.
"""
import ast
import inspect
from pathlib import Path


def get_module_path(module_name: str) -> Path:
    """Get the path to a module."""
    import importlib.util
    spec = importlib.util.find_spec(module_name.replace('/', '.'))
    if spec and spec.origin:
        return Path(spec.origin)
    return None


def find_mutable_at_module_level(source: str) -> list:
    """Find mutable objects assigned at module level."""
    tree = ast.parse(source)
    mutable = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Module):
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            if isinstance(item.value, (ast.List, ast.Dict, ast.Set)):
                                mutable.append((target.id, item.lineno, type(item.value).__name__))
                            elif isinstance(item.value, ast.ListComp):
                                mutable.append((target.id, item.lineno, 'ListComp'))
                            elif isinstance(item.value, ast.DictComp):
                                mutable.append((target.id, item.lineno, 'DictComp'))
                            elif isinstance(item.value, ast.SetComp):
                                mutable.append((target.id, item.lineno, 'SetComp'))
                        elif isinstance(target, ast.Tuple):
                            pass  # tuple unpacking is OK
                elif isinstance(item, ast.AnnAssign):
                    if isinstance(item.target, ast.Name):
                        if isinstance(item.value, (ast.List, ast.Dict, ast.Set)):
                            mutable.append((item.target.id, item.lineno, type(item.value).__name__))
    
    return mutable


class TestModuleLevelMutableState:
    """Test that modules don't have mutable state at module level."""
    
    def test_pdf_processor_no_mutable_state(self):
        """tools/pdf_tool/processor.py should not have module-level mutable state."""
        module_path = get_module_path('tools/pdf_tool/processor')
        assert module_path is not None, "Module not found"
        
        source = module_path.read_text()
        mutable = find_mutable_at_module_level(source)
        
        assert len(mutable) == 0, f"Found mutable state at module level: {mutable}"
    
    def test_video_processor_no_mutable_state(self):
        """tools/video_tool/processor.py should not have module-level mutable state."""
        module_path = get_module_path('tools/video_tool/processor')
        assert module_path is not None, "Module not found"
        
        source = module_path.read_text()
        mutable = find_mutable_at_module_level(source)
        
        assert len(mutable) == 0, f"Found mutable state at module level: {mutable}"
    
    def test_image_utils_no_mutable_state(self):
        """core/image_utils.py should not have module-level mutable state."""
        module_path = get_module_path('core.image_utils')
        assert module_path is not None, "Module not found"
        
        source = module_path.read_text()
        mutable = find_mutable_at_module_level(source)
        
        assert len(mutable) == 0, f"Found mutable state at module level: {mutable}"
