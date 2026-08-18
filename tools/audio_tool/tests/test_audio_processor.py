"""
Tests for audio_tool processors:
  - metadata.validate_metadata_value (pure, no mocks)
  - metadata.clean_audio_metadata / edit_audio_metadata
  - audio_info.get_audio_info
  - normalize.normalize_audio
  - convert.convert_audio
  - repair.verify_audio_integrity / repair_audio
"""
import json
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from pathlib import Path

from tools.audio_tool.processors.metadata import validate_metadata_value

# ─── metadata: validate_metadata_value (PURE) ──────────────────────────────


class TestValidateMetadataValue:
    """validate_metadata_value is a pure function — zero mocks."""

    # --- happy path ---

    def test_simple_ascii(self):
        ok, val = validate_metadata_value("My Song")
        assert ok is True
        assert val == "My Song"

    def test_spanish_accents(self):
        ok, val = validate_metadata_value("Canción Épica Ñoño Übergüte")
        assert ok is True
        assert val == "Canción Épica Ñoño Übergüte"

    def test_numbers_and_punctuation(self):
        ok, val = validate_metadata_value("Track 01 (Remastered) - feat. Someone")
        assert ok is True
        assert val == "Track 01 (Remastered) - feat. Someone"

    def test_allowed_special_chars(self):
        """Allowed pattern: ()-_.!,?'&"""
        ok, val = validate_metadata_value("A&B! C,D? E.F")
        assert ok is True
        assert val == "A&B! C,D? E.F"

    def test_whitespace_normalization(self):
        ok, val = validate_metadata_value("  too   many   spaces  ")
        assert ok is True
        assert val == "too many spaces"

    def test_tabs_newlines_collapsed(self):
        ok, val = validate_metadata_value("a\t\n\rb\t\nc")
        assert ok is True
        assert val == "a b c"

    # --- length limit ---

    def test_truncation_at_max_length(self):
        long_val = "A" * 150
        ok, val = validate_metadata_value(long_val, max_length=100)
        assert ok is True
        assert len(val) == 100

    def test_custom_max_length(self):
        ok, val = validate_metadata_value("Hello World", max_length=5)
        assert ok is True
        assert val == "Hello"

    def test_exact_max_length(self):
        val = "B" * 50
        ok, out = validate_metadata_value(val, max_length=50)
        assert ok is True
        assert out == val

    # --- rejected inputs ---

    def test_empty_string(self):
        ok, val = validate_metadata_value("")
        assert ok is False
        assert val == ""

    def test_none_like_empty(self):
        """Falsy input should fail."""
        ok, val = validate_metadata_value("")
        assert ok is False

    def test_only_spaces(self):
        ok, val = validate_metadata_value("     ")
        assert ok is False
        assert val == ""

    def test_only_tabs_and_newlines(self):
        ok, val = validate_metadata_value("\t\n\r")
        assert ok is False
        assert val == ""

    def test_only_disallowed_chars(self):
        """Characters not in allowed_pattern should be stripped, leaving empty."""
        ok, val = validate_metadata_value("@#$%^*{}[]|\\")
        assert ok is False
        assert val == ""

    def test_mixed_allowed_disallowed(self):
        """Disallowed chars stripped, allowed ones kept."""
        ok, val = validate_metadata_value("Good@#$ Title")
        assert ok is True
        assert val == "Good Title"

    def test_unicode_emoji_stripped(self):
        ok, val = validate_metadata_value("Song 🎵 Rock")
        assert ok is True
        assert val == "Song  Rock"  # emoji removed, spaces preserved

    def test_zero_max_length(self):
        ok, val = validate_metadata_value("Anything", max_length=0)
        assert ok is False
        assert val == ""


# ─── audio_info.get_audio_info ──────────────────────────────────────────────

from tools.audio_tool.processors.audio_info import (
    get_audio_info,
    _extract_audio_stream,
    _format_audio_info,
)


class TestExtractAudioStream:
    """Unit tests for _extract_audio_stream helper."""

    def test_finds_audio_stream(self):
        streams = [
            {"codec_type": "video", "codec_name": "h264"},
            {"codec_type": "audio", "codec_name": "aac"},
        ]
        result = _extract_audio_stream(streams)
        assert result is not None
        assert result["codec_name"] == "aac"

    def test_no_audio_stream(self):
        streams = [{"codec_type": "video", "codec_name": "h264"}]
        assert _extract_audio_stream(streams) is None

    def test_empty_streams(self):
        assert _extract_audio_stream([]) is None

    def test_first_audio_stream_returned(self):
        streams = [
            {"codec_type": "audio", "codec_name": "mp3"},
            {"codec_type": "audio", "codec_name": "aac"},
        ]
        result = _extract_audio_stream(streams)
        assert result["codec_name"] == "mp3"


class TestFormatAudioInfo:
    """Unit tests for _format_audio_info helper."""

    def test_with_audio_stream(self):
        fmt = {
            "size": "1024000",
            "duration": "180.5",
            "format_name": "mp3",
            "bit_rate": "192000",
            "tags": {"title": "T", "artist": "A", "album": "B", "track": "1", "date": "2024", "genre": "Pop"},
        }
        stream = {"codec_name": "mp3", "sample_rate": "44100", "channels": 2}
        result = _format_audio_info("/music/song.mp3", fmt, stream)

        assert result["success"] is True
        assert result["file_name"] == "song.mp3"
        assert result["file_size"] == 1024000
        assert result["duration"] == 180.5
        assert result["format"] == "mp3"
        assert result["codec"] == "mp3"
        assert result["sample_rate"] == 44100
        assert result["channels"] == 2
        assert result["bit_rate"] == 192000
        assert result["title"] == "T"
        assert result["artist"] == "A"
        assert result["genre"] == "Pop"

    def test_without_audio_stream(self):
        fmt = {"size": 0, "duration": 0, "format_name": "unknown", "bit_rate": 0, "tags": {}}
        result = _format_audio_info("/x.bin", fmt, None)

        assert result["success"] is True
        assert result["codec"] == "N/A"
        assert result["sample_rate"] == 0
        assert result["channels"] == 0
        assert result["title"] == ""
        assert result["artist"] == ""


