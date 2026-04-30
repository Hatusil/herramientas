"""
Tests for processor.py - PDF processing functions.
"""
import os
import tempfile
import pytest

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image


def create_test_pdf(output_path, num_pages=1, with_metadata=True):
    """Create a test PDF with specified number of pages."""
    c = canvas.Canvas(output_path, pagesize=letter)
    
    if with_metadata:
        c.setTitle("Test Document")
        c.setAuthor("Test Author")
        c.setSubject("Test Subject")
        c.setCreator("Test Creator")
    
    for i in range(num_pages):
        c.drawString(100, 750, f"Test Page {i + 1}")
        c.drawString(100, 700, "This is a test PDF for unit testing.")
        c.showPage()
    
    c.save()


def create_test_image(output_path, size=(100, 100), color=(128, 128, 128)):
    """Create a test image for watermark tests."""
    img = Image.new('RGB', size, color)
    img.save(output_path)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for file operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_pdf(temp_dir):
    """Create a sample PDF for testing."""
    pdf_path = os.path.join(temp_dir, "sample.pdf")
    create_test_pdf(pdf_path, num_pages=3, with_metadata=True)
    return pdf_path


@pytest.fixture
def multi_page_pdf(temp_dir):
    """Create a multi-page PDF for testing."""
    pdf_path = os.path.join(temp_dir, "multipage.pdf")
    create_test_pdf(pdf_path, num_pages=5, with_metadata=True)
    return pdf_path


@pytest.fixture
def test_image(temp_dir):
    """Create a test image for watermark tests."""
    img_path = os.path.join(temp_dir, "test.png")
    create_test_image(img_path, size=(100, 100), color=(100, 100, 200))
    return img_path


class TestGetPdfInfo:
    """Tests for get_pdf_info function."""

    def test_get_pdf_info_success(self, sample_pdf):
        """Test successful PDF info extraction."""
        from processor import get_pdf_info
        
        result = get_pdf_info(sample_pdf)
        
        assert result['success'] is True
        assert result['num_pages'] == 3
        assert result['is_encrypted'] is False
        assert result['title'] == 'Test Document'
        assert result['author'] == 'Test Author'
        assert result['file_size'] > 0

    def test_get_pdf_info_nonexistent_file(self):
        """Test handling of non-existent file."""
        from processor import get_pdf_info
        
        result = get_pdf_info("/nonexistent/file.pdf")
        
        assert result['success'] is False
        assert 'error' in result

    def test_get_pdf_info_pages_info(self, sample_pdf):
        """Test that page info is included."""
        from processor import get_pdf_info
        
        result = get_pdf_info(sample_pdf)
        
        assert 'pages' in result
        assert len(result['pages']) == 3
        assert result['pages'][0]['page_num'] == 1


class TestCheckPdfEncrypted:
    """Tests for check_pdf_encrypted function."""

    def test_unencrypted_pdf(self, sample_pdf):
        """Test that unencrypted PDF returns False."""
        from processor import check_pdf_encrypted
        
        result = check_pdf_encrypted(sample_pdf)
        
        assert result is False

    def test_nonexistent_file(self):
        """Test handling of non-existent file."""
        from processor import check_pdf_encrypted
        
        result = check_pdf_encrypted("/nonexistent/file.pdf")
        
        assert result is False


class TestAddTextWatermark:
    """Tests for add_text_watermark function."""

    def test_add_text_watermark_success(self, sample_pdf):
        """Test successful text watermark addition."""
        from processor import add_text_watermark
        
        result = add_text_watermark([sample_pdf], "CONFIDENTIAL")
        
        assert result['success'] is True
        assert len(result['output_files']) == 1
        assert os.path.exists(result['output_files'][0])

    def test_add_text_watermark_custom_options(self, sample_pdf):
        """Test watermark with custom options."""
        from processor import add_text_watermark
        
        result = add_text_watermark(
            [sample_pdf], 
            "DRAFT",
            font_size=36,
            color="#FF0000",
            opacity=0.5,
            rotation=30
        )
        
        assert result['success'] is True
        assert len(result['output_files']) == 1

    def test_add_text_watermark_nonexistent_file(self):
        """Test handling of non-existent file."""
        from processor import add_text_watermark
        
        result = add_text_watermark(["/nonexistent/file.pdf"], "TEST")
        
        assert result['success'] is False
        assert 'error' in result


