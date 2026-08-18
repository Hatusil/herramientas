"""
Comprehensive tests for image_tool processor functions.

Covers helpers (_ok, _fail, _image_to_dict), geometria, mejora, filtros,
morfologia, and bordes modules. All functions are pure: np.ndarray in → Dict out.
"""
import pytest
import numpy as np

from tools.image_tool.processors._ok import CV2_AVAILABLE, _ok, _fail, _image_to_dict

skip_no_cv2 = pytest.mark.skipif(not CV2_AVAILABLE, reason="cv2 not installed")

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def rgb_image():
    """100x100 RGB image with gradient."""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:, :, 0] = np.linspace(0, 255, 100, dtype=np.uint8)  # R gradient
    img[:, :, 1] = 128  # constant G
    img[:, :, 2] = 200  # constant B
    return img


@pytest.fixture
def gray_image():
    """100x100 grayscale image."""
    img = np.zeros((100, 100), dtype=np.uint8)
    img[30:70, 30:70] = 255  # white square in center
    return img


@pytest.fixture
def small_rgb():
    """Small 10x10 RGB image for fast edge-case tests."""
    return np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)


@pytest.fixture
def binary_image():
    """Binary (0/255) 100x100 image for contour tests."""
    img = np.zeros((100, 100), dtype=np.uint8)
    img[20:80, 20:80] = 255
    return img


# ===========================================================================
# Helpers: _ok, _fail, _image_to_dict
# ===========================================================================

class TestHelpers:
    """Tests for _ok, _fail, and _image_to_dict helpers."""

    def test_ok_returns_success_true(self):
        result = _ok(np.zeros((10, 10), dtype=np.uint8), "done")
        assert result["success"] is True

    def test_ok_contains_message(self):
        result = _ok(np.zeros((10, 10), dtype=np.uint8), "hello")
        assert result["message"] == "hello"

    def test_ok_has_empty_output_files(self):
        result = _ok(np.zeros((10, 10), dtype=np.uint8), "msg")
        assert result["output_files"] == []

    def test_ok_has_image_data(self):
        img = np.zeros((10, 10), dtype=np.uint8)
        result = _ok(img, "msg")
        assert result["image_data"] is not None
        assert result["image_data"]["array"] is img

    def test_ok_error_is_none(self):
        result = _ok(np.zeros((10, 10), dtype=np.uint8), "msg")
        assert result["error"] is None

    def test_fail_returns_success_false(self):
        result = _fail("something broke")
        assert result["success"] is False

    def test_fail_has_error_message(self):
        result = _fail("bad input")
        assert result["error"] == "bad input"

    def test_fail_has_empty_message(self):
        result = _fail("err")
        assert result["message"] == ""

    def test_fail_image_data_is_none(self):
        result = _fail("err")
        assert result["image_data"] is None

    def test_fail_output_files_is_empty(self):
        result = _fail("err")
        assert result["output_files"] == []

    def test_image_to_dict_rgb(self):
        img = np.zeros((50, 60, 3), dtype=np.uint8)
        d = _image_to_dict(img)
        assert d["shape"] == (50, 60, 3)
        assert d["dtype"] == "uint8"
        assert d["format"] == "png"
        assert d["mode"] == "RGB"

    def test_image_to_dict_grayscale(self):
        img = np.zeros((40, 40), dtype=np.uint8)
        d = _image_to_dict(img)
        assert d["shape"] == (40, 40)
        assert d["mode"] == "L"

    def test_image_to_dict_preserves_array_ref(self):
        img = np.ones((5, 5), dtype=np.uint8)
        d = _image_to_dict(img)
        assert d["array"] is img


# ===========================================================================
# Geometría
# ===========================================================================

class TestGrayscale:
    """Tests for _to_grayscale."""

    def test_rgb_to_grayscale(self):
        from tools.image_tool.processors.geometria import _to_grayscale
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        result = _to_grayscale(img)
        assert result["success"] is True
        assert len(result["image_data"]["shape"]) == 2

    def test_already_grayscale_passthrough(self):
        from tools.image_tool.processors.geometria import _to_grayscale
        img = np.ones((30, 30), dtype=np.uint8) * 128
        result = _to_grayscale(img)
        assert result["success"] is True
        assert result["image_data"]["shape"] == (30, 30)

    def test_grayscale_output_is_uint8(self):
        from tools.image_tool.processors.geometria import _to_grayscale
        img = np.ones((20, 20, 3), dtype=np.uint8) * 100
        result = _to_grayscale(img)
        assert result["image_data"]["array"].dtype == np.uint8