class TestGetAudioInfo:
    """Integration-style tests for get_audio_info with mocked subprocess."""

    @patch("tools.audio_tool.processors.audio_info.check_ffmpeg", return_value=True)
    @patch("tools.audio_tool.processors.audio_info.os.path.exists", return_value=True)
    @patch("tools.audio_tool.processors.audio_info._run_ffprobe")
    def test_success_path(self, mock_ffprobe, mock_exists, mock_ffmpeg):
        ffprobe_output = {
            "format": {
                "size": "500000",
                "duration": "200.0",
                "format_name": "mp3",
                "bit_rate": "320000",
                "tags": {"title": "Test", "artist": "Me"},
            },
            "streams": [
                {"codec_type": "audio", "codec_name": "mp3", "sample_rate": "44100", "channels": 2}
            ],
        }
        mock_ffprobe.return_value = ffprobe_output

        result = get_audio_info("/fake/song.mp3")

        assert result["success"] is True
        assert result["title"] == "Test"
        assert result["codec"] == "mp3"
        assert result["duration"] == 200.0
        mock_ffprobe.assert_called_once_with("/fake/song.mp3")

    @patch("tools.audio_tool.processors.audio_info.os.path.exists", return_value=False)
    def test_file_not_found(self, mock_exists):
        result = get_audio_info("/nonexistent/file.mp3")
        assert result["success"] is False
        assert "no encontrado" in result["error"].lower()

    @patch("tools.audio_tool.processors.audio_info.check_ffmpeg", return_value=False)
    @patch("tools.audio_tool.processors.audio_info.os.path.exists", return_value=True)
    def test_ffmpeg_not_installed(self, mock_exists, mock_ffmpeg):
        result = get_audio_info("/fake/file.mp3")
        assert result["success"] is False
        assert "ffmpeg" in result["error"].lower()

    @patch("tools.audio_tool.processors.audio_info.check_ffmpeg", return_value=True)
    @patch("tools.audio_tool.processors.audio_info.os.path.exists", return_value=True)
    @patch("tools.audio_tool.processors.audio_info._run_ffprobe", side_effect=Exception("bad file"))
    def test_ffprobe_exception(self, mock_ffprobe, mock_exists, mock_ffmpeg):
        result = get_audio_info("/corrupt/file.mp3")
        assert result["success"] is False
        assert "bad file" in result["error"]

    @patch("tools.audio_tool.processors.audio_info.check_ffmpeg", return_value=True)
    @patch("tools.audio_tool.processors.audio_info.os.path.exists", return_value=True)
    @patch("tools.audio_tool.processors.audio_info._run_ffprobe")
    def test_no_tags(self, mock_ffprobe, mock_exists, mock_ffmpeg):
        mock_ffprobe.return_value = {"format": {"size": 0, "duration": 0, "bit_rate": 0}, "streams": []}
        result = get_audio_info("/empty/file.mp3")
        assert result["success"] is True
        assert result["title"] == ""
        assert result["codec"] == "N/A"


# ─── metadata.clean_audio_metadata / edit_audio_metadata ────────────────────

from tools.audio_tool.processors.metadata import clean_audio_metadata, edit_audio_metadata


class TestCleanAudioMetadata:
    """Tests for clean_audio_metadata with mocked subprocess and ffprobe."""

    @patch("tools.audio_tool.processors.metadata.check_ffmpeg", return_value=False)
    def test_ffmpeg_missing(self, mock_ff):
        result = clean_audio_metadata(["/fake/file.mp3"])
        assert result["success"] is False
        assert "ffmpeg" in result["error"].lower()

    @patch("tools.audio_tool.processors.metadata.get_output_path")
    @patch("tools.audio_tool.processors.metadata.subprocess.run")
    @patch("tools.audio_tool.processors.metadata.get_audio_info")
    @patch("tools.audio_tool.processors.metadata.check_ffmpeg", return_value=True)
    def test_success_single_file(self, mock_ff, mock_info, mock_run, mock_out):
        mock_info.return_value = {"success": True, "title": "Old Title"}
        mock_out.return_value = "/output/song_clean.mp3"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        # Make output file "exist" after ffmpeg
        with patch.object(Path, "exists", return_value=True):
            result = clean_audio_metadata(["/input/song.mp3"])

        assert result["success"] is True
        assert "1/1" in result["message"]
        assert len(result["output_files"]) == 1

    @patch("tools.audio_tool.processors.metadata.Path")
    @patch("tools.audio_tool.processors.metadata.get_audio_info")
    @patch("tools.audio_tool.processors.metadata.check_ffmpeg", return_value=True)
    def test_no_metadata_skipped(self, mock_ff, mock_info, mock_path_cls):
        mock_path_cls.return_value.exists.return_value = True
        mock_info.return_value = {"success": True, "title": "", "artist": "", "album": ""}
        result = clean_audio_metadata(["/input/song.mp3"])
        assert result["success"] is False
        assert "no hay metadatos" in result["message"].lower()

    @patch("tools.audio_tool.processors.metadata.get_audio_info")
    @patch("tools.audio_tool.processors.metadata.check_ffmpeg", return_value=True)
    def test_file_not_found(self, mock_ff, mock_info):
        result = clean_audio_metadata(["/nonexistent/file.mp3"])
        assert result["success"] is False
        assert any("no encontrado" in e.lower() for e in [result.get("error", "") or ""])

    @patch("tools.audio_tool.processors.metadata.get_output_path")
    @patch("tools.audio_tool.processors.metadata.subprocess.run")
    @patch("tools.audio_tool.processors.metadata.get_audio_info")
    @patch("tools.audio_tool.processors.metadata.check_ffmpeg", return_value=True)
    def test_ffmpeg_failure(self, mock_ff, mock_info, mock_run, mock_out):
        mock_info.return_value = {"success": True, "title": "T"}
        mock_out.return_value = "/output/out.mp3"
        mock_run.return_value = MagicMock(returncode=1, stderr="encode error detail")

        result = clean_audio_metadata(["/input/song.mp3"])
        assert result["success"] is False
        assert result["error"] is not None

    @patch("tools.audio_tool.processors.metadata.get_output_path")
    @patch("tools.audio_tool.processors.metadata.subprocess.run")
    @patch("tools.audio_tool.processors.metadata.get_audio_info")
    @patch("tools.audio_tool.processors.metadata.check_ffmpeg", return_value=True)
    def test_multiple_files_partial_success(self, mock_ff, mock_info, mock_run, mock_out):
        call_count = [0]
        def info_side_effect(path):
            call_count[0] += 1
            if call_count[0] == 1:
                return {"success": True, "title": "T1"}
            return {"success": True, "title": "T2"}
        mock_info.side_effect = info_side_effect

        mock_out.side_effect = lambda p, s: f"/output/{Path(p).stem}{s}.mp3"

        def run_side_effect(cmd, **kwargs):
            if "song1" in cmd[4]:
                return MagicMock(returncode=0, stderr="")
            return MagicMock(returncode=1, stderr="fail")
        mock_run.side_effect = run_side_effect

        with patch.object(Path, "exists", return_value=True):
            result = clean_audio_metadata(["/input/song1.mp3", "/input/song2.mp3"])

        assert "1/2" in result["message"]

    @patch("tools.audio_tool.processors.metadata.get_output_path")
    @patch("tools.audio_tool.processors.metadata.subprocess.run")
    @patch("tools.audio_tool.processors.metadata.get_audio_info")
    @patch("tools.audio_tool.processors.metadata.check_ffmpeg", return_value=True)
    def test_multiple_files_all_skipped(self, mock_ff, mock_info, mock_run, mock_out):
        mock_info.return_value = {"success": True, "title": "", "artist": ""}
        result = clean_audio_metadata(["/a.mp3", "/b.mp3"])
        assert result["success"] is False
        assert "2" in result["message"]  # "2 sin metadatos"

    @patch("tools.audio_tool.processors.metadata.get_audio_info")
    @patch("tools.audio_tool.processors.metadata.check_ffmpeg", return_value=True)
    def test_ffprobe_error_file(self, mock_ff, mock_info):
        mock_info.return_value = {"success": False}
        result = clean_audio_metadata(["/bad.mp3"])
        assert result["success"] is False


