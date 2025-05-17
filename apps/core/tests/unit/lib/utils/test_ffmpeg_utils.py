"""
Unit tests for the FfmpegUtils class.
"""

import json
import os
import subprocess
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from apps.core.lib.utils.ffmpeg_utils import FfmpegUtils


class TestFfmpegUtils:
    """Test cases for the FfmpegUtils class."""

    @patch("subprocess.run")
    def test_extract_audio_sync_success(self, mock_run):
        """Test successful audio extraction from a video file."""
        # Set up the mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        # Call the method
        FfmpegUtils.extract_audio_sync("test_video.mp4", "output_audio.wav")

        # Verify subprocess.run was called with correct arguments
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args

        # Check the command list
        cmd = args[0]
        assert cmd[0] == "ffmpeg"
        assert "-i" in cmd
        assert "test_video.mp4" in cmd
        assert "output_audio.wav" in cmd

        # Check that stdout and stderr are captured
        assert kwargs["stdout"] == subprocess.PIPE
        assert kwargs["stderr"] == subprocess.PIPE

    @patch("subprocess.run")
    def test_extract_audio_sync_failure(self, mock_run):
        """Test handling of ffmpeg failure during audio extraction."""
        # Set up the mock for failure
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = b"ffmpeg error message"
        mock_run.return_value = mock_result

        # Call the method and expect an exception
        with pytest.raises(RuntimeError) as excinfo:
            FfmpegUtils.extract_audio_sync("test_video.mp4", "output_audio.wav")

        # Verify the error message
        assert "FFmpeg audio extraction failed" in str(excinfo.value)
        assert "ffmpeg error message" in str(excinfo.value)

    @patch("subprocess.run")
    def test_extract_frame_sync_success(self, mock_run):
        """Test successful frame extraction from a video file."""
        # Set up the mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        # Call the method
        FfmpegUtils.extract_frame_sync("test_video.mp4", 10.5, "output_frame.jpg")

        # Verify subprocess.run was called with correct arguments
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args

        # Check the command list
        cmd = args[0]
        assert cmd[0] == "ffmpeg"
        assert "-ss" in cmd
        assert "10.5" in cmd
        assert "-i" in cmd
        assert "test_video.mp4" in cmd
        assert "output_frame.jpg" in cmd

        # Check that stdout and stderr are captured
        assert kwargs["stdout"] == subprocess.PIPE
        assert kwargs["stderr"] == subprocess.PIPE

    @patch("subprocess.run")
    def test_extract_frame_sync_failure(self, mock_run):
        """Test handling of ffmpeg failure during frame extraction."""
        # Set up the mock for failure
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = b"ffmpeg error message"
        mock_run.return_value = mock_result

        # Call the method and expect an exception
        with pytest.raises(RuntimeError) as excinfo:
            FfmpegUtils.extract_frame_sync("test_video.mp4", 10.5, "output_frame.jpg")

        # Verify the error message
        assert "FFmpeg frame extraction failed" in str(excinfo.value)
        assert "ffmpeg error message" in str(excinfo.value)

    @patch("subprocess.run")
    def test_get_video_metadata_sync_success(self, mock_run):
        """Test successful metadata extraction from a video file."""
        # Sample ffprobe JSON output
        sample_metadata = {
            "streams": [
                {
                    "codec_type": "video",
                    "width": 1920,
                    "height": 1080,
                    "duration": "60.000000",
                    "r_frame_rate": "30/1",
                },
                {"codec_type": "audio", "sample_rate": "44100", "channels": 2},
            ],
            "format": {
                "duration": "60.000000",
                "bit_rate": "1000000",
                "format_name": "mp4",
            },
        }

        # Set up the mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(sample_metadata).encode("utf-8")
        mock_run.return_value = mock_result

        # Call the method
        metadata = FfmpegUtils.get_video_metadata_sync("test_video.mp4")

        # Verify subprocess.run was called with correct arguments
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args

        # Check the command list
        cmd = args[0]
        assert cmd[0] == "ffprobe"
        assert "-print_format" in cmd
        assert "json" in cmd
        assert "test_video.mp4" in cmd

        # Check that stdout and stderr are captured
        assert kwargs["stdout"] == subprocess.PIPE
        assert kwargs["stderr"] == subprocess.PIPE

        # Verify the parsed metadata
        assert metadata == sample_metadata
        assert metadata["streams"][0]["width"] == 1920
        assert metadata["format"]["duration"] == "60.000000"

    @patch("subprocess.run")
    def test_get_video_metadata_sync_failure(self, mock_run):
        """Test handling of ffprobe failure during metadata extraction."""
        # Set up the mock for failure
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = b"ffprobe error message"
        mock_run.return_value = mock_result

        # Call the method and expect an exception
        with pytest.raises(RuntimeError) as excinfo:
            FfmpegUtils.get_video_metadata_sync("test_video.mp4")

        # Verify the error message
        assert "ffprobe metadata extraction failed" in str(excinfo.value)
        assert "ffprobe error message" in str(excinfo.value)

    def test_real_command_structure(self):
        """
        Test the actual structure of commands without executing them.
        This verifies the command construction logic without mocking.
        """
        import subprocess

        # Extract audio command
        with patch("subprocess.run") as mock_run:
            FfmpegUtils.extract_audio_sync("video.mp4", "audio.wav")
            cmd = mock_run.call_args[0][0]
            assert cmd[0:3] == ["ffmpeg", "-y", "-i"]
            assert "-vn" in cmd
            assert "audio.wav" in cmd

        # Extract frame command
        with patch("subprocess.run") as mock_run:
            FfmpegUtils.extract_frame_sync("video.mp4", 5.5, "frame.jpg")
            cmd = mock_run.call_args[0][0]
            assert cmd[0:3] == ["ffmpeg", "-y", "-ss"]
            assert cmd[3] == "5.5"
            assert "-frames:v" in cmd
            assert "1" in cmd
            assert "frame.jpg" in cmd

        # Get metadata command
        with patch("subprocess.run") as mock_run:
            FfmpegUtils.get_video_metadata_sync("video.mp4")
            cmd = mock_run.call_args[0][0]
            assert cmd[0:3] == ["ffprobe", "-v", "error"]
            assert "-show_entries" in cmd
            assert "format:stream" in cmd
            assert "-print_format" in cmd
            assert "json" in cmd
