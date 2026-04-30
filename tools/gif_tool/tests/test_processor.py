"""
Tests for gif_tool.processor module.
"""
import os
import tempfile
import pytest
from pathlib import Path
import sys
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))
from processor import create_gif, extract_frames, get_gif_info


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as td:
        yield td


def create_test_image(path, size=(100, 100), color=(255, 0, 0)):
    img = Image.new('RGB', size, color)
    img.save(path)


def create_test_images(temp_dir, count=3, size=(100, 100)):
    paths = []
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
    for i in range(count):
        path = os.path.join(temp_dir, f'test_{i}.png')
        create_test_image(path, size, colors[i % len(colors)])
        paths.append(path)
    return paths


class TestCreateGif:
    def test_create_gif_basic(self, temp_dir):
        images = create_test_images(temp_dir, count=3)
        output = os.path.join(temp_dir, 'output.gif')
        
        result = create_gif(images, output_path=output)
        
        assert result['success'] is True
        assert os.path.exists(output)
        assert output in result['output_files']
    
    def test_create_gif_default_output(self, temp_dir):
        images = create_test_images(temp_dir, count=2)
        
        result = create_gif(images)
        
        assert result['success'] is True
        assert len(result['output_files']) == 1
        assert result['output_files'][0].endswith('_animated.gif')
    
    def test_create_gif_custom_duration(self, temp_dir):
        images = create_test_images(temp_dir, count=2)
        output = os.path.join(temp_dir, 'animated.gif')
        
        result = create_gif(images, output_path=output, duration=1000)
        
        assert result['success'] is True
    
    def test_create_gif_no_loop(self, temp_dir):
        images = create_test_images(temp_dir, count=2)
        output = os.path.join(temp_dir, 'animated.gif')
        
        result = create_gif(images, output_path=output, loop=0)
        
        assert result['success'] is True
    
    def test_create_gif_single_image(self, temp_dir):
        images = create_test_images(temp_dir, count=1)
        output = os.path.join(temp_dir, 'single.gif')
        
        result = create_gif(images, output_path=output)
        
        assert result['success'] is True
        assert os.path.exists(output)
    
    def test_create_gif_empty_list(self, temp_dir):
        result = create_gif([])
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_create_gif_nonexistent_images(self, temp_dir):
        result = create_gif(['/nonexistent/image.png'])
        
        assert result['success'] is False
    
    def test_create_gif_different_sizes(self, temp_dir):
        sizes = [(100, 100), (150, 150), (80, 80)]
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        images = []
        for i, (size, color) in enumerate(zip(sizes, colors)):
            path = os.path.join(temp_dir, f'size_{i}.png')
            create_test_image(path, size, color)
            images.append(path)
        
        output = os.path.join(temp_dir, 'resized.gif')
        result = create_gif(images, output_path=output)
        
        assert result['success'] is True


class TestExtractFrames:
    def test_extract_frames_basic(self, temp_dir):
        images = create_test_images(temp_dir, count=3)
        gif_path = os.path.join(temp_dir, 'test.gif')
        create_gif(images, output_path=gif_path)
        
        result = extract_frames(gif_path)
        
        assert result['success'] is True
        assert len(result['output_files']) == 3
        for frame_path in result['output_files']:
            assert os.path.exists(frame_path)
    
    def test_extract_frames_custom_output_dir(self, temp_dir):
        images = create_test_images(temp_dir, count=2)
        gif_path = os.path.join(temp_dir, 'test.gif')
        create_gif(images, output_path=gif_path)
        
        output_dir = os.path.join(temp_dir, 'my_frames')
        result = extract_frames(gif_path, output_dir=output_dir)
        
        assert result['success'] is True
        assert os.path.isdir(output_dir)
    
    def test_extract_frames_nonexistent_gif(self, temp_dir):
        result = extract_frames(os.path.join(temp_dir, 'nonexistent.gif'))
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_extract_frames_default_output_dir(self, temp_dir):
        images = create_test_images(temp_dir, count=2)
        gif_path = os.path.join(temp_dir, 'test.gif')
        create_gif(images, output_path=gif_path)
        
        result = extract_frames(gif_path)
        
        assert result['success'] is True
        assert 'test_frames' in result['output_files'][0]


class TestGetGifInfo:
    def test_get_gif_info_basic(self, temp_dir):
        images = create_test_images(temp_dir, count=3)
        gif_path = os.path.join(temp_dir, 'test.gif')
        create_gif(images, output_path=gif_path, duration=500)
        
        result = get_gif_info(gif_path)
        
        assert result['success'] is True
        assert 'file_name' in result
        assert 'file_size' in result
        assert 'size' in result
        assert 'frames' in result
        assert result['frames'] == 3
    
    def test_get_gif_info_size_info(self, temp_dir):
        images = create_test_images(temp_dir, count=2, size=(200, 150))
        gif_path = os.path.join(temp_dir, 'test.gif')
        create_gif(images, output_path=gif_path)
        
        result = get_gif_info(gif_path)
        
        assert result['success'] is True
        assert result['size'] == (200, 150)
    
    def test_get_gif_info_nonexistent_file(self, temp_dir):
        result = get_gif_info(os.path.join(temp_dir, 'nonexistent.gif'))
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_get_gif_info_single_frame(self, temp_dir):
        images = create_test_images(temp_dir, count=1)
        gif_path = os.path.join(temp_dir, 'single.gif')
        create_gif(images, output_path=gif_path)
        
        result = get_gif_info(gif_path)
        
        assert result['success'] is True
        assert result['frames'] >= 1
    
    def test_get_gif_info_contains_duration(self, temp_dir):
        images = create_test_images(temp_dir, count=2)
        gif_path = os.path.join(temp_dir, 'test.gif')
        create_gif(images, output_path=gif_path, duration=300)
        
        result = get_gif_info(gif_path)
        
        assert result['success'] is True
        assert 'duration' in result


class TestGifRoundTrips:
    def test_create_extract_roundtrip(self, temp_dir):
        original_images = create_test_images(temp_dir, count=4)
        gif_path = os.path.join(temp_dir, 'roundtrip.gif')
        create_gif(original_images, output_path=gif_path, duration=200)
        
        frames_dir = os.path.join(temp_dir, 'extracted')
        extract_result = extract_frames(gif_path, output_dir=frames_dir)
        
        assert extract_result['success'] is True
        assert len(extract_result['output_files']) == 4
    
    def test_create_info_roundtrip(self, temp_dir):
        images = create_test_images(temp_dir, count=3)
        gif_path = os.path.join(temp_dir, 'info_test.gif')
        create_gif(images, output_path=gif_path, duration=100)
        
        info = get_gif_info(gif_path)
        
        assert info['success'] is True
        assert info['frames'] == 3
        assert info['duration'] > 0
    
    def test_full_workflow(self, temp_dir):
        original = create_test_images(temp_dir, count=5, size=(80, 80))
        
        gif_path = os.path.join(temp_dir, 'workflow.gif')
        create_result = create_gif(original, output_path=gif_path, duration=150, loop=2)
        assert create_result['success'] is True
        
        info_result = get_gif_info(gif_path)
        assert info_result['success'] is True
        assert info_result['frames'] == 5
        
        extract_result = extract_frames(gif_path)
        assert extract_result['success'] is True
        assert len(extract_result['output_files']) == 5