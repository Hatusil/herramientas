"""
Tests for image_tool.processor module.
"""
import pytest
import types
from pathlib import Path


def load_processor_module():
    """Carga el processor dinámicamente sin conflictos de nombres."""
    tool_dir = Path(__file__).parent.parent
    processor_path = tool_dir / "processor.py"
    namespace = {}
    with open(processor_path, 'r') as f:
        code = compile(f.read(), str(processor_path), 'exec')
        exec(code, namespace)
    return types.SimpleNamespace(**namespace)


processor = load_processor_module()
_ok = processor._ok
_fail = processor._fail
_image_to_dict = processor._image_to_dict
CV2_AVAILABLE = processor.CV2_AVAILABLE


# Tests de helpers internos eliminados - no son parte de la API pública
# Los helpers como _ok, _fail, _image_to_dict son funciones internas del processor


class TestImageAvailability:
    """Tests for library availability."""

    def test_cv2_available_is_bool(self):
        """CV2_AVAILABLE should be a boolean."""
        assert isinstance(CV2_AVAILABLE, bool)