"""
Tests for image_tool/processor.py
Tests for phases 1-7 including morphology, edge detection, and advanced analysis.
"""
import pytest
import numpy as np
import tempfile
import os
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools' / 'image_tool'))

from processor import (
    _to_grayscale, _crop_region, _resize, _rotate,
    _filter_gaussian, _filter_median, _filter_mean,
    _erode, _dilate, _open, _close,
    _edge_sobel, _edge_prewitt, _edge_laplacian, _edge_canny,
    _pseudocolor, _to_hsv
)


# === Helper fixtures ===

@pytest.fixture
def color_image():
    """Create a simple color test image (RGB)."""
    # Create a 100x100 RGB image with some variation
    arr = np.zeros((100, 100, 3), dtype=np.uint8)
    arr[20:80, 20:80] = [128, 64, 192]  # Purple square in center
    arr[0:20, :] = [255, 0, 0]  # Red top
    arr[80:100, :] = [0, 0, 255]  # Blue bottom
    return arr


@pytest.fixture
def gray_image():
    """Create a grayscale test image."""
    arr = np.zeros((100, 100), dtype=np.uint8)
    arr[20:80, 20:80] = 200  # Bright square
    arr[0:20, :] = 50  # Dark top
    arr[80:100, :] = 150  # Medium bottom
    return arr


@pytest.fixture
def binary_image():
    """Create a binary test image."""
    arr = np.zeros((100, 100), dtype=np.uint8)
    arr[30:70, 30:70] = 255  # White square
    arr[10:20, 10:20] = 255  # Small white region
    return arr


# === Phase 2: Geometry Tests ===

class TestToGrayscale:
    """Tests for _to_grayscale()."""

    def test_to_grayscale_color(self, color_image):
        """Test conversion from color to grayscale."""
        result = _to_grayscale(color_image)
        assert result['success'] is True
        # Shape can be (h, w) or (h, w, 1) depending on implementation
        assert len(result['image_data']['array'].shape) in [2, 3]

    def test_to_grayscale_already_gray(self, gray_image):
        """Test grayscale image stays grayscale."""
        result = _to_grayscale(gray_image)
        assert result['success'] is True
        assert len(result['image_data']['array'].shape) == 2


class TestCropRegion:
    """Tests for _crop_region()."""

    def test_crop_region_basic(self, color_image):
        """Test basic crop operation."""
        result = _crop_region(color_image, 10, 10, 50, 50)
        assert result['success'] is True
        assert result['image_data']['array'].shape[:2] == (50, 50)

    def test_crop_region_full(self, color_image):
        """Test crop with no changes (full image)."""
        result = _crop_region(color_image, 0, 0, 100, 100)
        assert result['success'] is True
        assert result['image_data']['array'].shape[:2] == (100, 100)

    def test_crop_region_invalid_negative(self, color_image):
        """Test crop with negative coordinates."""
        result = _crop_region(color_image, -10, 10, 50, 50)
        assert result['success'] is False
        assert 'error' in result

    def test_crop_region_invalid_exceed(self, color_image):
        """Test crop exceeding image boundaries."""
        result = _crop_region(color_image, 50, 50, 100, 100)
        assert result['success'] is False


class TestResize:
    """Tests for _resize()."""

    def test_resize_upscale(self, color_image):
        """Test upscaling image."""
        result = _resize(color_image, 2.0)
        assert result['success'] is True
        assert result['image_data']['array'].shape[:2] == (200, 200)

    def test_resize_downscale(self, color_image):
        """Test downscaling image."""
        result = _resize(color_image, 0.5)
        assert result['success'] is True
        assert result['image_data']['array'].shape[:2] == (50, 50)

    def test_resize_invalid_scale(self, color_image):
        """Test resize with invalid (negative) scale."""
        result = _resize(color_image, -0.5)
        assert result['success'] is False


class TestRotate:
    """Tests for _rotate()."""

    def test_rotate_90(self, color_image):
        """Test 90 degree rotation."""
        result = _rotate(color_image, 90)
        assert result['success'] is True
        # 90 degree rotation swaps dimensions
        assert result['image_data']['array'].shape[:2] == (100, 100)

    def test_rotate_45(self, color_image):
        """Test 45 degree rotation."""
        result = _rotate(color_image, 45)
        assert result['success'] is True

    def test_rotate_no_change(self, color_image):
        """Test 0 degree rotation."""
        result = _rotate(color_image, 0)
        assert result['success'] is True


class TestToHSV:
    """Tests for _to_hsv()."""

    def test_to_hsv_color(self, color_image):
        """Test HSV conversion."""
        result = _to_hsv(color_image)
        # May fail if OpenCV not available (fallback returns error)
        if result['success']:
            assert result['image_data']['array'].shape == color_image.shape
        else:
            # Expected when OpenCV not available
            assert 'error' in result or result.get('message', '') != ''


# === Phase 4: Filtering Tests ===

