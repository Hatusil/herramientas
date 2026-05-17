"""
Async processor for video_tool - Wrapper async para operaciones bloqueantes.
Cumple con máxima A9 (operaciones pesadas deben tener wrapper async).
"""
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Callable

# A12: Observabilidad - metrics para tracking
from core.metrics import Counter, Timer, increment

from tools.video_tool.processor import (
    extract_audio,
    convert_video,
    get_video_info,
)


# Executor compartido para operaciones async
_executor = ThreadPoolExecutor(max_workers=2)


def extract_audio_async(file_path: str, output_format: str = 'mp3') -> Dict[str, Any]:
    """Wrapper async para extract_audio."""
    return _executor.submit(extract_audio, file_path, output_format).result()


def convert_video_async(
    file_path: str,
    output_format: str,
    quality: str = 'medium',
    start_time: float = None,
    end_time: float = None
) -> Dict[str, Any]:
    """Wrapper async para convert_video."""
    return _executor.submit(
        convert_video, file_path, output_format, quality, start_time, end_time
    ).result()


def get_video_info_async(file_path: str) -> Dict[str, Any]:
    """Wrapper async para get_video_info."""
    return _executor.submit(get_video_info, file_path).result()