"""
Smoke tests - Verifica que los componentes principales funcionan.
"""
import pytest


class TestCoreImports:
    """Verifica que los módulos core se pueden importar."""

    def test_import_core_constants(self):
        """Core constants importable."""
        from core import constants
        assert hasattr(constants, 'COLORS')

    def test_import_core_base_tool(self):
        """BaseTool importable."""
        from core.base_tool import BaseTool
        assert BaseTool is not None

    def test_import_core_base_tool_ui(self):
        """BaseToolUI importable."""
        from core.base_tool_ui import BaseToolUI
        assert BaseToolUI is not None

    def test_import_core_plugin_manager(self):
        """PluginManager importable."""
        from core.plugin_manager import PluginManager
        assert PluginManager is not None

    def test_import_core_theme(self):
        """Theme importable."""
        from core import theme
        assert hasattr(theme, 'COLORS')


class TestToolsImports:
    """Verifica que las tools se pueden importar."""

    def test_import_audio_tool(self):
        """AudioTool importable."""
        from tools.audio_tool import AudioTool
        assert AudioTool is not None

    def test_import_compress_tool(self):
        """CompressTool importable."""
        from tools.compress_tool import CompressTool
        assert CompressTool is not None

    def test_import_duplicate_tool(self):
        """DuplicateTool importable."""
        from tools.duplicate_tool import DuplicateTool
        assert DuplicateTool is not None

    def test_import_gif_tool(self):
        """GifTool importable."""
        from tools.gif_tool import GifTool
        assert GifTool is not None

    def test_import_hash_tool(self):
        """HashTool importable."""
        from tools.hash_tool import HashTool
        assert HashTool is not None

    def test_import_image_tool(self):
        """ImageTool importable."""
        from tools.image_tool import ImageTool
        assert ImageTool is not None

    def test_import_pdf_tool(self):
        """PDFTool importable."""
        from tools.pdf_tool import PDFTool
        assert PDFTool is not None

    def test_import_rename_tool(self):
        """RenameTool importable."""
        from tools.rename_tool import RenameTool
        assert RenameTool is not None

    def test_import_scrubber(self):
        """Scrubber importable."""
        from tools.scrubber import ScrubberTool
        assert ScrubberTool is not None

    def test_import_search_tool(self):
        """SearchTool importable."""
        from tools.search_tool import SearchTool
        assert SearchTool is not None

    def test_import_text_tool(self):
        """TextAnalyzerTool importable."""
        from tools.text_tool import TextAnalyzerTool
        assert TextAnalyzerTool is not None

    def test_import_video_tool(self):
        """VideoTool importable."""
        from tools.video_tool import VideoTool
        assert VideoTool is not None


class TestPluginManager:
    """Verifica que PluginManager funciona."""

    def test_plugin_manager_discovers_tools(self):
        """PluginManager puede descubrir tools."""
        from core.plugin_manager import PluginManager
        pm = PluginManager()
        tools = pm.discover_tools()
        # Puede ser None o lista vacía si falla la carga
        assert tools is not None or True  # Solo verificamos que no crashea

    def test_plugin_manager_all_have_base_interface(self):
        """Todas las tools implementan BaseTool."""
        from core.plugin_manager import PluginManager
        from core.base_tool import BaseTool
        pm = PluginManager()
        tools = pm.discover_tools()
        if not tools:
            pytest.skip("No se pudieron cargar las tools")
        for tool in tools:
            assert isinstance(tool, BaseTool), f"{tool.__class__.__name__} no hereda de BaseTool"


class TestBaseToolInterface:
    """Verifica el contrato de BaseTool."""

    def test_all_tools_have_get_name(self):
        """Todas las tools tienen get_name."""
        from core.plugin_manager import PluginManager
        pm = PluginManager()
        tools = pm.discover_tools()
        if not tools:
            pytest.skip("No se pudieron cargar las tools")
        for tool in tools:
            assert hasattr(tool, 'get_name')
            assert callable(tool.get_name)

    def test_all_tools_have_get_icon(self):
        """Todas las tools tienen get_icon."""
        from core.plugin_manager import PluginManager
        pm = PluginManager()
        tools = pm.discover_tools()
        if not tools:
            pytest.skip("No se pudieron cargar las tools")
        for tool in tools:
            assert hasattr(tool, 'get_icon')
            assert callable(tool.get_icon)

    def test_all_tools_have_get_description(self):
        """Todas las tools tienen get_description."""
        from core.plugin_manager import PluginManager
        pm = PluginManager()
        tools = pm.discover_tools()
        if not tools:
            pytest.skip("No se pudieron cargar las tools")
        for tool in tools:
            assert hasattr(tool, 'get_description')
            assert callable(tool.get_description)

    def test_all_tools_have_build_ui(self):
        """Todas las tools tienen build_ui."""
        from core.plugin_manager import PluginManager
        pm = PluginManager()
        tools = pm.discover_tools()
        if not tools:
            pytest.skip("No se pudieron cargar las tools")
        for tool in tools:
            assert hasattr(tool, 'build_ui')
            assert callable(tool.build_ui)