class TestEditAudioMetadata:
    """Tests for edit_audio_metadata with mocked subprocess."""

    @patch("tools.audio_tool.processors.metadata.check_ffmpeg", return_value=False)
    def test_ffmpeg_missing(self, mock_ff):
        result = edit_audio_metadata(["/f.mp3"], title="T")
        assert result["success"] is False
        assert "ffmpeg" in result["error"].lower()

    @patch("tools.audio_tool.processors.metadata.check_ffmpeg", return_value=True)
    def test_no_valid_metadata_fields(self, mock_ff):
        result = edit_audio_metadata(["/f.mp3"])
        assert result["success"] is False
        assert "no hay metadatos válidos" in result["error"].lower()

    def test_empty_title_rejected(self):
        result = edit_audio_metadata(["/f.mp3"], title="   ")
        assert result["success"] is False

    @patch("tools.audio_tool.processors.metadata.get_output_path")
    @patch("tools.audio_tool.processors.metadata.subprocess.run")
    @patch("tools.audio_tool.processors.metadata.check_ffmpeg", return_value=True)
    def test_success_edit(self, mock_ff, mock_run, mock_out):
        mock_out.return_value = "/output/song_edited.mp3"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            result = edit_audio_metadata(["/input/song.mp3"], title="New Title", artist="New Artist")

        assert result["success"] is True
        assert "1/1" in result["message"]
        # Verify ffmpeg command includes metadata flags
        cmd = mock_run.call_args[0][0]
        assert "-metadata" in cmd
        assert "title=New Title" in cmd
        assert "artist=New Artist" in cmd

    @patch("tools.audio_tool.processors.metadata.get_output_path")
    @patch("tools.audio_tool.processors.metadata.subprocess.run")
    @patch("tools.audio_tool.processors.metadata.check_ffmpeg", return_value=True)
    def test_disallowed_chars_stripped_in_metadata(self, mock_ff, mock_run, mock_out):
        mock_out.return_value = "/output/song_edited.mp3"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            edit_audio_metadata(["/input/song.mp3"], title="Song @#$%")

        cmd = mock_run.call_args[0][0]
        meta_args = [a for a in cmd if a.startswith("title=")]
        assert len(meta_args) == 1
        assert "@#$%" not in meta_args[0]
        assert "Song" in meta_args[0]

    @patch("tools.audio_tool.processors.metadata.get_output_path")
    @patch("tools.audio_tool.processors.metadata.subprocess.run")
    @patch("tools.audio_tool.processors.metadata.check_ffmpeg", return_value=True)
    def test_ffmpeg_failure(self, mock_ff, mock_run, mock_out):
        mock_out.return_value = "/output/out.mp3"
        mock_run.return_value = MagicMock(returncode=1, stderr="encode err")

        result = edit_audio_metadata(["/input/song.mp3"], title="T")
        assert result["success"] is False

    @patch("tools.audio_tool.processors.metadata.get_output_path")
    @patch("tools.audio_tool.processors.metadata.subprocess.run")
    @patch("tools.audio_tool.processors.metadata.check_ffmpeg", return_value=True)
    def test_file_not_found_in_list(self, mock_ff, mock_run, mock_out):
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        result = edit_audio_metadata(["/nonexistent.mp3"], title="T")
        assert result["success"] is False
        assert "no encontrado" in result["error"].lower()

    @patch("tools.audio_tool.processors.metadata.get_output_path")
    @patch("tools.audio_tool.processors.metadata.subprocess.run")
    @patch("tools.audio_tool.processors.metadata.check_ffmpeg", return_value=True)
    def test_multiple_metadata_fields(self, mock_ff, mock_run, mock_out):
        mock_out.return_value = "/output/ed.mp3"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            result = edit_audio_metadata(
                ["/input/s.mp3"],
                title="T", artist="A", album="B",
                genre="Rock", year="2024", track="1"
            )

        assert result["success"] is True
        cmd = mock_run.call_args[0][0]
        meta_values = [a for a in cmd if a.startswith("title=")]
        assert len(meta_values) == 1