class TestHSV:
    """Tests for _to_hsv."""

    @skip_no_cv2
    def test_rgb_to_hsv(self):
        from tools.image_tool.processors.geometria import _to_hsv
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        result = _to_hsv(img)
        assert result["success"] is True
        assert result["image_data"]["shape"] == (50, 50, 3)

    @skip_no_cv2
    def test_grayscale_to_hsv(self):
        from tools.image_tool.processors.geometria import _to_hsv
        img = np.ones((30, 30), dtype=np.uint8) * 128
        result = _to_hsv(img)
        assert result["success"] is True
        # grayscale → RGB → HSV, so output is 3-channel
        assert len(result["image_data"]["shape"]) == 3


class TestCrop:
    """Tests for _crop_region."""

    def test_valid_crop(self):
        from tools.image_tool.processors.geometria import _crop_region
        img = np.ones((100, 100, 3), dtype=np.uint8) * 50
        result = _crop_region(img, 10, 20, 30, 40)
        assert result["success"] is True
        h, w = result["image_data"]["shape"][:2]
        assert h == 40
        assert w == 30

    def test_crop_preserves_pixel_values(self):
        from tools.image_tool.processors.geometria import _crop_region
        img = np.zeros((100, 100), dtype=np.uint8)
        img[5:15, 10:20] = 255
        result = _crop_region(img, 10, 5, 10, 10)
        assert result["success"] is True
        assert np.all(result["image_data"]["array"] == 255)

    def test_crop_negative_coords_fails(self):
        from tools.image_tool.processors.geometria import _crop_region
        img = np.ones((100, 100), dtype=np.uint8)
        result = _crop_region(img, -5, 10, 20, 20)
        assert result["success"] is False
        assert "positive" in result["error"].lower()

    def test_crop_zero_width_fails(self):
        from tools.image_tool.processors.geometria import _crop_region
        img = np.ones((100, 100), dtype=np.uint8)
        result = _crop_region(img, 0, 0, 0, 10)
        assert result["success"] is False

    def test_crop_exceeds_boundary_fails(self):
        from tools.image_tool.processors.geometria import _crop_region
        img = np.ones((100, 100), dtype=np.uint8)
        result = _crop_region(img, 80, 80, 30, 30)
        assert result["success"] is False
        assert "boundaries" in result["error"].lower()


class TestResize:
    """Tests for _resize."""

    def test_resize_upscale(self):
        from tools.image_tool.processors.geometria import _resize
        img = np.ones((50, 50, 3), dtype=np.uint8)
        result = _resize(img, 2.0)
        assert result["success"] is True
        h, w = result["image_data"]["shape"][:2]
        assert h == 100
        assert w == 100

    def test_resize_downscale(self):
        from tools.image_tool.processors.geometria import _resize
        img = np.ones((100, 100, 3), dtype=np.uint8)
        result = _resize(img, 0.5)
        assert result["success"] is True
        h, w = result["image_data"]["shape"][:2]
        assert h == 50
        assert w == 50

    def test_resize_identity(self):
        from tools.image_tool.processors.geometria import _resize
        img = np.ones((80, 60, 3), dtype=np.uint8)
        result = _resize(img, 1.0)
        assert result["success"] is True
        h, w = result["image_data"]["shape"][:2]
        assert h == 80
        assert w == 60

    def test_resize_zero_scale_fails(self):
        from tools.image_tool.processors.geometria import _resize
        img = np.ones((50, 50), dtype=np.uint8)
        result = _resize(img, 0.0)
        assert result["success"] is False
        assert "positive" in result["error"].lower()

    def test_resize_negative_scale_fails(self):
        from tools.image_tool.processors.geometria import _resize
        img = np.ones((50, 50), dtype=np.uint8)
        result = _resize(img, -1.0)
        assert result["success"] is False


class TestTranslate:
    """Tests for _translate."""

    def test_translate_zero(self):
        from tools.image_tool.processors.geometria import _translate
        img = np.ones((50, 50), dtype=np.uint8) * 100
        result = _translate(img, 0, 0)
        assert result["success"] is True
        assert result["image_data"]["shape"] == (50, 50)

    def test_translate_positive(self):
        from tools.image_tool.processors.geometria import _translate
        img = np.zeros((50, 50), dtype=np.uint8)
        img[0:10, 0:10] = 255
        result = _translate(img, 10, 10)
        assert result["success"] is True
        assert result["image_data"]["shape"] == (50, 50)

    def test_translate_negative(self):
        from tools.image_tool.processors.geometria import _translate
        img = np.zeros((50, 50), dtype=np.uint8)
        result = _translate(img, -20, -20)
        assert result["success"] is True

    def test_translate_preserves_shape(self):
        from tools.image_tool.processors.geometria import _translate
        img = np.ones((60, 80, 3), dtype=np.uint8)
        result = _translate(img, 5, 5)
        assert result["success"] is True
        assert result["image_data"]["shape"] == (60, 80, 3)


