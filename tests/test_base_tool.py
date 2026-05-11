"""
Tests for core/base_tool.py
"""
try:
    import pytest
except ImportError:
    pytest = None
    


def raises_type_error():
    """Helper to check if TypeError is raised (for environments without pytest)."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if pytest:
                with pytest.raises(TypeError):
                    return func(*args, **kwargs)
            else:
                try:
                    return func(*args, **kwargs)
                except TypeError:
                    return True
        return wrapper
    return decorator


class TestBaseTool:
    """Test suite for BaseTool abstract class."""

    def test_base_tool_is_abstract(self):
        """Test that BaseTool cannot be instantiated."""
        from core.base_tool import BaseTool
        
        # Should not be able to instantiate directly
        if pytest:
            with pytest.raises(TypeError):
                BaseTool()
        else:
            try:
                BaseTool()
                assert False, "Expected TypeError"
            except TypeError:
                pass  # Expected

    def test_base_tool_has_required_methods(self):
        """Test BaseTool has all required abstract methods."""
        from core.base_tool import BaseTool
        
        # Get abstract methods
        abstract_methods = BaseTool.__abstractmethods__
        
        assert 'get_name' in abstract_methods
        assert 'get_icon' in abstract_methods
        assert 'get_description' in abstract_methods
        assert 'build_ui' in abstract_methods
        assert 'process' in abstract_methods

    def test_concrete_implementation(self):
        """Test that a class inheriting from BaseTool can be instantiated."""
        from core.base_tool import BaseTool
        
        class ConcreteTool(BaseTool):
            def get_name(self): return "Test"
            def get_icon(self): return "🔧"
            def get_description(self): return "Test desc"
            def build_ui(self, parent_frame): pass
            def process(self, files, options): return {}
        
        tool = ConcreteTool()
        assert tool.get_name() == "Test"
        assert tool.get_icon() == "🔧"
        assert tool.get_description() == "Test desc"

    def test_concrete_impl_all(self):
        """Test that missing abstract methods cause TypeError."""
        from core.base_tool import BaseTool
        
        # Class missing process
        class PartialTool(BaseTool):
            def get_name(self): return "Test"
            def get_icon(self): return "🔧"
            def get_description(self): return "Test"
            def build_ui(self, parent_frame): pass
            # Missing process - should fail
        
        if pytest:
            with pytest.raises(TypeError):
                PartialTool()
        else:
            try:
                PartialTool()
                assert False, "Expected TypeError"
            except TypeError:
                pass  # Expected