class TestAddImageWatermark:
    """Tests for add_image_watermark function."""

    def test_add_image_watermark_success(self, sample_pdf, test_image):
        """Test successful image watermark addition."""
        from processor import add_image_watermark
        
        result = add_image_watermark([sample_pdf], test_image)
        
        assert result['success'] is True
        assert len(result['output_files']) == 1
        assert os.path.exists(result['output_files'][0])

    def test_add_image_watermark_custom_options(self, sample_pdf, test_image):
        """Test image watermark with custom options."""
        from processor import add_image_watermark
        
        result = add_image_watermark(
            [sample_pdf], 
            test_image,
            scale=0.3,
            opacity=0.5
        )
        
        assert result['success'] is True

    def test_add_image_watermark_nonexistent_image(self, sample_pdf):
        """Test handling of non-existent image."""
        from processor import add_image_watermark
        
        result = add_image_watermark([sample_pdf], "/nonexistent/image.png")
        
        assert result['success'] is False
        assert 'error' in result


class TestRotatePages:
    """Tests for rotate_pages function."""

    def test_rotate_all_pages_90(self, sample_pdf):
        """Test rotating all pages by 90 degrees."""
        from processor import rotate_pages, get_pdf_info
        
        result = rotate_pages([sample_pdf], degrees=90)
        
        assert result['success'] is True
        assert len(result['output_files']) == 1
        
        output_file = result['output_files'][0]
        info = get_pdf_info(output_file)
        assert info['pages'][0]['rotation'] == 90

    def test_rotate_all_pages_180(self, sample_pdf):
        """Test rotating all pages by 180 degrees."""
        from processor import rotate_pages, get_pdf_info
        
        result = rotate_pages([sample_pdf], degrees=180)
        
        assert result['success'] is True
        output_file = result['output_files'][0]
        info = get_pdf_info(output_file)
        assert info['pages'][0]['rotation'] == 180

    def test_rotate_all_pages_270(self, sample_pdf):
        """Test rotating all pages by 270 degrees."""
        from processor import rotate_pages, get_pdf_info
        
        result = rotate_pages([sample_pdf], degrees=270)
        
        assert result['success'] is True
        output_file = result['output_files'][0]
        info = get_pdf_info(output_file)
        assert info['pages'][0]['rotation'] == 270

    def test_rotate_specific_pages(self, multi_page_pdf):
        """Test rotating specific pages."""
        from processor import rotate_pages, get_pdf_info
        
        result = rotate_pages([multi_page_pdf], degrees=90, pages=[1, 3])
        
        assert result['success'] is True
        output_file = result['output_files'][0]
        info = get_pdf_info(output_file)
        
        assert info['pages'][0]['rotation'] == 90
        assert info['pages'][1]['rotation'] == 0
        assert info['pages'][2]['rotation'] == 90

    def test_rotate_invalid_degrees(self, sample_pdf):
        """Test invalid rotation degrees."""
        from processor import rotate_pages
        
        result = rotate_pages([sample_pdf], degrees=45)
        
        assert result['success'] is False
        assert 'error' in result


class TestMergePdfs:
    """Tests for merge_pdfs function."""

    def test_merge_two_pdfs(self, temp_dir):
        """Test merging two PDFs."""
        from processor import merge_pdfs, get_pdf_info
        
        pdf1 = os.path.join(temp_dir, "pdf1.pdf")
        pdf2 = os.path.join(temp_dir, "pdf2.pdf")
        create_test_pdf(pdf1, num_pages=2)
        create_test_pdf(pdf2, num_pages=3)
        
        result = merge_pdfs([pdf1, pdf2])
        
        assert result['success'] is True
        output_file = result['output_files'][0]
        info = get_pdf_info(output_file)
        assert info['num_pages'] == 5

    def test_merge_single_pdf_fails(self, sample_pdf):
        """Test that merging single PDF fails."""
        from processor import merge_pdfs
        
        result = merge_pdfs([sample_pdf])
        
        assert result['success'] is False
        assert 'error' in result

    def test_merge_with_output_path(self, temp_dir):
        """Test merge with custom output path."""
        from processor import merge_pdfs
        
        pdf1 = os.path.join(temp_dir, "pdf1.pdf")
        pdf2 = os.path.join(temp_dir, "pdf2.pdf")
        create_test_pdf(pdf1, num_pages=1)
        create_test_pdf(pdf2, num_pages=1)
        output_path = os.path.join(temp_dir, "custom_output.pdf")
        
        result = merge_pdfs([pdf1, pdf2], output_path=output_path)
        
        assert result['success'] is True
        assert os.path.exists(output_path)