class TestRotate:
    """Tests for _rotate."""

    def test_rotate_zero_degrees(self):
        from tools.image_tool.processors.geometria import _rotate
        img = np.ones((50, 50, 3), dtype=np.uint8)
        result = _rotate(img, 0.0)
        assert result["success"] is True
        assert result["image_data"]["shape"] == (50, 50, 3)

    def test_rotate_90(self):
        from tools.image_tool.processors.geometria import _rotate
        img = np.ones((50, 50, 3), dtype=np.uint8)
        result = _rotate(img, 90.0)
        assert result["success"] is True

    def test_rotate_negative_angle(self):
        from tools.image_tool.processors.geometria import _rotate
        img = np.ones((50, 50, 3), dtype=np.uint8)
        result = _rotate(img, -45.0)
        assert result["success"] is True

    def test_rotate_preserves_dimensions(self):
        from tools.image_tool.processors.geometria import _rotate
        img = np.ones((60, 80, 3), dtype=np.uint8)
        result = _rotate(img, 30.0)
        assert result["success"] is True
        # cv2 warpAffine with same output size
        assert result["image_data"]["shape"][:2] == (60, 80)


# ===========================================================================
# Mejora (Enhancement)
# ===========================================================================

class TestHistogram:
    """Tests for _compute_histogram."""

    def test_histogram_rgb(self):
        from tools.image_tool.processors.mejora import _compute_histogram
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        result = _compute_histogram(img)
        assert result["success"] is True
        assert len(result["output_files"]) == 1
        assert result["output_files"][0].endswith(".png")

    def test_histogram_grayscale(self):
        from tools.image_tool.processors.mejora import _compute_histogram
        img = np.random.randint(0, 256, (50, 50), dtype=np.uint8)
        result = _compute_histogram(img)
        assert result["success"] is True

    def test_histogram_constant_image(self):
        from tools.image_tool.processors.mejora import _compute_histogram
        img = np.full((40, 40, 3), 128, dtype=np.uint8)
        result = _compute_histogram(img)
        assert result["success"] is True


class TestEqualizeHistogram:
    """Tests for _equalize_histogram."""

    def test_equalize_rgb(self):
        from tools.image_tool.processors.mejora import _equalize_histogram
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        result = _equalize_histogram(img)
        assert result["success"] is True
        # RGB input → 3-channel output
        assert len(result["image_data"]["shape"]) == 3

    def test_equalize_grayscale(self):
        from tools.image_tool.processors.mejora import _equalize_histogram
        img = np.random.randint(0, 256, (50, 50), dtype=np.uint8)
        result = _equalize_histogram(img)
        assert result["success"] is True
        assert len(result["image_data"]["shape"]) == 2

    def test_equalize_preserves_shape(self):
        from tools.image_tool.processors.mejora import _equalize_histogram
        img = np.random.randint(0, 256, (60, 80, 3), dtype=np.uint8)
        result = _equalize_histogram(img)
        assert result["success"] is True
        assert result["image_data"]["shape"] == (60, 80, 3)

    def test_equalize_output_is_uint8(self):
        from tools.image_tool.processors.mejora import _equalize_histogram
        img = np.random.randint(0, 256, (30, 30), dtype=np.uint8)
        result = _equalize_histogram(img)
        assert result["image_data"]["array"].dtype == np.uint8


class TestBrightnessContrast:
    """Tests for _adjust_brightness_contrast."""

    def test_no_adjustment(self):
        from tools.image_tool.processors.mejora import _adjust_brightness_contrast
        img = np.full((10, 10), 128, dtype=np.uint8)
        result = _adjust_brightness_contrast(img, brightness=0.0, contrast=1.0)
        assert result["success"] is True
        assert np.all(result["image_data"]["array"] == 128)

    def test_increase_brightness(self):
        from tools.image_tool.processors.mejora import _adjust_brightness_contrast
        img = np.zeros((10, 10), dtype=np.uint8)
        result = _adjust_brightness_contrast(img, brightness=1.0, contrast=1.0)
        assert result["success"] is True
        # brightness=1.0 → 1.0*255 = 255
        assert np.all(result["image_data"]["array"] == 255)

    def test_decrease_brightness(self):
        from tools.image_tool.processors.mejora import _adjust_brightness_contrast
        img = np.full((10, 10), 128, dtype=np.uint8)
        result = _adjust_brightness_contrast(img, brightness=-0.5, contrast=1.0)
        assert result["success"] is True
        # 128 * 1.0 + (-0.5) * 255 = 128 - 127.5 = 0.5 → clipped to 0 or 1
        arr = result["image_data"]["array"]
        assert arr.max() <= 1

    def test_increase_contrast(self):
        from tools.image_tool.processors.mejora import _adjust_brightness_contrast
        img = np.full((10, 10), 128, dtype=np.uint8)
        result = _adjust_brightness_contrast(img, brightness=0.0, contrast=2.0)
        assert result["success"] is True
        # 128 * 2.0 = 256 → clipped to 255
        assert np.all(result["image_data"]["array"] == 255)

    def test_output_is_clipped_to_uint8(self):
        from tools.image_tool.processors.mejora import _adjust_brightness_contrast
        img = np.full((10, 10), 200, dtype=np.uint8)
        result = _adjust_brightness_contrast(img, brightness=1.0, contrast=1.0)
        assert result["success"] is True
        assert result["image_data"]["array"].dtype == np.uint8
        assert result["image_data"]["array"].max() <= 255

    def test_default_params_noop(self):
        from tools.image_tool.processors.mejora import _adjust_brightness_contrast
        img = np.random.randint(0, 256, (20, 20), dtype=np.uint8)
        result = _adjust_brightness_contrast(img)
        assert result["success"] is True
        assert np.array_equal(result["image_data"]["array"], img)