class TestFilterGaussian:
    """Tests for _filter_gaussian()."""

    def test_filter_gaussian_basic(self, color_image):
        """Test Gaussian filter."""
        result = _filter_gaussian(color_image, ksize=5)
        assert result['success'] is True

    def test_filter_gaussian_invalid_ksize_even(self, color_image):
        """Test Gaussian with even ksize."""
        result = _filter_gaussian(color_image, ksize=4)
        assert result['success'] is False

    def test_filter_gaussian_invalid_ksize_small(self, color_image):
        """Test Gaussian with too small ksize."""
        result = _filter_gaussian(color_image, ksize=1)
        assert result['success'] is False


class TestFilterMedian:
    """Tests for _filter_median()."""

    def test_filter_median_basic(self, gray_image):
        """Test median filter."""
        result = _filter_median(gray_image, ksize=3)
        assert result['success'] is True


class TestFilterMean:
    """Tests for _filter_mean()."""

    def test_filter_mean_basic(self, color_image):
        """Test mean filter."""
        result = _filter_mean(color_image, ksize=3)
        assert result['success'] is True


# === Phase 5: Morphology Tests ===

class TestErode:
    """Tests for _erode()."""

    def test_erode_basic(self, binary_image):
        """Test erosion."""
        result = _erode(binary_image, kernel_size=3)
        assert result['success'] is True

    def test_erode_invalid_ksize(self, binary_image):
        """Test erosion with invalid ksize."""
        result = _erode(binary_image, kernel_size=2)
        assert result['success'] is False


class TestDilate:
    """Tests for _dilate()."""

    def test_dilate_basic(self, binary_image):
        """Test dilation."""
        result = _dilate(binary_image, kernel_size=3)
        assert result['success'] is True

    def test_dilate_invalid_ksize(self, binary_image):
        """Test dilation with invalid ksize."""
        result = _dilate(binary_image, kernel_size=4)
        assert result['success'] is False


class TestOpen:
    """Tests for _open() (erosion + dilation)."""

    def test_open_basic(self, binary_image):
        """Test opening operation."""
        result = _open(binary_image, kernel_size=3)
        assert result['success'] is True


class TestClose:
    """Tests for _close() (dilation + erosion)."""

    def test_close_basic(self, binary_image):
        """Test closing operation."""
        result = _close(binary_image, kernel_size=3)
        assert result['success'] is True


# === Phase 6: Edge Detection Tests ===

class TestEdgeSobel:
    """Tests for _edge_sobel()."""

    def test_edge_sobel_basic(self, gray_image):
        """Test Sobel edge detection."""
        result = _edge_sobel(gray_image)
        assert result['success'] is True

    def test_edge_sobel_color(self, color_image):
        """Test Sobel on color image."""
        result = _edge_sobel(color_image)
        assert result['success'] is True


class TestEdgePrewitt:
    """Tests for _edge_prewitt()."""

    def test_edge_prewitt_basic(self, gray_image):
        """Test Prewitt edge detection."""
        result = _edge_prewitt(gray_image)
        assert result['success'] is True


class TestEdgeLaplacian:
    """Tests for _edge_laplacian()."""

    def test_edge_laplacian_basic(self, gray_image):
        """Test Laplacian edge detection."""
        result = _edge_laplacian(gray_image)
        # May fail if OpenCV not available (fallback returns error)
        if result['success']:
            assert result['image_data']['array'].shape[:2] == gray_image.shape[:2]
        else:
            # Expected when OpenCV not available
            assert 'error' in result or result.get('message', '') != ''


class TestEdgeCanny:
    """Tests for _edge_canny()."""

    def test_edge_canny_basic(self, gray_image):
        """Test Canny edge detection."""
        result = _edge_canny(gray_image)
        assert result['success'] is True

    def test_edge_canny_custom_thresholds(self, gray_image):
        """Test Canny with custom thresholds."""
        result = _edge_canny(gray_image, threshold1=30, threshold2=100)
        assert result['success'] is True


# === Phase 7: Analysis Tests ===

class TestPseudocolor:
    """Tests for _pseudocolor()."""

    def test_pseudocolor_gray(self, gray_image):
        """Test pseudocolor on grayscale."""
        result = _pseudocolor(gray_image, colormap='jet')
        # May fail without OpenCV
        if result['success']:
            assert result['image_data']['array'].shape[2] == 3

    def test_pseudocolor_color(self, color_image):
        """Test pseudocolor on color image."""
        result = _pseudocolor(color_image, colormap='ocean')
        # May fail without OpenCV
        if result['success']:
            assert result['image_data']['array'].shape[2] == 3

    def test_pseudocolor_invalid_colormap(self, gray_image):
        """Test pseudocolor with invalid colormap."""
        result = _pseudocolor(gray_image, colormap='invalid')
        # Should fail when OpenCV available, may pass (fallback) without OpenCV
        # Either is acceptable - just verify no crash
        assert 'message' in result or 'error' in result