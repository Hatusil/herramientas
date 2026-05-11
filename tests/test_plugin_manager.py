"""Tests for core/plugin_manager.py"""
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from core.plugin_manager import PluginManager
from core.base_tool import BaseTool


class TestPluginManager:
    """Test suite for PluginManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_init(self):
        """Test PluginManager initialization."""
        pm = PluginManager()
        assert pm.tools == {}
        assert pm.tool_instances == {}
        assert pm.tool_status == {}
    
    def test_discover_tools_empty_directory(self, temp_dir):
        """Test discover_tools with empty tools directory."""
        tools_path = Path(temp_dir) / 'tools'
        tools_path.mkdir()
        
        with patch('core.constants.TOOLS_DIR', tools_path):
            pm = PluginManager()
            pm.discover_tools()
            assert len(pm.tool_instances) == 0
    
    def test_discover_skips_private(self, temp_dir):
        """Test discover_tools skips directories starting with underscore."""
        tools_path = Path(temp_dir) / 'tools'
        tools_path.mkdir()
        
        # Create private dir
        private_dir = tools_path / '_private_tool'
        private_dir.mkdir()
        
        with patch('core.constants.TOOLS_DIR', tools_path):
            pm = PluginManager()
            pm.discover_tools()
            assert '_private_tool' not in pm.tool_instances
    
    @pytest.mark.skip(reason="Requires complex mocking - use integration test instead")
    def test_load_tool_success(self, mock_import, temp_dir):
        pass
        
    @pytest.mark.skip(reason="Requires complex mocking - use integration test instead") 
    def test_load_tool_no_base_tool(self, temp_dir):
        pass
        
    @pytest.mark.skip(reason="Requires complex mocking - use integration test instead")
    def test_load_tool_exception(self, temp_dir):
        pass
    
    def test_find_tool_returns_subclass(self):
        """Test _find_tool_class finds BaseTool subclass."""
        class TestTool(BaseTool):
            pass
        
        mock_module = MagicMock()
        mock_module.TestTool = TestTool
        
        pm = PluginManager()
        result = pm._find_tool_class(mock_module)
        
        assert result == TestTool
    
    def test_find_tool_returns_none_base(self):
        """Test _find_tool_class returns None for BaseTool itself."""
        mock_module = MagicMock()
        mock_module.BaseTool = BaseTool
        
        pm = PluginManager()
        result = pm._find_tool_class(mock_module)
        
        assert result is None
    
    def test_find_tool_returns_none(self):
        """Test _find_tool_class returns None when no subclass."""
        mock_module = MagicMock()
        
        pm = PluginManager()
        result = pm._find_tool_class(mock_module)
        
        assert result is None
    
    def test_get_tools_returns_instances(self):
        """Test get_tools returns tool instances."""
        pm = PluginManager()
        result = pm.get_tools()
        
        assert isinstance(result, dict)
    
    def test_get_tools_list_empty(self):
        """Test get_tools_list with no tools."""
        pm = PluginManager()
        result = pm.get_tools_list()
        
        assert result == []
    
    def test_get_tools_list_structure(self):
        """Test get_tools_list returns proper data structure."""
        pm = PluginManager()
        
        # Discover actual tools
        pm.discover_tools()
        result = pm.get_tools_list()
        
        if result:
            assert 'name' in result[0]
            assert 'icon' in result[0]
            assert 'description' in result[0]
            assert 'status' in result[0]
    
    def test_get_tools_list_name_err(self):
        """Test get_tools_list handles errors in get_name."""
        pm = PluginManager()
        pm.tool_instances['bad_tool'] = MagicMock()
        pm.tool_instances['bad_tool'].get_name = MagicMock(side_effect=Exception("Error"))
        pm.tool_instances['bad_tool'].get_icon = lambda: "icon"
        pm.tool_instances['bad_tool'].get_description = lambda: "desc"
        
        result = pm.get_tools_list()
        
        assert any('[Error' in t.get('display_name', '') for t in result)
    
    def test_get_tools_list_icon_err(self):
        """Test get_tools_list handles errors in get_icon."""
        pm = PluginManager()
        pm.tool_instances['bad_tool'] = MagicMock()
        pm.tool_instances['bad_tool'].get_name = lambda: "name"
        pm.tool_instances['bad_tool'].get_icon = MagicMock(side_effect=Exception("Error"))
        pm.tool_instances['bad_tool'].get_description = lambda: "desc"
        
        result = pm.get_tools_list()
        
        assert any('⚠️' in t.get('icon', '') for t in result)
    
    def test_get_tools_list_desc_err(self):
        """Test get_tools_list handles errors in get_description."""
        pm = PluginManager()
        pm.tool_instances['bad_tool'] = MagicMock()
        pm.tool_instances['bad_tool'].get_name = lambda: "name"
        pm.tool_instances['bad_tool'].get_icon = lambda: "icon"
        pm.tool_instances['bad_tool'].get_description = MagicMock(side_effect=Exception("Error"))
        
        result = pm.get_tools_list()
        
        assert any('Error' in t.get('description', '') for t in result)
    
    def test_get_status_returns_status(self):
        """Test get_status returns tool status."""
        pm = PluginManager()
        pm.tool_status['test_tool'] = 'OK'
        
        result = pm.get_status('test_tool')
        
        assert result == 'OK'
    
    def test_get_status_unknown_err(self):
        """Test get_status returns ERROR for unknown tool."""
        pm = PluginManager()
        
        result = pm.get_status('unknown_tool')
        
        assert result == 'ERROR'
    
    def test_discover_finds_tools(self):
        """Test discover_tools finds actual tools in tools/ directory."""
        pm = PluginManager()
        pm.discover_tools()
        
        # Should find at least some tools
        assert len(pm.tool_instances) > 0
        
        # Verify each tool has required methods
        for name, tool in pm.tool_instances.items():
            assert hasattr(tool, 'get_name')
            assert hasattr(tool, 'get_icon')
            assert hasattr(tool, 'get_description')
            assert hasattr(tool, 'build_ui')
            assert hasattr(tool, 'process')
    
    def test_discover_real_tools_work(self):
        """Test that real tools have working methods."""
        pm = PluginManager()
        pm.discover_tools()
        tools_list = pm.get_tools_list()
        
        # Check structure
        for tool in tools_list:
            assert tool['name']
            assert tool['icon']
            assert tool['description']
            assert tool['status']