# ─── normalize.normalize_audio ──────────────────────────────────────────────

from tools.audio_tool.processors.normalize import normalize_audio


class TestNormalizeAudio:
    """Tests for normalize_audio with mocked subprocess."""

    @patch("tools.audio_tool.processors.normalize.check_ffmpeg", return_value=False)
    def test_ffmpeg_missing(self, mock_ff):
        result = normalize_audio(["/f.mp3"])
        assert result["success"] is False
        assert "ffmpeg" in result["error"].lower()

    @patch("tools.audio_tool.processors.normalize.check_ffmpeg", return_value=True)
    def test_file_not_found(self, mock_ff):
        result = normalize_audio(["/nonexistent.mp3"])
        assert result["success"] is False
        assert "no encontrado" in result["error"].lower()

    @patch("tools.audio_tool.processors.normalize.get_output_path")
    @patch("tools.audio_tool.processors.normalize.subprocess.run")
    @patch("tools.audio_tool.processors.normalize.check_ffmpeg", return_value=True)
    def test_success_single_file(self, mock_ff, mock_run, mock_out):
        mock_out.return_value = "/output/song_normalized.mp3"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            result = normalize_audio(["/input/song.mp3"])

        assert result["success"] is True
        assert "1/1" in result["message"]
        # Verify ffmpeg command structure
        cmd = mock_run.call_args[0][0]
        assert "-af" in cmd
        assert "loudnorm" in cmd[cmd.index("-af") + 1]

    @patch("tools.audio_tool.processors.normalize.get_output_path")
    @patch("tools.audio_tool.processors.normalize.subprocess.run")
    @patch("tools.audio_tool.processors.normalize.check_ffmpeg", return_value=True)
    def test_custom_target_lufs(self, mock_ff, mock_run, mock_out):
        mock_out.return_value = "/output/out.mp3"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            normalize_audio(["/input/song.mp3"], target_lufs=-14)

        cmd = mock_run.call_args[0][0]
        af_idx = cmd.index("-af")
        af_filter = cmd[af_idx + 1]
        assert "-14" in af_filter

    @patch("tools.audio_tool.processors.normalize.get_output_path")
    @patch("tools.audio_tool.processors.normalize.subprocess.run")
    @patch("tools.audio_tool.processors.normalize.check_ffmpeg", return_value=True)
    def test_custom_quality(self, mock_ff, mock_run, mock_out):
        mock_out.return_value = "/output/out.mp3"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            normalize_audio(["/input/song.mp3"], quality=320)

        cmd = mock_run.call_args[0][0]
        assert "320k" in cmd

    @patch("tools.audio_tool.processors.normalize.get_output_path")
    @patch("tools.audio_tool.processors.normalize.subprocess.run")
    @patch("tools.audio_tool.processors.normalize.check_ffmpeg", return_value=True)
    def test_custom_sample_rate(self, mock_ff, mock_run, mock_out):
        mock_out.return_value = "/output/out.mp3"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            normalize_audio(["/input/song.mp3"], sample_rate=48000)

        cmd = mock_run.call_args[0][0]
        assert "48000" in cmd
        assert "-ar" in cmd

    @patch("tools.audio_tool.processors.normalize.get_output_path")
    @patch("tools.audio_tool.processors.normalize.subprocess.run")
    @patch("tools.audio_tool.processors.normalize.check_ffmpeg", return_value=True)
    def test_ffmpeg_failure(self, mock_ff, mock_run, mock_out):
        mock_out.return_value = "/output/out.mp3"
        mock_run.return_value = MagicMock(returncode=1, stderr="norm error detail")

        result = normalize_audio(["/input/song.mp3"])
        assert result["success"] is False
        assert result["error"] is not None

    @patch("tools.audio_tool.processors.normalize.get_output_path")
    @patch("tools.audio_tool.processors.normalize.subprocess.run")
    @patch("tools.audio_tool.processors.normalize.Path")
    @patch("tools.audio_tool.processors.normalize.check_ffmpeg", return_value=True)
    def test_timeout_error(self, mock_ff, mock_path_cls, mock_run, mock_out):
        mock_path_cls.return_value.exists.return_value = True
        mock_path_cls.return_value.stem.endswith.return_value = False
        mock_path_cls.return_value.suffix.lower.return_value = ".mp3"
        mock_out.return_value = "/output/out.mp3"
        import subprocess as _subprocess
        mock_run.side_effect = _subprocess.TimeoutExpired(cmd="ffmpeg", timeout=300)

        result = normalize_audio(["/input/song.mp3"])
        assert result["success"] is False
        assert "timeout" in result["error"].lower()

    @patch("tools.audio_tool.processors.normalize.check_ffmpeg", return_value=True)
    def test_already_normalized_skipped(self, mock_ff):
        result = normalize_audio(["/input/song_normalized.mp3"])
        assert result["success"] is False  # no output files, only skipped

    @patch("tools.audio_tool.processors.normalize.get_output_path")
    @patch("tools.audio_tool.processors.normalize.subprocess.run")
    @patch("tools.audio_tool.processors.normalize.check_ffmpeg", return_value=True)
    def test_return_dict_keys(self, mock_ff, mock_run, mock_out):
        mock_out.return_value = "/output/out.mp3"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            result = normalize_audio(["/input/s.mp3"])

        assert "success" in result
        assert "message" in result
        assert "output_files" in result
        assert "error" in result
        assert "skipped_files" in result

    @patch("tools.audio_tool.processors.normalize.get_output_path")
    @patch("tools.audio_tool.processors.normalize.subprocess.run")
    @patch("tools.audio_tool.processors.normalize.check_ffmpeg", return_value=True)
    def test_wav_codec_pcm(self, mock_ff, mock_run, mock_out):
        """WAV files should use pcm_s16le codec."""
        mock_out.return_value = "/output/song_normalized.wav"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            normalize_audio(["/input/song.wav"])

        cmd = mock_run.call_args[0][0]
        assert "pcm_s16le" in cmd

    @patch("tools.audio_tool.processors.normalize.get_output_path")
    @patch("tools.audio_tool.processors.normalize.subprocess.run")
    @patch("tools.audio_tool.processors.normalize.check_ffmpeg", return_value=True)
    def test_flac_codec(self, mock_ff, mock_run, mock_out):
        """FLAC files should use flac codec."""
        mock_out.return_value = "/output/song_normalized.flac"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            normalize_audio(["/input/song.flac"])

        cmd = mock_run.call_args[0][0]
        assert "flac" in cmd

    @patch("tools.audio_tool.processors.normalize.get_output_path")
    @patch("tools.audio_tool.processors.normalize.subprocess.run")
    @patch("tools.audio_tool.processors.normalize.check_ffmpeg", return_value=True)
    def test_multiple_files(self, mock_ff, mock_run, mock_out):
        mock_out.side_effect = lambda p, s: f"/output/{Path(p).stem}{s}.mp3"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            result = normalize_audio(["/input/a.mp3", "/input/b.mp3", "/input/c.mp3"])

        assert result["success"] is True
        assert "3/3" in result["message"]