class TestGamma:
    """Tests for _adjust_gamma."""

    def test_gamma_1_no_change(self):
        from tools.image_tool.processors.mejora import _adjust_gamma
        img = np.full((10, 10), 128, dtype=np.uint8)
        result = _adjust_gamma(img, 1.0)
        assert result["success"] is True
        # power(128/255, 1/1) * 255 ≈ 128
        arr = result["image_data"]["array"]
        assert abs(int(arr.mean()) - 128) <= 1

    def test_gamma_less_than_1_darkens(self):
        # power(x, 1/0.5) = power(x, 2) → darkens mid-tones
        from tools.image_tool.processors.mejora import _adjust_gamma
        img = np.full((10, 10), 100, dtype=np.uint8)
        result = _adjust_gamma(img, 0.5)
        assert result["success"] is True
        assert result["image_data"]["array"].mean() < 100

    def test_gamma_greater_than_1_brightens(self):
        # power(x, 1/2) = sqrt(x) → brightens mid-tones
        from tools.image_tool.processors.mejora import _adjust_gamma
        img = np.full((10, 10), 200, dtype=np.uint8)
        result = _adjust_gamma(img, 2.0)
        assert result["success"] is True
        assert result["image_data"]["array"].mean() > 200

    def test_gamma_zero_fails(self):
        from tools.image_tool.processors.mejora import _adjust_gamma
        img = np.ones((10, 10), dtype=np.uint8)
        result = _adjust_gamma(img, 0.0)
        assert result["success"] is False
        assert "positive" in result["error"].lower()

    def test_gamma_negative_fails(self):
        from tools.image_tool.processors.mejora import _adjust_gamma
        img = np.ones((10, 10), dtype=np.uint8)
        result = _adjust_gamma(img, -1.0)
        assert result["success"] is False

    def test_gamma_output_is_uint8(self):
        from tools.image_tool.processors.mejora import _adjust_gamma
        img = np.random.randint(0, 256, (20, 20), dtype=np.uint8)
        result = _adjust_gamma(img, 1.5)
        assert result["image_data"]["array"].dtype == np.uint8


# ===========================================================================
# Filtros (Filters)
# ===========================================================================

class TestGaussianFilter:
    """Tests for _filter_gaussian."""

    def test_gaussian_default(self):
        from tools.image_tool.processors.filtros import _filter_gaussian
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        result = _filter_gaussian(img)
        assert result["success"] is True
        assert result["image_data"]["shape"] == (50, 50, 3)

    def test_gaussian_ksize_3(self):
        from tools.image_tool.processors.filtros import _filter_gaussian
        img = np.random.randint(0, 256, (30, 30), dtype=np.uint8)
        result = _filter_gaussian(img, ksize=3)
        assert result["success"] is True

    def test_gaussian_ksize_7(self):
        from tools.image_tool.processors.filtros import _filter_gaussian
        img = np.random.randint(0, 256, (40, 40, 3), dtype=np.uint8)
        result = _filter_gaussian(img, ksize=7)
        assert result["success"] is True

    def test_gaussian_even_ksize_fails(self):
        from tools.image_tool.processors.filtros import _filter_gaussian
        img = np.ones((20, 20), dtype=np.uint8)
        result = _filter_gaussian(img, ksize=4)
        assert result["success"] is False
        assert "odd" in result["error"].lower()

    def test_gaussian_ksize_1_fails(self):
        from tools.image_tool.processors.filtros import _filter_gaussian
        img = np.ones((20, 20), dtype=np.uint8)
        result = _filter_gaussian(img, ksize=1)
        assert result["success"] is False
        assert ">=" in result["error"]

    def test_gaussian_smoothing_effect(self):
        from tools.image_tool.processors.filtros import _filter_gaussian
        img = np.zeros((50, 50), dtype=np.uint8)
        img[20:30, 20:30] = 255  # sharp square
        result = _filter_gaussian(img, ksize=15)
        assert result["success"] is True
        # The center should still be bright but edges softened
        center_val = result["image_data"]["array"][25, 25]
        assert center_val > 0