class TestExtractPages:
    """Tests for extract_pages function."""

    def test_extract_single_page(self, multi_page_pdf):
        """Test extracting a single page."""
        from processor import extract_pages, get_pdf_info
        
        result = extract_pages([multi_page_pdf], pages=[2])
        
        assert result['success'] is True
        output_file = result['output_files'][0]
        info = get_pdf_info(output_file)
        assert info['num_pages'] == 1

    def test_extract_multiple_pages(self, multi_page_pdf):
        """Test extracting multiple pages."""
        from processor import extract_pages, get_pdf_info
        
        result = extract_pages([multi_page_pdf], pages=[1, 3, 5])
        
        assert result['success'] is True
        output_file = result['output_files'][0]
        info = get_pdf_info(output_file)
        assert info['num_pages'] == 3

    def test_extract_pages_nonexistent(self):
        """Test extracting from non-existent file."""
        from processor import extract_pages
        
        result = extract_pages(["/nonexistent.pdf"], pages=[1])
        
        assert result['success'] is False


class TestAddPageNumbers:
    """Tests for add_page_numbers function."""

    def test_add_page_numbers_default(self, sample_pdf):
        """Test adding page numbers with default options."""
        from processor import add_page_numbers
        
        result = add_page_numbers([sample_pdf])
        
        assert result['success'] is True
        assert len(result['output_files']) == 1
        assert os.path.exists(result['output_files'][0])

    def test_add_page_numbers_custom_format(self, sample_pdf):
        """Test with custom format."""
        from processor import add_page_numbers
        
        result = add_page_numbers(
            [sample_pdf],
            format="Page {n}/{total}",
            position="footer",
            font_size=10,
            color="#000000"
        )
        
        assert result['success'] is True

    def test_add_page_numbers_header(self, sample_pdf):
        """Test adding page numbers in header."""
        from processor import add_page_numbers
        
        result = add_page_numbers([sample_pdf], position="header")
        
        assert result['success'] is True


class TestCompressPdf:
    """Tests for compress_pdf function."""

    def test_compress_pdf_default(self, sample_pdf):
        """Test PDF compression with default level."""
        from processor import compress_pdf
        
        result = compress_pdf([sample_pdf])
        
        assert result['success'] is True
        assert len(result['output_files']) == 1
        assert os.path.exists(result['output_files'][0])

    def test_compress_pdf_different_levels(self, sample_pdf):
        """Test compression with different levels."""
        from processor import compress_pdf
        
        for level in ['low', 'medium', 'high']:
            result = compress_pdf([sample_pdf], level=level)
            assert result['success'] is True


class TestCleanMetadata:
    """Tests for clean_metadata function."""

    def test_clean_metadata_success(self, sample_pdf):
        """Test successful metadata cleaning."""
        from processor import clean_metadata, get_pdf_info
        
        result = clean_metadata([sample_pdf])
        
        assert result['success'] is True
        assert len(result['output_files']) == 1
        
        output_file = result['output_files'][0]
        info = get_pdf_info(output_file)
        assert info['title'] == ''
        assert info['author'] == ''

    def test_clean_metadata_nonexistent_file(self):
        """Test handling of non-existent file."""
        from processor import clean_metadata
        
        result = clean_metadata(["/nonexistent/file.pdf"])
        
        assert result['success'] is False


class TestFullWorkflow:
    """Integration tests for complete workflows."""

    def test_complete_pdf_workflow(self, temp_dir):
        """Test complete PDF processing workflow."""
        from processor import (
            get_pdf_info,
            add_text_watermark,
            rotate_pages,
            add_page_numbers,
            clean_metadata
        )
        
        original_pdf = os.path.join(temp_dir, "original.pdf")
        create_test_pdf(original_pdf, num_pages=2, with_metadata=True)
        
        info = get_pdf_info(original_pdf)
        assert info['success'] is True
        assert info['num_pages'] == 2
        
        watermarked = add_text_watermark([original_pdf], "DRAFT")
        assert watermarked['success'] is True
        
        rotated = rotate_pages([watermarked['output_files'][0]], degrees=90)
        assert rotated['success'] is True
        
        numbered = add_page_numbers([rotated['output_files'][0]])
        assert numbered['success'] is True
        
        cleaned = clean_metadata([numbered['output_files'][0]])
        assert cleaned['success'] is True
        
        final_info = get_pdf_info(cleaned['output_files'][0])
        assert final_info['title'] == ''
        assert final_info['pages'][0]['rotation'] == 90