# ─── convert.convert_audio ──────────────────────────────────────────────────

from tools.audio_tool.processors.convert import convert_audio, AUDIO_EXTENSIONS


class TestConvertAudio:
    """Tests for convert_audio with mocked subprocess."""

    @patch("tools.audio_tool.processors.convert.check_ffmpeg", return_value=False)
    def test_ffmpeg_missing(self, mock_ff):
        result = convert_audio(["/f.mp3"], "wav")
        assert result["success"] is False
        assert "ffmpeg" in result["error"].lower()

    @patch("tools.audio_tool.processors.convert.check_ffmpeg", return_value=True)
    def test_invalid_format(self, mock_ff):
        result = convert_audio(["/f.mp3"], "invalid_format")
        assert result["success"] is False
        assert "formato no válido" in result["error"].lower()

    @patch("tools.audio_tool.processors.convert.check_ffmpeg", return_value=True)
    def test_valid_output_formats(self, mock_ff):
        """All valid formats should not trigger format error."""
        for fmt in ["mp3", "wav", "flac", "ogg", "aac", "m4a"]:
            # Will fail at validation (file doesn't exist), but NOT format check
            result = convert_audio(["/f.mp3"], fmt)
            assert "formato no válido" not in (result.get("error") or "")

    @patch("tools.audio_tool.processors.convert._validate_audio_input")
    @patch("tools.audio_tool.processors.convert.get_output_path_format")
    @patch("tools.audio_tool.processors.convert.subprocess.run")
    @patch("tools.audio_tool.processors.convert.check_ffmpeg", return_value=True)
    def test_skip_same_format_default_quality(self, mock_ff, mock_run, mock_out, mock_val):
        mock_val.return_value = {"valid": True}
        result = convert_audio(["/input/song.mp3"], "mp3", quality=192)
        assert result["success"] is True
        assert len(result.get("skipped", [])) == 1
        mock_run.assert_not_called()

    @patch("tools.audio_tool.processors.convert._validate_audio_input")
    @patch("tools.audio_tool.processors.convert.get_output_path_format")
    @patch("tools.audio_tool.processors.convert.subprocess.run")
    @patch("tools.audio_tool.processors.convert.check_ffmpeg", return_value=True)
    def test_same_format_different_quality_proceeds(self, mock_ff, mock_run, mock_out, mock_val):
        mock_val.return_value = {"valid": True}
        mock_out.return_value = "/output/song_converted.mp3"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            result = convert_audio(["/input/song.mp3"], "mp3", quality=320)

        assert result["success"] is True
        mock_run.assert_called_once()

    @patch("tools.audio_tool.processors.convert._validate_audio_input")
    @patch("tools.audio_tool.processors.convert.get_output_path_format")
    @patch("tools.audio_tool.processors.convert.subprocess.run")
    @patch("tools.audio_tool.processors.convert.check_ffmpeg", return_value=True)
    def test_mp3_to_wav(self, mock_ff, mock_run, mock_out, mock_val):
        mock_val.return_value = {"valid": True}
        mock_out.return_value = "/output/song_converted.wav"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            result = convert_audio(["/input/song.mp3"], "wav")

        assert result["success"] is True
        cmd = mock_run.call_args[0][0]
        assert "pcm_s16le" in cmd

    @patch("tools.audio_tool.processors.convert._validate_audio_input")
    @patch("tools.audio_tool.processors.convert.get_output_path_format")
    @patch("tools.audio_tool.processors.convert.subprocess.run")
    @patch("tools.audio_tool.processors.convert.check_ffmpeg", return_value=True)
    def test_mp3_to_flac(self, mock_ff, mock_run, mock_out, mock_val):
        mock_val.return_value = {"valid": True}
        mock_out.return_value = "/output/song_converted.flac"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            result = convert_audio(["/input/song.mp3"], "flac")

        assert result["success"] is True
        cmd = mock_run.call_args[0][0]
        assert "flac" in cmd

    @patch("tools.audio_tool.processors.convert._validate_audio_input")
    @patch("tools.audio_tool.processors.convert.get_output_path_format")
    @patch("tools.audio_tool.processors.convert.subprocess.run")
    @patch("tools.audio_tool.processors.convert.check_ffmpeg", return_value=True)
    def test_mp3_to_ogg(self, mock_ff, mock_run, mock_out, mock_val):
        mock_val.return_value = {"valid": True}
        mock_out.return_value = "/output/song_converted.ogg"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            result = convert_audio(["/input/song.mp3"], "ogg", quality=256)

        assert result["success"] is True
        cmd = mock_run.call_args[0][0]
        assert "libvorbis" in cmd
        assert "256k" in cmd

    @patch("tools.audio_tool.processors.convert._validate_audio_input")
    @patch("tools.audio_tool.processors.convert.get_output_path_format")
    @patch("tools.audio_tool.processors.convert.subprocess.run")
    @patch("tools.audio_tool.processors.convert.check_ffmpeg", return_value=True)
    def test_ffmpeg_failure(self, mock_ff, mock_run, mock_out, mock_val):
        mock_val.return_value = {"valid": True}
        mock_out.return_value = "/output/out.mp3"
        mock_run.return_value = MagicMock(returncode=1, stderr="convert fail")

        result = convert_audio(["/input/song.wav"], "mp3")
        assert result["success"] is False

    @patch("tools.audio_tool.processors.convert._validate_audio_input")
    @patch("tools.audio_tool.processors.convert.check_ffmpeg", return_value=True)
    def test_validation_failure(self, mock_ff, mock_val):
        mock_val.return_value = {"valid": False, "error": "File too large"}
        result = convert_audio(["/input/big.mp3"], "wav")
        assert result["success"] is False
        assert "File too large" in result["error"]

    @patch("tools.audio_tool.processors.convert._validate_audio_input")
    @patch("tools.audio_tool.processors.convert.get_output_path_format")
    @patch("tools.audio_tool.processors.convert.subprocess.run")
    @patch("tools.audio_tool.processors.convert.check_ffmpeg", return_value=True)
    def test_return_dict_keys(self, mock_ff, mock_run, mock_out, mock_val):
        mock_val.return_value = {"valid": True}
        mock_out.return_value = "/output/out.wav"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            result = convert_audio(["/input/s.mp3"], "wav")

        assert "success" in result
        assert "message" in result
        assert "output_files" in result
        assert "skipped" in result
        assert "error" in result

    @patch("tools.audio_tool.processors.convert._validate_audio_input")
    @patch("tools.audio_tool.processors.convert.get_output_path_format")
    @patch("tools.audio_tool.processors.convert.subprocess.run")
    @patch("tools.audio_tool.processors.convert.check_ffmpeg", return_value=True)
    def test_multiple_files_all_converted(self, mock_ff, mock_run, mock_out, mock_val):
        mock_val.return_value = {"valid": True}
        mock_out.side_effect = lambda p, s, e: f"/output/{Path(p).stem}{s}{e}"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            result = convert_audio(["/a.mp3", "/b.mp3"], "wav")

        assert result["success"] is True
        assert "2/2" in result["message"]
        assert mock_run.call_count == 2

    def test_audio_extensions_constant(self):
        assert ".mp3" in AUDIO_EXTENSIONS
        assert ".wav" in AUDIO_EXTENSIONS
        assert ".flac" in AUDIO_EXTENSIONS
        assert ".ogg" in AUDIO_EXTENSIONS
        assert ".aac" in AUDIO_EXTENSIONS
        assert ".m4a" in AUDIO_EXTENSIONS