class TestMedianFilter:
    """Tests for _filter_median."""

    def test_median_default(self):
        from tools.image_tool.processors.filtros import _filter_median
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        result = _filter_median(img)
        assert result["success"] is True
        assert result["image_data"]["shape"] == (50, 50, 3)

    def test_median_ksize_5(self):
        from tools.image_tool.processors.filtros import _filter_median
        img = np.random.randint(0, 256, (40, 40), dtype=np.uint8)
        result = _filter_median(img, ksize=5)
        assert result["success"] is True

    def test_median_even_ksize_fails(self):
        from tools.image_tool.processors.filtros import _filter_median
        img = np.ones((20, 20), dtype=np.uint8)
        result = _filter_median(img, ksize=4)
        assert result["success"] is False
        assert "odd" in result["error"].lower()


class TestMeanFilter:
    """Tests for _filter_mean."""

    def test_mean_default(self):
        from tools.image_tool.processors.filtros import _filter_mean
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        result = _filter_mean(img)
        assert result["success"] is True
        assert result["image_data"]["shape"] == (50, 50, 3)

    def test_mean_even_ksize_fails(self):
        from tools.image_tool.processors.filtros import _filter_mean
        img = np.ones((20, 20), dtype=np.uint8)
        result = _filter_mean(img, ksize=6)
        assert result["success"] is False
        assert "odd" in result["error"].lower()

    def test_mean_blur_effect(self):
        from tools.image_tool.processors.filtros import _filter_mean
        img = np.zeros((50, 50), dtype=np.uint8)
        img[25, 25] = 255  # single bright pixel
        result = _filter_mean(img, ksize=5)
        assert result["success"] is True
        # Mean filter spreads the single pixel
        center_val = result["image_data"]["array"][25, 25]
        assert 0 < center_val < 255


class TestDeconvolve:
    """Tests for _deconvolve."""

    @skip_no_cv2
    def test_deconvolve_gaussian_kernel(self):
        from tools.image_tool.processors.filtros import _deconvolve
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        result = _deconvolve(img, kernel_type="gaussian")
        assert result["success"] is True

    @skip_no_cv2
    def test_deconvolve_motion_kernel(self):
        from tools.image_tool.processors.filtros import _deconvolve
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        result = _deconvolve(img, kernel_type="motion")
        assert result["success"] is True

    @skip_no_cv2
    def test_deconvolve_disk_kernel(self):
        from tools.image_tool.processors.filtros import _deconvolve
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        result = _deconvolve(img, kernel_type="disk")
        assert result["success"] is True

    @skip_no_cv2
    def test_deconvolve_unknown_kernel_fails(self):
        from tools.image_tool.processors.filtros import _deconvolve
        img = np.ones((30, 30), dtype=np.uint8)
        result = _deconvolve(img, kernel_type="invalid")
        assert result["success"] is False
        assert "Unknown kernel_type" in result["error"]


# ===========================================================================
# Morfología (Morphology)
# ===========================================================================

class TestErode:
    """Tests for _erode."""

    def test_erode_default(self):
        from tools.image_tool.processors.morfologia import _erode
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        result = _erode(img)
        assert result["success"] is True
        assert result["image_data"]["shape"] == (50, 50, 3)

    def test_erode_grayscale(self):
        from tools.image_tool.processors.morfologia import _erode
        img = np.ones((50, 50), dtype=np.uint8) * 128
        result = _erode(img, kernel_size=5)
        assert result["success"] is True

    def test_erode_shrinks_white_regions(self):
        from tools.image_tool.processors.morfologia import _erode
        img = np.zeros((50, 50), dtype=np.uint8)
        img[15:35, 15:35] = 255  # 20x20 white square
        result = _erode(img, kernel_size=5)
        assert result["success"] is True
        # After erosion, white area should shrink
        assert result["image_data"]["array"].sum() < img.sum()

    def test_erode_even_kernel_fails(self):
        from tools.image_tool.processors.morfologia import _erode
        img = np.ones((20, 20), dtype=np.uint8)
        result = _erode(img, kernel_size=4)
        assert result["success"] is False
        assert "odd" in result["error"].lower()

    def test_erode_small_kernel_fails(self):
        from tools.image_tool.processors.morfologia import _erode
        img = np.ones((20, 20), dtype=np.uint8)
        result = _erode(img, kernel_size=1)
        assert result["success"] is False
        assert ">=" in result["error"]


