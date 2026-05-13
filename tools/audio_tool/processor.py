"""Audio tool processor — re-export from modular processors."""
from tools.audio_tool.processors import (
    normalize_audio, normalize_audio_async,
    convert_audio, convert_audio_async,
    clean_audio_metadata, clean_audio_metadata_async,
    edit_audio_metadata, edit_audio_metadata_async,
    repair_audio, repair_audio_async,
    get_audio_info, get_metadata,
    verify_multiple_audio
)
