"""
Comprehensive tests for video_tool.processor module.

Covers:
  - _validate_video_input: file existence, extension, size
  - _should_skip_conversion: same-format + default-CRF skip logic
  - _build_ffmpeg_command: command construction per format
  - _execute_ffmpeg: subprocess execution
  - extract_audio: full flow with mocked subprocess
  - convert_video: multi-file orchestration with mocked subprocess
  - get_video_info: ffprobe JSON parsing with mocked subprocess
"""
import importlib.util
import json
import sys
from pathlib import Path
from types import MappingProxyType
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Dynamic import — register in sys.modules so patch("video_processor.xxx") works
# ---------------------------------------------------------------------------
def _load_processor():
    tool_dir = Path(__file__).parent.parent
    processor_path = tool_dir / "processor.py"
    spec = importlib.util.spec_from_file_location("video_processor", processor_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Register so unittest.mock.patch can resolve "video_processor.xxx"
    sys.modules["video_processor"] = module
    return module


proc = _load_processor()
_MOD = "video_processor"


# ===================================================================
# _validate_video_input
# ===================================================================
class TestValidateVideoInput:
    """_validate_video_input checks existence, extension, and size."""

    def test_valid_mp4(self, tmp_path):
        f = tmp_path / "clip.mp4"
        f.write_bytes(b"\x00" * 1024)
        result = proc._validate_video_input(str(f))
        assert result == {"valid": True}

    def test_valid_mkv(self, tmp_path):
        f = tmp_path / "clip.mkv"
        f.write_bytes(b"\x00" * 1024)
        result = proc._validate_video_input(str(f))
        assert result == {"valid": True}

    def test_valid_webm(self, tmp_path):
        f = tmp_path / "clip.webm"
        f.write_bytes(b"\x00" * 512)
        assert proc._validate_video_input(str(f)) == {"valid": True}

    def test_file_not_found(self, tmp_path):
        result = proc._validate_video_input(str(tmp_path / "missing.mp4"))
        assert result["valid"] is False
        assert "error" in result

    def test_disallowed_extension(self, tmp_path):
        f = tmp_path / "notes.txt"
        f.write_text("hello")
        result = proc._validate_video_input(str(f))
        assert result["valid"] is False
        assert "error" in result

    def test_no_extension(self, tmp_path):
        f = tmp_path / "noext"
        f.write_bytes(b"\x00")
        result = proc._validate_video_input(str(f))
        assert result["valid"] is False

    def test_file_too_large(self, tmp_path):
        f = tmp_path / "huge.mp4"
        f.write_bytes(b"\x00")
        with patch(f"{_MOD}.validate_file_size", return_value={"valid": False, "error": "File too large", "size_mb": 2001}):
            result = proc._validate_video_input(str(f))
        assert result["valid"] is False
        assert "too large" in result["error"].lower()

    def test_empty_path(self):
        result = proc._validate_video_input("")
        assert result["valid"] is False


# ===================================================================
# _should_skip_conversion
# ===================================================================
class TestShouldSkipConversion:
    """Skip when input format == output format AND CRF is default (23)."""

    def test_same_format_default_crf(self, tmp_path):
        f = tmp_path / "video.mp4"
        f.write_bytes(b"\x00")
        reason = proc._should_skip_conversion(str(f), "mp4", {})
        assert reason is not None
        assert "Ya está en MP4" in reason

    def test_same_format_explicit_default_crf(self, tmp_path):
        f = tmp_path / "video.mp4"
        f.write_bytes(b"\x00")
        reason = proc._should_skip_conversion(str(f), "mp4", {"crf": 23})
        assert reason is not None

    def test_same_format_non_default_crf(self, tmp_path):
        f = tmp_path / "video.mp4"
        f.write_bytes(b"\x00")
        reason = proc._should_skip_conversion(str(f), "mp4", {"crf": 18})
        assert reason is None  # Should NOT skip — user wants different quality

    def test_different_format(self, tmp_path):
        f = tmp_path / "video.mp4"
        f.write_bytes(b"\x00")
        reason = proc._should_skip_conversion(str(f), "avi", {})
        assert reason is None

    def test_case_insensitive(self, tmp_path):
        f = tmp_path / "video.MP4"
        f.write_bytes(b"\x00")
        reason = proc._should_skip_conversion(str(f), "mp4", {})
        assert reason is not None

    def test_skip_message_contains_filename(self, tmp_path):
        f = tmp_path / "myclip.mp4"
        f.write_bytes(b"\x00")
        reason = proc._should_skip_conversion(str(f), "mp4", {})
        assert "myclip.mp4" in reason

    def test_mkv_to_mkv_skip(self, tmp_path):
        f = tmp_path / "video.mkv"
        f.write_bytes(b"\x00")
        reason = proc._should_skip_conversion(str(f), "mkv", {})
        assert reason is not None


# ===================================================================
# _build_ffmpeg_command
# ===================================================================
class TestBuildFfmpegCommand:
    """Verify command construction for each output format."""

    def _cmd(self, output_format, options=None):
        if options is None:
            options = {}
        video_path = "/tmp/in.mp4"
        output_path = Path("/tmp/out." + output_format)
        with patch(f"{_MOD}.get_ffmpeg_path", return_value="/usr/bin/ffmpeg"):
            cmd = proc._build_ffmpeg_command(video_path, output_path, output_format, options)
        return cmd

    def test_mp4_command(self):
        cmd = self._cmd("mp4")
        assert cmd[0] == "/usr/bin/ffmpeg"
        assert "-y" in cmd
        assert "-i" in cmd
        assert "libx264" in cmd
        assert "-preset" in cmd
        assert "medium" in cmd
        assert "-crf" in cmd
        assert "aac" in cmd
        assert "-b:a" in cmd
        assert "128k" in cmd

    def test_mkv_command(self):
        cmd = self._cmd("mkv")
        assert "libx264" in cmd
        assert "-preset" in cmd
        assert "aac" in cmd

    def test_avi_command(self):
        cmd = self._cmd("avi")
        assert "mpeg4" in cmd
        assert "mp3" in cmd
        # avi does NOT have preset/crf flags
        assert "-preset" not in cmd

    def test_mov_command(self):
        cmd = self._cmd("mov")
        assert "mpeg4" in cmd
        assert "aac" in cmd

    def test_unknown_format_defaults(self):
        cmd = self._cmd("flv")
        # Unknown format → libx264 video, aac audio
        assert "libx264" in cmd
        assert "aac" in cmd

    def test_custom_crf(self):
        cmd = self._cmd("mp4", {"crf": 18})
        assert "18" in cmd

    def test_default_crf(self):
        cmd = self._cmd("mp4", {})
        assert "23" in cmd

    def test_output_path_is_last_arg(self):
        cmd = self._cmd("mp4")
        assert cmd[-1] == "/tmp/out.mp4"

    def test_opus_audio_codec_no_bitrate(self):
        """libopus is handled in the no-bitrate branch."""
        with patch(f"{_MOD}.get_ffmpeg_path", return_value="ffmpeg"):
            with patch(f"{_MOD}._get_audio_codecs", return_value=MappingProxyType({"mp4": "libopus"})):
                cmd = proc._build_ffmpeg_command(
                    "/tmp/in.mp4", Path("/tmp/out.mp4"), "mp4", {}
                )
        assert "libopus" in cmd
        assert "-b:a" not in cmd

    def test_vorbis_audio_codec_no_bitrate(self):
        with patch(f"{_MOD}.get_ffmpeg_path", return_value="ffmpeg"):
            with patch(f"{_MOD}._get_audio_codecs", return_value=MappingProxyType({"mp4": "libvorbis"})):
                cmd = proc._build_ffmpeg_command(
                    "/tmp/in.mp4", Path("/tmp/out.mp4"), "mp4", {}
                )
        assert "libvorbis" in cmd
        assert "-b:a" not in cmd


# ===================================================================
# _execute_ffmpeg
# ===================================================================
class TestExecuteFfmpeg:
    """Test the _execute_ffmpeg helper."""

    @patch(f"{_MOD}.subprocess.run")
    def test_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        output = Path("/tmp/out.mp4")
        # Simulate output file exists
        with patch.object(Path, "exists", return_value=True):
            ok, err = proc._execute_ffmpeg(["ffmpeg", "-i", "in.mp4", "out.mp4"], output)
        assert ok is True
        assert err == ""

    @patch(f"{_MOD}.subprocess.run")
    def test_failure_nonzero_return(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr="bad codec")
        output = Path("/tmp/out.mp4")
        with patch.object(Path, "exists", return_value=False):
            ok, err = proc._execute_ffmpeg(["ffmpeg"], output)
        assert ok is False
        assert "bad codec" in err

    @patch(f"{_MOD}.subprocess.run")
    def test_failure_no_stderr(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr=None)
        output = Path("/tmp/out.mp4")
        with patch.object(Path, "exists", return_value=False):
            ok, err = proc._execute_ffmpeg(["ffmpeg"], output)
        assert ok is False
        assert "Unknown error" in err

    @patch(f"{_MOD}.subprocess.run")
    def test_exception_caught(self, mock_run):
        mock_run.side_effect = OSError("permission denied")
        ok, err = proc._execute_ffmpeg(["ffmpeg"], Path("/tmp/out.mp4"))
        assert ok is False
        assert "permission denied" in err

    @patch(f"{_MOD}.subprocess.run")
    def test_stderr_truncated_to_100_chars(self, mock_run):
        long_err = "x" * 300
        mock_run.return_value = MagicMock(returncode=1, stderr=long_err)
        with patch.object(Path, "exists", return_value=False):
            ok, err = proc._execute_ffmpeg(["ffmpeg"], Path("/tmp/out.mp4"))
        assert len(err) <= 100


# ===================================================================
# extract_audio
# ===================================================================
class TestExtractAudio:
    """Full flow tests for extract_audio with mocked subprocess."""

    @patch(f"{_MOD}.check_ffmpeg", return_value=False)
    def test_no_ffmpeg(self, mock_check):
        result = proc.extract_audio("/tmp/video.mp3")
        assert result["success"] is False
        assert "FFmpeg" in result["error"]
        assert result["output_files"] == []

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    def test_invalid_input_file(self, mock_check):
        result = proc.extract_audio("/tmp/nonexistent.mp4")
        assert result["success"] is False
        assert "error" in result

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    def test_wrong_extension(self, mock_check):
        with patch.object(proc, "_validate_video_input", return_value={"valid": False, "error": "Bad ext"}):
            result = proc.extract_audio("/tmp/file.txt")
            assert result["success"] is False

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    @patch(f"{_MOD}.subprocess.run")
    def test_mp3_success(self, mock_run, mock_check, tmp_path):
        video = tmp_path / "clip.mp4"
        video.write_bytes(b"\x00" * 100)

        # Mock successful subprocess
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        # Simulate output file exists
        output_path = tmp_path / "clip_audio.mp3"

        with patch.object(Path, "exists", return_value=True):
            result = proc.extract_audio(str(video), "mp3")

        assert result["success"] is True
        assert "output_files" in result
        assert len(result["output_files"]) == 1
        assert "clip_audio.mp3" in result["output_files"][0]
        assert result["error"] is None

        # Verify correct codec used
        cmd = mock_run.call_args[0][0]
        assert "libmp3lame" in cmd
        assert "192k" in cmd

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    @patch(f"{_MOD}.subprocess.run")
    def test_ogg_codec(self, mock_run, mock_check, tmp_path):
        video = tmp_path / "clip.mp4"
        video.write_bytes(b"\x00" * 100)
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            result = proc.extract_audio(str(video), "ogg")

        cmd = mock_run.call_args[0][0]
        assert "libvorbis" in cmd
        assert "192k" in cmd

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    @patch(f"{_MOD}.subprocess.run")
    def test_wav_codec_no_bitrate(self, mock_run, mock_check, tmp_path):
        video = tmp_path / "clip.mp4"
        video.write_bytes(b"\x00" * 100)
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            result = proc.extract_audio(str(video), "wav")

        cmd = mock_run.call_args[0][0]
        assert "pcm_s16le" in cmd
        assert "-b:a" not in cmd

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    @patch(f"{_MOD}.subprocess.run")
    def test_unknown_format_uses_copy(self, mock_run, mock_check, tmp_path):
        video = tmp_path / "clip.mp4"
        video.write_bytes(b"\x00" * 100)
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            result = proc.extract_audio(str(video), "flac")

        cmd = mock_run.call_args[0][0]
        assert "copy" in cmd
        assert "-b:a" not in cmd

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    @patch(f"{_MOD}.subprocess.run")
    def test_ffmpeg_failure(self, mock_run, mock_check, tmp_path):
        video = tmp_path / "clip.mp4"
        video.write_bytes(b"\x00" * 100)
        mock_run.return_value = MagicMock(returncode=1, stderr="codec error details")

        with patch.object(Path, "exists", return_value=False):
            result = proc.extract_audio(str(video))

        assert result["success"] is False
        assert "error" in result

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    @patch(f"{_MOD}.subprocess.run")
    def test_ffmpeg_failure_truncates_error(self, mock_run, mock_check, tmp_path):
        video = tmp_path / "clip.mp4"
        video.write_bytes(b"\x00" * 100)
        mock_run.return_value = MagicMock(returncode=1, stderr="x" * 500)

        with patch.object(Path, "exists", return_value=False):
            result = proc.extract_audio(str(video))

        assert len(result["error"]) <= 120  # "Error al extraer: " + 100 chars

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    @patch(f"{_MOD}.subprocess.run", side_effect=OSError("timeout"))
    def test_exception_handling(self, mock_run, mock_check, tmp_path):
        video = tmp_path / "clip.mp4"
        video.write_bytes(b"\x00" * 100)
        result = proc.extract_audio(str(video))
        assert result["success"] is False
        assert "timeout" in result["error"]

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    @patch(f"{_MOD}.subprocess.run")
    def test_command_contains_vn_flag(self, mock_run, mock_check, tmp_path):
        """Verify -vn (no video) flag is present to strip video stream."""
        video = tmp_path / "clip.mp4"
        video.write_bytes(b"\x00" * 100)
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with patch.object(Path, "exists", return_value=True):
            proc.extract_audio(str(video), "mp3")

        cmd = mock_run.call_args[0][0]
        assert "-vn" in cmd


# ===================================================================
# convert_video
# ===================================================================
class TestConvertVideo:
    """Tests for convert_video multi-file orchestration."""

    @patch(f"{_MOD}.check_ffmpeg", return_value=False)
    def test_no_ffmpeg(self, mock_check):
        result = proc.convert_video(["/tmp/a.mp4"], "avi")
        assert result["success"] is False
        assert "FFmpeg" in result["error"]
        assert result["output_files"] == []

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    def test_missing_file(self, mock_check):
        result = proc.convert_video(["/tmp/nonexistent.mp4"], "avi")
        assert result["success"] is False
        assert "No encontrado" in result["error"]

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    def test_all_skipped(self, mock_check, tmp_path):
        """When all files already match format + default CRF → success with skip message."""
        f = tmp_path / "video.mp4"
        f.write_bytes(b"\x00")
        result = proc.convert_video([str(f)], "mp4")
        assert result["success"] is True
        assert len(result["skipped"]) == 1
        assert "MP4" in result["skipped"][0]
        assert result["output_files"] == []

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    def test_mixed_skipped_and_converted(self, mock_check, tmp_path):
        """One file skipped (same fmt + default CRF), one converted."""
        same = tmp_path / "same.mp4"
        same.write_bytes(b"\x00")
        diff = tmp_path / "diff.avi"
        diff.write_bytes(b"\x00")

        with patch.object(proc, "_execute_ffmpeg", return_value=(True, "")):
            result = proc.convert_video([str(same), str(diff)], "mp4")

        assert result["success"] is True
        assert len(result["skipped"]) == 1
        assert len(result["output_files"]) == 1

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    def test_non_default_crf_prevents_skip(self, mock_check, tmp_path):
        """Different CRF means no skip even if same format."""
        f = tmp_path / "video.mp4"
        f.write_bytes(b"\x00")

        with patch.object(proc, "_execute_ffmpeg", return_value=(True, "")):
            with patch.object(Path, "exists", return_value=True):
                result = proc.convert_video([str(f)], "mp4", crf=18)

        assert result["success"] is True
        assert len(result["skipped"]) == 0

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    def test_convert_to_avi(self, mock_check, tmp_path):
        f = tmp_path / "clip.mp4"
        f.write_bytes(b"\x00")

        with patch.object(proc, "_execute_ffmpeg", return_value=(True, "")):
            with patch.object(Path, "exists", return_value=True):
                result = proc.convert_video([str(f)], "avi")

        assert result["success"] is True
        assert len(result["output_files"]) == 1
        assert "avi" in result["output_files"][0]

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    def test_ffmpeg_execution_failure(self, mock_check, tmp_path):
        f = tmp_path / "clip.mp4"
        f.write_bytes(b"\x00")

        with patch.object(proc, "_execute_ffmpeg", return_value=(False, "codec not found")):
            result = proc.convert_video([str(f)], "avi")

        assert result["success"] is False
        assert "codec not found" in result["error"]

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    def test_multiple_files_partial_failure(self, mock_check, tmp_path):
        """One succeeds, one fails."""
        ok_file = tmp_path / "ok.mp4"
        ok_file.write_bytes(b"\x00")
        bad_file = tmp_path / "bad.mp4"
        bad_file.write_bytes(b"\x00")

        call_count = 0

        def fake_execute(cmd, output_path):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return True, ""
            return False, "encoding error"

        with patch.object(proc, "_execute_ffmpeg", side_effect=fake_execute):
            result = proc.convert_video([str(ok_file), str(bad_file)], "avi")

        assert result["success"] is True
        assert len(result["output_files"]) == 1
        assert "encoding error" in result["error"]

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    def test_empty_file_list(self, mock_check):
        result = proc.convert_video([], "mp4")
        assert result["success"] is False
        assert result["output_files"] == []
        assert result["skipped"] == []

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    def test_output_path_format(self, mock_check, tmp_path):
        """Output file is {stem}_converted.{format}."""
        f = tmp_path / "myvideo.mp4"
        f.write_bytes(b"\x00")

        with patch.object(proc, "_execute_ffmpeg", return_value=(True, "")) as mock_exec:
            proc.convert_video([str(f)], "avi")

        cmd_arg = mock_exec.call_args[0][0]
        output_path = mock_exec.call_args[0][1]
        assert "myvideo_converted.avi" in str(output_path)

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    def test_success_message_format(self, mock_check, tmp_path):
        f = tmp_path / "clip.mp4"
        f.write_bytes(b"\x00")

        with patch.object(proc, "_execute_ffmpeg", return_value=(True, "")):
            with patch.object(Path, "exists", return_value=True):
                result = proc.convert_video([str(f)], "avi")

        assert "1/1" in result["message"]
        assert "AVI" in result["message"]

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    def test_skip_message_format(self, mock_check, tmp_path):
        f = tmp_path / "clip.mp4"
        f.write_bytes(b"\x00")
        result = proc.convert_video([str(f)], "mp4")
        assert "1 omitidos" in result["message"]

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    def test_build_command_called_with_options(self, mock_check, tmp_path):
        f = tmp_path / "clip.mp4"
        f.write_bytes(b"\x00")

        with patch.object(proc, "_build_ffmpeg_command") as mock_build:
            mock_build.return_value = ["ffmpeg"]
            with patch.object(proc, "_execute_ffmpeg", return_value=(True, "")):
                proc.convert_video([str(f)], "mp4", crf=18, preset="slow")

        mock_build.assert_called_once()
        call_opts = mock_build.call_args[0][3]
        assert call_opts["crf"] == 18
        assert call_opts["preset"] == "slow"


# ===================================================================
# get_video_info
# ===================================================================
class TestGetVideoInfo:
    """Tests for get_video_info with mocked ffprobe output."""

    SAMPLE_JSON = json.dumps({
        "streams": [
            {
                "codec_type": "video",
                "codec_name": "h264",
                "width": 1920,
                "height": 1080,
                "r_frame_rate": "30/1",
            },
            {
                "codec_type": "audio",
                "codec_name": "aac",
                "bit_rate": "128000",
            },
        ],
        "format": {
            "format_name": "mov,mp4,m4a,3gp",
            "duration": "120.5",
            "size": "104857600",
            "bit_rate": "6960000",
        },
    })

    @patch(f"{_MOD}.check_ffmpeg", return_value=False)
    def test_no_ffmpeg(self, mock_check):
        result = proc.get_video_info("/tmp/video.mp4")
        assert result["success"] is False
        assert "FFmpeg" in result["error"]

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    def test_file_not_found(self, mock_check):
        result = proc.get_video_info("/tmp/nonexistent.mp4")
        assert result["success"] is False
        assert "no encontrado" in result["error"].lower() or "not found" in result["error"].lower()

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    @patch(f"{_MOD}.subprocess.run")
    def test_ffprobe_returns_nonzero(self, mock_run, mock_check, tmp_path):
        f = tmp_path / "video.mp4"
        f.write_bytes(b"\x00")
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
        result = proc.get_video_info(str(f))
        assert result["success"] is False
        assert "error" in result["error"].lower()

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    @patch(f"{_MOD}.subprocess.run")
    def test_valid_video_info(self, mock_run, mock_check, tmp_path):
        f = tmp_path / "test.mp4"
        f.write_bytes(b"\x00")

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=self.SAMPLE_JSON,
            stderr="",
        )

        result = proc.get_video_info(str(f))

        assert result["success"] is True
        assert result["video_codec"] == "h264"
        assert result["video_resolution"] == "1920x1080"
        assert result["video_fps"] == "30/1"
        assert result["audio_codec"] == "aac"
        assert result["format"] == "mov,mp4,m4a,3gp"
        assert result["duration"] == 120.5
        assert result["file_size"] == 104857600
        assert result["video_bitrate"] == "6960000"

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    @patch(f"{_MOD}.subprocess.run")
    def test_video_only_no_audio(self, mock_run, mock_check, tmp_path):
        f = tmp_path / "test.mp4"
        f.write_bytes(b"\x00")

        data = {
            "streams": [{"codec_type": "video", "codec_name": "h264", "width": 1280, "height": 720, "r_frame_rate": "24/1"}],
            "format": {"format_name": "mp4", "duration": "60", "size": "5000000", "bit_rate": "3000000"},
        }
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(data), stderr="")

        result = proc.get_video_info(str(f))
        assert result["success"] is True
        assert result["audio_codec"] == "N/A"
        assert result["audio_bitrate"] == "N/A"

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    @patch(f"{_MOD}.subprocess.run")
    def test_audio_only_no_video(self, mock_run, mock_check, tmp_path):
        f = tmp_path / "test.mp4"
        f.write_bytes(b"\x00")

        data = {
            "streams": [{"codec_type": "audio", "codec_name": "aac", "bit_rate": "192000"}],
            "format": {"format_name": "mp4", "duration": "30", "size": "1000000", "bit_rate": "500000"},
        }
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(data), stderr="")

        result = proc.get_video_info(str(f))
        assert result["success"] is True
        assert result["video_codec"] == "N/A"
        assert result["video_resolution"] == "N/A"
        assert result["video_fps"] == "N/A"

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    @patch(f"{_MOD}.subprocess.run")
    def test_empty_streams(self, mock_run, mock_check, tmp_path):
        f = tmp_path / "test.mp4"
        f.write_bytes(b"\x00")

        data = {"streams": [], "format": {"format_name": "mp4", "duration": "0", "size": "0", "bit_rate": "0"}}
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(data), stderr="")

        result = proc.get_video_info(str(f))
        assert result["success"] is True
        assert result["video_codec"] == "N/A"
        assert result["audio_codec"] == "N/A"

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    @patch(f"{_MOD}.subprocess.run")
    def test_malformed_json(self, mock_run, mock_check, tmp_path):
        f = tmp_path / "test.mp4"
        f.write_bytes(b"\x00")
        mock_run.return_value = MagicMock(returncode=0, stdout="not json at all", stderr="")

        result = proc.get_video_info(str(f))
        assert result["success"] is False
        assert "error" in result

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    @patch(f"{_MOD}.subprocess.run")
    def test_command_uses_ffprobe(self, mock_run, mock_check, tmp_path):
        f = tmp_path / "test.mp4"
        f.write_bytes(b"\x00")
        mock_run.return_value = MagicMock(returncode=0, stdout="{}", stderr="")

        proc.get_video_info(str(f))

        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "ffprobe" or "ffprobe" in cmd[0]
        assert "-show_format" in cmd
        assert "-show_streams" in cmd
        assert "-print_format" in cmd
        assert "json" in cmd

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    @patch(f"{_MOD}.subprocess.run")
    def test_file_name_in_result(self, mock_run, mock_check, tmp_path):
        f = tmp_path / "my_video.mp4"
        f.write_bytes(b"\x00")
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"streams": [], "format": {"format_name": "mp4", "duration": "0", "size": "0"}}),
            stderr="",
        )
        result = proc.get_video_info(str(f))
        assert result["file_name"] == "my_video.mp4"

    @patch(f"{_MOD}.check_ffmpeg", return_value=True)
    @patch(f"{_MOD}.subprocess.run")
    def test_timeout_handling(self, mock_run, mock_check, tmp_path):
        f = tmp_path / "test.mp4"
        f.write_bytes(b"\x00")
        mock_run.side_effect = OSError("timed out")
        result = proc.get_video_info(str(f))
        assert result["success"] is False
        assert "timed out" in result["error"]


# ===================================================================
# Codec mappings (unit tests for the frozen dicts)
# ===================================================================
class TestCodecMappings:
    """Verify the frozen codec dictionaries are correct."""

    def test_video_codecs_keys(self):
        codecs = proc._get_video_codecs()
        assert set(codecs.keys()) == {"mp4", "avi", "mkv", "mov"}

    def test_audio_codecs_keys(self):
        codecs = proc._get_audio_codecs()
        assert set(codecs.keys()) == {"mp4", "avi", "mkv", "mov"}

    def test_mp4_codecs(self):
        assert proc._get_video_codecs()["mp4"] == "libx264"
        assert proc._get_audio_codecs()["mp4"] == "aac"

    def test_avi_codecs(self):
        assert proc._get_video_codecs()["avi"] == "mpeg4"
        assert proc._get_audio_codecs()["avi"] == "mp3"

    def test_codecs_are_immutable(self):
        """MappingProxyType prevents modification."""
        with pytest.raises(TypeError):
            proc._get_video_codecs()["mp4"] = "changed"