# ─── repair.verify_audio_integrity / repair_audio ────────────────────────────

from tools.audio_tool.processors.repair import verify_audio_integrity, repair_audio, verify_multiple_audio


class TestVerifyAudioIntegrity:
    """Tests for verify_audio_integrity with mocked subprocess."""

    @patch("tools.audio_tool.processors.repair.check_ffmpeg", return_value=False)
    def test_ffmpeg_missing(self, mock_ff):
        result = verify_audio_integrity("/f.mp3")
        assert result["corrupt"] is False
        assert "ffmpeg" in result["message"].lower()

    @patch("tools.audio_tool.processors.repair.Path")
    @patch("tools.audio_tool.processors.repair.check_ffmpeg", return_value=True)
    def test_file_not_found(self, mock_ff, mock_path_cls):
        mock_path_cls.return_value.exists.return_value = False
        result = verify_audio_integrity("/nonexistent.mp3")
        assert result["corrupt"] is False
        assert "no encontrado" in result["message"].lower()

    @patch("core.utils.get_ffprobe_path", return_value="/usr/bin/ffprobe")
    @patch("tools.audio_tool.processors.repair.subprocess.run")
    @patch("tools.audio_tool.processors.repair.Path")
    @patch("tools.audio_tool.processors.repair.check_ffmpeg", return_value=True)
    def test_healthy_file(self, mock_ff, mock_path_cls, mock_run, mock_ffprobe):
        mock_path_cls.return_value.exists.return_value = True
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="codec_type=audio\ncodec_name=mp3",
            stderr=""
        )
        result = verify_audio_integrity("/music/good.mp3")
        assert result["corrupt"] is False
        assert "ok" in result["message"].lower()

    @patch("core.utils.get_ffprobe_path", return_value="/usr/bin/ffprobe")
    @patch("tools.audio_tool.processors.repair.subprocess.run")
    @patch("tools.audio_tool.processors.repair.Path")
    @patch("tools.audio_tool.processors.repair.check_ffmpeg", return_value=True)
    def test_corrupt_file(self, mock_ff, mock_path_cls, mock_run, mock_ffprobe):
        mock_path_cls.return_value.exists.return_value = True
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Invalid data found"
        )
        result = verify_audio_integrity("/music/bad.mp3")
        assert result["corrupt"] is True
        assert "corrupto" in result["message"].lower()

    @patch("core.utils.get_ffprobe_path", return_value="/usr/bin/ffprobe")
    @patch("tools.audio_tool.processors.repair.subprocess.run")
    @patch("tools.audio_tool.processors.repair.Path")
    @patch("tools.audio_tool.processors.repair.check_ffmpeg", return_value=True)
    def test_no_audio_stream(self, mock_ff, mock_path_cls, mock_run, mock_ffprobe):
        mock_path_cls.return_value.exists.return_value = True
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="codec_type=video\ncodec_name=h264",  # no 'audio' in output
            stderr=""
        )
        result = verify_audio_integrity("/video/file.mp4")
        assert result["corrupt"] is True
        assert "audio" in result["message"].lower()

    @patch("core.utils.get_ffprobe_path", return_value="/usr/bin/ffprobe")
    @patch("tools.audio_tool.processors.repair.subprocess.run")
    @patch("tools.audio_tool.processors.repair.Path")
    @patch("tools.audio_tool.processors.repair.check_ffmpeg", return_value=True)
    def test_timeout(self, mock_ff, mock_path_cls, mock_run, mock_ffprobe):
        mock_path_cls.return_value.exists.return_value = True
        mock_run.side_effect = TimeoutError("timeout")
        result = verify_audio_integrity("/big/file.mp3")
        assert result["corrupt"] is True
        assert "timeout" in result["message"].lower()

    @patch("core.utils.get_ffprobe_path", return_value="/usr/bin/ffprobe")
    @patch("tools.audio_tool.processors.repair.subprocess.run")
    @patch("tools.audio_tool.processors.repair.Path")
    @patch("tools.audio_tool.processors.repair.check_ffmpeg", return_value=True)
    def test_return_structure(self, mock_ff, mock_path_cls, mock_run, mock_ffprobe):
        mock_path_cls.return_value.exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0, stdout="codec_type=audio", stderr="")
        result = verify_audio_integrity("/f.mp3")
        assert "corrupt" in result
        assert "message" in result
        assert "details" in result