class TestDilate:
    """Tests for _dilate."""

    def test_dilate_default(self):
        from tools.image_tool.processors.morfologia import _dilate
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        result = _dilate(img)
        assert result["success"] is True

    def test_dilate_grows_white_regions(self):
        from tools.image_tool.processors.morfologia import _dilate
        img = np.zeros((50, 50), dtype=np.uint8)
        img[20:30, 20:30] = 255  # 10x10 white square
        result = _dilate(img, kernel_size=5)
        assert result["success"] is True
        # After dilation, white area should grow
        assert result["image_data"]["array"].sum() > img.sum()

    def test_dilate_even_kernel_fails(self):
        from tools.image_tool.processors.morfologia import _dilate
        img = np.ones((20, 20), dtype=np.uint8)
        result = _dilate(img, kernel_size=2)
        assert result["success"] is False


class TestMorphOpen:
    """Tests for _open (erode → dilate)."""

    def test_open_default(self):
        from tools.image_tool.processors.morfologia import _open
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        result = _open(img)
        assert result["success"] is True

    def test_open_removes_small_noise(self):
        from tools.image_tool.processors.morfologia import _open
        img = np.zeros((50, 50), dtype=np.uint8)
        img[15:35, 15:35] = 255  # large white square
        # Add small noise dots
        img[5, 5] = 255
        img[45, 45] = 255
        result = _open(img, kernel_size=5)
        assert result["success"] is True
        # Noise should be removed
        arr = result["image_data"]["array"]
        assert arr[5, 5] == 0
        assert arr[45, 45] == 0

    def test_open_even_kernel_fails(self):
        from tools.image_tool.processors.morfologia import _open
        img = np.ones((20, 20), dtype=np.uint8)
        result = _open(img, kernel_size=4)
        assert result["success"] is False


class TestMorphClose:
    """Tests for _close (dilate → erode)."""

    def test_close_default(self):
        from tools.image_tool.processors.morfologia import _close
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        result = _close(img)
        assert result["success"] is True

    def test_close_fills_small_holes(self):
        from tools.image_tool.processors.morfologia import _close
        img = np.ones((50, 50), dtype=np.uint8) * 255
        # Small black hole in the middle
        img[24:26, 24:26] = 0
        result = _close(img, kernel_size=5)
        assert result["success"] is True
        # Hole should be filled
        assert result["image_data"]["array"][25, 25] == 255

    def test_close_even_kernel_fails(self):
        from tools.image_tool.processors.morfologia import _close
        img = np.ones((20, 20), dtype=np.uint8)
        result = _close(img, kernel_size=6)
        assert result["success"] is False


# ===========================================================================
# Bordes (Edge Detection)
# ===========================================================================

class TestEdgeSobel:
    """Tests for _edge_sobel."""

    def test_sobel_rgb(self):
        from tools.image_tool.processors.bordes import _edge_sobel
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        result = _edge_sobel(img)
        assert result["success"] is True
        assert result["image_data"]["shape"] == (50, 50)

    def test_sobel_grayscale(self):
        from tools.image_tool.processors.bordes import _edge_sobel
        img = np.random.randint(0, 256, (50, 50), dtype=np.uint8)
        result = _edge_sobel(img)
        assert result["success"] is True

    def test_sobel_flat_image_low_edges(self):
        from tools.image_tool.processors.bordes import _edge_sobel
        img = np.ones((50, 50), dtype=np.uint8) * 128
        result = _edge_sobel(img)
        assert result["success"] is True
        # Flat image → minimal edge response
        assert result["image_data"]["array"].sum() == 0

    def test_sobel_output_is_uint8(self):
        from tools.image_tool.processors.bordes import _edge_sobel
        img = np.random.randint(0, 256, (30, 30, 3), dtype=np.uint8)
        result = _edge_sobel(img)
        assert result["image_data"]["array"].dtype == np.uint8


class TestEdgePrewitt:
    """Tests for _edge_prewitt."""

    def test_prewitt_rgb(self):
        from tools.image_tool.processors.bordes import _edge_prewitt
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        result = _edge_prewitt(img)
        assert result["success"] is True
        assert result["image_data"]["shape"] == (50, 50)

    def test_prewitt_grayscale(self):
        from tools.image_tool.processors.bordes import _edge_prewitt
        img = np.random.randint(0, 256, (50, 50), dtype=np.uint8)
        result = _edge_prewitt(img)
        assert result["success"] is True

    def test_prewitt_flat_image(self):
        from tools.image_tool.processors.bordes import _edge_prewitt
        img = np.full((40, 40), 200, dtype=np.uint8)
        result = _edge_prewitt(img)
        assert result["success"] is True
        assert result["image_data"]["array"].sum() == 0


