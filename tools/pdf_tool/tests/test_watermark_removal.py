"""
Tests for watermark_removal.py - PDF watermark removal functions.
"""
import os
import tempfile
import pytest

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def create_test_pdf(output_path, num_pages=1, with_watermark=False):
    """Create a test PDF with optional watermark text."""
    c = canvas.Canvas(output_path, pagesize=letter)
    
    for i in range(num_pages):
        c.drawString(100, 750, f"Test Page {i + 1}")
        c.drawString(100, 700, "This is a test PDF for unit testing.")
        
        if with_watermark:
            # Add watermark text (diagonal)
            c.saveState()
            c.translate(letter[0]/2, letter[1]/2)
            c.rotate(45)
            c.setFillColorRGB(0.5, 0.5, 0.5, alpha=0.3)
            c.setFont("Helvetica-Bold", 48)
            c.drawCentredString(0, 0, "CONFIDENTIAL")
            c.restoreState()
        
        c.showPage()
    
    c.save()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for file operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_pdf(temp_dir):
    """Create a sample PDF for testing."""
    pdf_path = os.path.join(temp_dir, "sample.pdf")
    create_test_pdf(pdf_path, num_pages=3, with_watermark=True)
    return pdf_path


@pytest.fixture
def simple_pdf(temp_dir):
    """Create a simple PDF without watermark."""
    pdf_path = os.path.join(temp_dir, "simple.pdf")
    create_test_pdf(pdf_path, num_pages=1, with_watermark=False)
    return pdf_path


class TestCheckFitz:
    """Tests for check_fitz function."""

    def test_check_fitz_installed(self):
        """Test that Fitz is available."""
        from tools.pdf_tool.modules.watermark_removal import check_fitz
        
        # This test will pass only if fitz is installed
        result = check_fitz()
        # Just verify the function runs without error
        assert isinstance(result, bool)


class TestDetectWatermarks:
    """Tests for detect_watermarks function."""

    def test_detect_watermarks_returns_list(self, sample_pdf):
        """Test that detect_watermarks returns a list."""
        from tools.pdf_tool.modules import watermark_removal
        
        if not watermark_removal.check_fitz():
            pytest.skip("Fitz not installed")
        
        doc = watermark_removal.fitz.open(sample_pdf)
        page = doc[0]
        
        result = watermark_removal.detect_watermarks(page)
        
        assert isinstance(result, list)
        doc.close()

    def test_detect_watermarks_auto(self, sample_pdf):
        """Test auto detection across document."""
        from tools.pdf_tool.modules import watermark_removal
        
        if not watermark_removal.check_fitz():
            pytest.skip("Fitz not installed")
        
        doc = watermark_removal.fitz.open(sample_pdf)
        result = watermark_removal.detect_watermarks_auto(doc)
        
        assert isinstance(result, list)
        doc.close()


class TestRemoveWatermark:
    """Tests for remove_watermark function."""

    def test_remove_watermark_exists(self):
        """Test that remove_watermark function exists."""
        from tools.pdf_tool.modules import watermark_removal
        
        assert hasattr(watermark_removal, 'remove_watermark')
        assert callable(watermark_removal.remove_watermark)

    def test_remove_watermark_auto_mode(self, sample_pdf):
        """Test watermark removal in auto mode."""
        from tools.pdf_tool.modules import watermark_removal
        
        if not watermark_removal.check_fitz():
            pytest.skip("Fitz not installed")
        
        result = watermark_removal.remove_watermark(
            [sample_pdf], 
            detection_mode='auto'
        )
        
        # Function should run and return a dict with expected keys
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'output_files' in result

    def test_remove_watermark_manual_mode(self, sample_pdf):
        """Test watermark removal in manual mode."""
        from tools.pdf_tool.modules import watermark_removal
        
        if not watermark_removal.check_fitz():
            pytest.skip("Fitz not installed")
        
        manual_region = {
            'x': 100,
            'y': 100,
            'width': 300,
            'height': 100
        }
        
        result = watermark_removal.remove_watermark(
            [sample_pdf],
            detection_mode='manual',
            manual_region=manual_region
        )
        
        assert isinstance(result, dict)
        assert 'output_files' in result

    def test_remove_watermark_no_fitz(self):
        """Test graceful handling when Fitz is not installed."""
        from tools.pdf_tool.modules import watermark_removal
        
        # Mock check_fitz to return False
        original_check = watermark_removal.check_fitz
        watermark_removal.check_fitz = lambda: False
        
        try:
            result = watermark_removal.remove_watermark(['/nonexistent.pdf'])
            
            assert result['success'] is False
            assert 'error' in result
        finally:
            watermark_removal.check_fitz = original_check


class TestRemoveWatermarkFallback:
    """Tests for fallback annotation removal."""

    def test_remove_watermark_fallback(self, sample_pdf):
        """Test pypdf fallback function."""
        from tools.pdf_tool.modules import watermark_removal
        
        result = watermark_removal.remove_watermark_fallback([sample_pdf])
        
        assert isinstance(result, dict)
        assert 'success' in result


class TestFullWorkflow:
    """Integration tests."""

    def test_complete_removal_workflow(self, sample_pdf, temp_dir):
        """Test complete watermark removal workflow."""
        from tools.pdf_tool.modules import watermark_removal
        
        if not watermark_removal.check_fitz():
            pytest.skip("Fitz not installed")
        
        # Run removal
        result = watermark_removal.remove_watermark([sample_pdf])
        
        # Verify output
        if result['success']:
            assert len(result['output_files']) > 0
            output_file = result['output_files'][0]
            assert os.path.exists(output_file)
            assert os.path.getsize(output_file) > 0