class TestRepairAudio:
    """Tests for repair_audio with mocked subprocess."""

    @patch("tools.audio_tool.processors.repair.check_ffmpeg", return_value=False)
    def test_ffmpeg_missing(self, mock_ff):
        result = repair_audio(["/f.mp3"])
        assert result["success"] is False
        assert "ffmpeg" in result["error"].lower()

    @patch("tools.audio_tool.processors.repair.check_ffmpeg", return_value=True)
    def test_file_not_found(self, mock_ff):
        result = repair_audio(["/nonexistent.mp3"])
        assert result["success"] is False
        assert "no encontrado" in result["error"].lower()

    @patch("tools.audio_tool.processors.repair.get_output_path")
    @patch("tools.audio_tool.processors.repair.subprocess.run")
    @patch("tools.audio_tool.processors.repair.Path")
    @patch("tools.audio_tool.processors.repair.check_ffmpeg", return_value=True)
    def test_success_repair(self, mock_ff, mock_path_cls, mock_run, mock_out):
        mock_path_cls.return_value.exists.return_value = True
        mock_out.return_value = "/output/song_repaired.mp3"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        result = repair_audio(["/input/song.mp3"])
        assert result["success"] is True
        assert "1/1" in result["message"]
        assert len(result["output_files"]) == 1

    @patch("tools.audio_tool.processors.repair.get_output_path")
    @patch("tools.audio_tool.processors.repair.subprocess.run")
    @patch("tools.audio_tool.processors.repair.Path")
    @patch("tools.audio_tool.processors.repair.check_ffmpeg", return_value=True)
    def test_ffmpeg_failure(self, mock_ff, mock_path_cls, mock_run, mock_out):
        mock_path_cls.return_value.exists.return_value = True
        mock_out.return_value = "/output/out.mp3"
        mock_run.return_value = MagicMock(returncode=1, stderr="repair fail")

        result = repair_audio(["/input/song.mp3"])
        assert result["success"] is False
        assert "no se pudo reparar" in result["error"].lower()

    @patch("tools.audio_tool.processors.repair.get_output_path")
    @patch("tools.audio_tool.processors.repair.subprocess.run")
    @patch("tools.audio_tool.processors.repair.Path")
    @patch("tools.audio_tool.processors.repair.check_ffmpeg", return_value=True)
    def test_multiple_files(self, mock_ff, mock_path_cls, mock_run, mock_out):
        mock_path_cls.return_value.exists.return_value = True
        mock_out.side_effect = lambda p, s: f"/output/{Path(p).stem}{s}.mp3"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        result = repair_audio(["/a.mp3", "/b.mp3"])
        assert result["success"] is True
        assert "2/2" in result["message"]

    @patch("tools.audio_tool.processors.repair.get_output_path")
    @patch("tools.audio_tool.processors.repair.subprocess.run")
    @patch("tools.audio_tool.processors.repair.Path")
    @patch("tools.audio_tool.processors.repair.check_ffmpeg", return_value=True)
    def test_uses_320k_bitrate(self, mock_ff, mock_path_cls, mock_run, mock_out):
        """Repair should use libmp3lame at 320k."""
        mock_path_cls.return_value.exists.return_value = True
        mock_out.return_value = "/output/out.mp3"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        repair_audio(["/input/s.mp3"])
        cmd = mock_run.call_args[0][0]
        assert "libmp3lame" in cmd
        assert "320k" in cmd

    @patch("tools.audio_tool.processors.repair.get_output_path")
    @patch("tools.audio_tool.processors.repair.subprocess.run")
    @patch("tools.audio_tool.processors.repair.Path")
    @patch("tools.audio_tool.processors.repair.check_ffmpeg", return_value=True)
    def test_return_dict_keys(self, mock_ff, mock_path_cls, mock_run, mock_out):
        mock_path_cls.return_value.exists.return_value = True
        mock_out.return_value = "/output/out.mp3"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        result = repair_audio(["/input/s.mp3"])
        assert "success" in result
        assert "message" in result
        assert "output_files" in result
        assert "error" in result


class TestVerifyMultipleAudio:
    """Tests for verify_multiple_audio."""

    @patch("tools.audio_tool.processors.repair.verify_audio_integrity")
    def test_all_ok(self, mock_verify):
        mock_verify.return_value = {"corrupt": False, "message": "Archivo OK", "details": {}}
        result = verify_multiple_audio(["/a.mp3", "/b.mp3", "/c.mp3"])
        assert result["success"] is True
        assert result["total"] == 3
        assert result["ok"] == 3
        assert result["corrupt"] == 0

    @patch("tools.audio_tool.processors.repair.verify_audio_integrity")
    def test_mixed_results(self, mock_verify):
        mock_verify.side_effect = [
            {"corrupt": False, "message": "OK", "details": {}},
            {"corrupt": True, "message": "Corrupto", "details": {}},
            {"corrupt": False, "message": "OK", "details": {}},
        ]
        result = verify_multiple_audio(["/a.mp3", "/b.mp3", "/c.mp3"])
        assert result["ok"] == 2
        assert result["corrupt"] == 1
        assert len(result["results"]) == 3

    @patch("tools.audio_tool.processors.repair.verify_audio_integrity")
    def test_empty_list(self, mock_verify):
        result = verify_multiple_audio([])
        assert result["success"] is True
        assert result["total"] == 0
        assert result["ok"] == 0
        assert result["corrupt"] == 0

    @patch("tools.audio_tool.processors.repair.verify_audio_integrity")
    def test_result_structure(self, mock_verify):
        mock_verify.return_value = {"corrupt": False, "message": "OK", "details": {}}
        result = verify_multiple_audio(["/song.mp3"])
        entry = result["results"][0]
        assert "file" in entry
        assert "name" in entry
        assert "corrupt" in entry
        assert "message" in entry