class TestEdgeLaplacian:
    """Tests for _edge_laplacian."""

    def test_laplacian_rgb(self):
        from tools.image_tool.processors.bordes import _edge_laplacian
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        result = _edge_laplacian(img)
        assert result["success"] is True
        assert result["image_data"]["shape"] == (50, 50)

    def test_laplacian_grayscale(self):
        from tools.image_tool.processors.bordes import _edge_laplacian
        img = np.random.randint(0, 256, (50, 50), dtype=np.uint8)
        result = _edge_laplacian(img)
        assert result["success"] is True

    def test_laplacian_flat_image(self):
        from tools.image_tool.processors.bordes import _edge_laplacian
        img = np.full((30, 30), 100, dtype=np.uint8)
        result = _edge_laplacian(img)
        assert result["success"] is True
        assert result["image_data"]["array"].sum() == 0


class TestEdgeCanny:
    """Tests for _edge_canny."""

    def test_canny_default_thresholds(self):
        from tools.image_tool.processors.bordes import _edge_canny
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        result = _edge_canny(img)
        assert result["success"] is True
        assert result["image_data"]["shape"] == (50, 50)

    def test_canny_custom_thresholds(self):
        from tools.image_tool.processors.bordes import _edge_canny
        img = np.random.randint(0, 256, (50, 50), dtype=np.uint8)
        result = _edge_canny(img, threshold1=100, threshold2=200)
        assert result["success"] is True

    def test_canny_flat_image_no_edges(self):
        from tools.image_tool.processors.bordes import _edge_canny
        img = np.full((40, 40, 3), 128, dtype=np.uint8)
        result = _edge_canny(img)
        assert result["success"] is True
        assert result["image_data"]["array"].sum() == 0

    def test_canny_strong_edges_detected(self):
        from tools.image_tool.processors.bordes import _edge_canny
        img = np.zeros((50, 50), dtype=np.uint8)
        img[25, :] = 255  # horizontal white line
        result = _edge_canny(img, threshold1=50, threshold2=150)
        assert result["success"] is True
        # Should detect edges along the line
        assert result["image_data"]["array"].sum() > 0


class TestFindContours:
    """Tests for _find_contours."""

    @skip_no_cv2
    def test_find_contours_on_binary(self):
        from tools.image_tool.processors.bordes import _find_contours
        img = np.zeros((100, 100), dtype=np.uint8)
        img[20:80, 20:80] = 255
        result = _find_contours(img)
        assert result["success"] is True
        assert len(result["output_files"]) == 1
        assert "contour" in result["message"].lower()

    @skip_no_cv2
    def test_find_contours_on_rgb(self):
        from tools.image_tool.processors.bordes import _find_contours
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[20:80, 20:80] = 255
        result = _find_contours(img)
        assert result["success"] is True

    @skip_no_cv2
    def test_find_contours_empty_image(self):
        from tools.image_tool.processors.bordes import _find_contours
        img = np.zeros((50, 50), dtype=np.uint8)
        result = _find_contours(img)
        assert result["success"] is True
        assert "0 contours" in result["message"]

    @skip_no_cv2
    def test_find_contours_produces_output_file(self):
        from tools.image_tool.processors.bordes import _find_contours
        from pathlib import Path
        img = np.zeros((60, 60), dtype=np.uint8)
        img[10:50, 10:50] = 255
        result = _find_contours(img)
        assert result["success"] is True
        output = Path(result["output_files"][0])
        assert output.exists()


class TestBoundingBoxes:
    """Tests for _bounding_boxes."""

    @skip_no_cv2
    def test_bounding_boxes_on_binary(self):
        from tools.image_tool.processors.bordes import _bounding_boxes
        img = np.zeros((100, 100), dtype=np.uint8)
        img[20:80, 20:80] = 255
        result = _bounding_boxes(img)
        assert result["success"] is True
        assert len(result["output_files"]) == 1

    @skip_no_cv2
    def test_bounding_boxes_min_area_filter(self):
        from tools.image_tool.processors.bordes import _bounding_boxes
        img = np.zeros((100, 100), dtype=np.uint8)
        img[10:15, 10:15] = 255  # 5x5 = 25 area (small)
        img[50:90, 50:90] = 255  # 40x40 = 1600 area (large)
        # min_area=100 → should only find the large one
        result = _bounding_boxes(img, min_area=100)
        assert result["success"] is True
        assert "1 bounding" in result["message"]

    @skip_no_cv2
    def test_bounding_boxes_on_rgb(self):
        from tools.image_tool.processors.bordes import _bounding_boxes
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[20:80, 20:80] = 255
        result = _bounding_boxes(img)
        assert result["success"] is True

    @skip_no_cv2
    def test_bounding_boxes_produces_output_file(self):
        from tools.image_tool.processors.bordes import _bounding_boxes
        from pathlib import Path
        img = np.zeros((80, 80), dtype=np.uint8)
        img[10:70, 10:70] = 255
        result = _bounding_boxes(img)
        output = Path(result["output_files"][0])
        assert output.exists()