# ─── Edge cases and integration-level mocks ─────────────────────────────────


class TestConvertAudioEdgeCases:
    """Edge cases for convert_audio."""

    @patch("tools.audio_tool.processors.convert.check_ffmpeg", return_value=True)
    def test_empty_files_list(self, mock_ff):
        result = convert_audio([], "wav")
        assert result["success"] is False  # no output_files

    @patch("tools.audio_tool.processors.convert._validate_audio_input")
    @patch("tools.audio_tool.processors.convert.check_ffmpeg", return_value=True)
    def test_all_files_fail_validation(self, mock_ff, mock_val):
        mock_val.return_value = {"valid": False, "error": "bad"}
        result = convert_audio(["/a.mp3", "/b.mp3"], "wav")
        assert result["success"] is False
        assert "2 errors" in result["error"].lower() or "bad" in result["error"]

    @patch("tools.audio_tool.processors.convert._validate_audio_input")
    @patch("tools.audio_tool.processors.convert.get_output_path_format")
    @patch("tools.audio_tool.processors.convert.subprocess.run")
    @patch("tools.audio_tool.processors.convert.check_ffmpeg", return_value=True)
    def test_subprocess_exception(self, mock_ff, mock_run, mock_out, mock_val):
        mock_val.return_value = {"valid": True}
        mock_out.return_value = "/output/out.mp3"
        mock_run.side_effect = OSError("disk full")

        result = convert_audio(["/input/s.wav"], "mp3")
        assert result["success"] is False
        assert "disk full" in result["error"]

    @patch("tools.audio_tool.processors.convert._validate_audio_input")
    @patch("tools.audio_tool.processors.convert.get_output_path_format")
    @patch("tools.audio_tool.processors.convert.subprocess.run")
    @patch("tools.audio_tool.processors.convert.check_ffmpeg", return_value=True)
    def test_all_skipped_returns_success(self, mock_ff, mock_run, mock_out, mock_val):
        """All files already in target format with default quality → success=True, output_files=[]"""
        mock_val.return_value = {"valid": True}
        result = convert_audio(["/a.mp3", "/b.mp3"], "mp3", quality=192)
        assert result["success"] is True
        assert result["output_files"] == []
        assert len(result["skipped"]) == 2


class TestNormalizeAudioEdgeCases:
    """Edge cases for normalize_audio."""

    @patch("tools.audio_tool.processors.normalize.check_ffmpeg", return_value=True)
    def test_empty_files_list(self, mock_ff):
        result = normalize_audio([])
        assert result["success"] is False

    @patch("tools.audio_tool.processors.normalize.get_output_path")
    @patch("tools.audio_tool.processors.normalize.subprocess.run")
    @patch("tools.audio_tool.processors.normalize.check_ffmpeg", return_value=True)
    def test_ogg_uses_libmp3lame(self, mock_ff, mock_run, mock_out):
        """OGG files fall through to the else clause using libmp3lame."""
        mock_out.return_value = "/output/song_normalized.ogg"
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            normalize_audio(["/input/song.ogg"])

        cmd = mock_run.call_args[0][0]
        assert "libmp3lame" in cmd


class TestMetadataEdgeCases:
    """Edge cases for metadata functions."""

    @patch("tools.audio_tool.processors.metadata.get_output_path")
    @patch("tools.audio_tool.processors.metadata.subprocess.run")
    @patch("tools.audio_tool.processors.metadata.Path")
    @patch("tools.audio_tool.processors.metadata.get_audio_info")
    @patch("tools.audio_tool.processors.metadata.check_ffmpeg", return_value=True)
    def test_clean_subprocess_exception(self, mock_ff, mock_info, mock_path_cls, mock_run, mock_out):
        mock_path_cls.return_value.exists.return_value = True
        mock_info.return_value = {"success": True, "title": "T"}
        mock_out.return_value = "/output/out.mp3"
        mock_run.side_effect = OSError("permission denied")

        result = clean_audio_metadata(["/input/song.mp3"])
        assert result["success"] is False
        assert "excepción" in result["error"].lower()

    @patch("tools.audio_tool.processors.metadata.get_output_path")
    @patch("tools.audio_tool.processors.metadata.subprocess.run")
    @patch("tools.audio_tool.processors.metadata.Path")
    @patch("tools.audio_tool.processors.metadata.check_ffmpeg", return_value=True)
    def test_edit_subprocess_exception(self, mock_ff, mock_path_cls, mock_run, mock_out):
        mock_path_cls.return_value.exists.return_value = True
        mock_out.return_value = "/output/out.mp3"
        mock_run.side_effect = OSError("disk error")

        result = edit_audio_metadata(["/input/song.mp3"], title="T")
        assert result["success"] is False
        assert "excepción" in result["error"].lower()

    @patch("tools.audio_tool.processors.metadata.get_output_path")
    @patch("tools.audio_tool.processors.metadata.subprocess.run")
    @patch("tools.audio_tool.processors.metadata.Path")
    @patch("tools.audio_tool.processors.metadata.get_audio_info")
    @patch("tools.audio_tool.processors.metadata.check_ffmpeg", return_value=True)
    def test_clean_multiple_files_all_errors(self, mock_ff, mock_info, mock_path_cls, mock_run, mock_out):
        mock_path_cls.return_value.exists.return_value = True
        mock_info.return_value = {"success": True, "title": "T"}
        mock_out.return_value = "/output/out.mp3"
        mock_run.return_value = MagicMock(returncode=1, stderr="err")

        result = clean_audio_metadata(["/a.mp3", "/b.mp3"])
        assert result["success"] is False
        assert result["error"] is not None