# ===========================================================================
# Integration: pipeline chains
# ===========================================================================

class TestPipelineChains:
    """Test chaining multiple processors in sequence (common real usage)."""

    def test_grayscale_then_sobel(self):
        from tools.image_tool.processors.geometria import _to_grayscale
        from tools.image_tool.processors.bordes import _edge_sobel
        img = np.random.randint(0, 256, (80, 80, 3), dtype=np.uint8)
        gray = _to_grayscale(img)
        assert gray["success"] is True
        edges = _edge_sobel(gray["image_data"]["array"])
        assert edges["success"] is True
        assert edges["image_data"]["shape"] == (80, 80)

    def test_blur_then_equalize(self):
        from tools.image_tool.processors.filtros import _filter_gaussian
        from tools.image_tool.processors.mejora import _equalize_histogram
        img = np.random.randint(0, 256, (60, 60, 3), dtype=np.uint8)
        blurred = _filter_gaussian(img, ksize=5)
        assert blurred["success"] is True
        eq = _equalize_histogram(blurred["image_data"]["array"])
        assert eq["success"] is True

    def test_crop_then_resize(self):
        from tools.image_tool.processors.geometria import _crop_region, _resize
        img = np.ones((100, 100, 3), dtype=np.uint8) * 128
        cropped = _crop_region(img, 10, 10, 40, 40)
        assert cropped["success"] is True
        resized = _resize(cropped["image_data"]["array"], 2.0)
        assert resized["success"] is True
        h, w = resized["image_data"]["shape"][:2]
        assert h == 80
        assert w == 80

    def test_erode_then_dilate_roundtrip(self):
        from tools.image_tool.processors.morfologia import _erode, _dilate
        img = np.zeros((50, 50), dtype=np.uint8)
        img[15:35, 15:35] = 255
        eroded = _erode(img, kernel_size=3)
        assert eroded["success"] is True
        dilated = _dilate(eroded["image_data"]["array"], kernel_size=3)
        assert dilated["success"] is True

    def test_gamma_then_gaussian(self):
        from tools.image_tool.processors.mejora import _adjust_gamma
        from tools.image_tool.processors.filtros import _filter_gaussian
        img = np.random.randint(0, 256, (40, 40, 3), dtype=np.uint8)
        gamma = _adjust_gamma(img, 0.5)
        assert gamma["success"] is True
        smoothed = _filter_gaussian(gamma["image_data"]["array"], ksize=3)
        assert smoothed["success"] is True


# ===========================================================================
# Edge cases: unusual input shapes
# ===========================================================================

class TestEdgeCases:
    """Edge cases: minimal sizes, unusual aspect ratios."""

    def test_1x1_image(self):
        from tools.image_tool.processors.geometria import _to_grayscale
        img = np.array([[[128, 128, 128]]], dtype=np.uint8)
        result = _to_grayscale(img)
        assert result["success"] is True
        assert result["image_data"]["shape"] == (1, 1)

    def test_very_wide_image(self):
        from tools.image_tool.processors.geometria import _resize
        img = np.ones((5, 500, 3), dtype=np.uint8)
        result = _resize(img, 0.5)
        assert result["success"] is True
        h, w = result["image_data"]["shape"][:2]
        assert h == 2
        assert w == 250

    def test_very_tall_image(self):
        from tools.image_tool.processors.geometria import _resize
        img = np.ones((500, 5, 3), dtype=np.uint8)
        result = _resize(img, 0.5)
        assert result["success"] is True
        h, w = result["image_data"]["shape"][:2]
        assert h == 250
        assert w == 2

    def test_all_zeros_image(self):
        from tools.image_tool.processors.mejora import _adjust_gamma
        img = np.zeros((20, 20), dtype=np.uint8)
        result = _adjust_gamma(img, 1.0)
        assert result["success"] is True
        assert result["image_data"]["array"].sum() == 0

    def test_all_255_image(self):
        from tools.image_tool.processors.mejora import _adjust_gamma
        img = np.full((20, 20), 255, dtype=np.uint8)
        result = _adjust_gamma(img, 1.0)
        assert result["success"] is True
        assert np.all(result["image_data"]["array"] == 255)

    def test_single_channel_3d(self):
        """Image with shape (H, W, 1) — edge case for 3-channel checks."""
        from tools.image_tool.processors.mejora import _adjust_brightness_contrast
        img = np.ones((20, 20, 1), dtype=np.uint8) * 128
        result = _adjust_brightness_contrast(img)
        assert result["success"] is True
        assert result["image_data"]["shape"] == (20, 20, 1)
