"""
FfmpegUtils: Synchronous FFmpeg utility functions for video processing.

- Provides methods for audio extraction, frame extraction, and metadata retrieval.
- Uses subprocess.run to call the ffmpeg CLI.
- Designed for use in the infrastructure/lib layer.

Directory: apps/core/lib/utils/ffmpeg_utils.py
Layer: Infrastructure/Lib
"""

import json
import subprocess
from typing import Any, Dict, cast


class FfmpegUtils:
    """
    Utility class for common FFmpeg operations.
    All methods are synchronous and use subprocess.run.
    """

    @staticmethod
    def extract_audio_sync(video_path: str, output_audio_path: str) -> None:
        """
        Extracts audio from a video file and saves it to output_audio_path.

        Args:
            video_path (str): Path to the input video file.
            output_audio_path (str): Path to save the extracted audio file.

        Raises:
            RuntimeError: If ffmpeg fails.
        """
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output files without asking
            "-i",
            video_path,
            "-vn",  # No video
            "-acodec",
            "pcm_s16le",
            "-ar",
            "44100",
            "-ac",
            "2",
            output_audio_path,
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise RuntimeError(
                f"FFmpeg audio extraction failed: {result.stderr.decode('utf-8')}"
            )

    @staticmethod
    def extract_frame_sync(
        video_path: str, timestamp_seconds: float, output_image_path: str
    ) -> None:
        """
        Extracts a single frame from a video at the specified timestamp.

        Args:
            video_path (str): Path to the input video file.
            timestamp_seconds (float): Timestamp in seconds to extract the frame.
            output_image_path (str): Path to save the extracted image.

        Raises:
            RuntimeError: If ffmpeg fails.
        """
        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            str(timestamp_seconds),
            "-i",
            video_path,
            "-frames:v",
            "1",
            output_image_path,
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise RuntimeError(
                f"FFmpeg frame extraction failed: {result.stderr.decode('utf-8')}"
            )

    @staticmethod
    def get_video_metadata_sync(video_path: str) -> Dict[str, Any]:
        """
        Retrieves metadata from a video file using ffprobe.

        Args:
            video_path (str): Path to the input video file.

        Returns:
            Dict[str, Any]: Parsed metadata dictionary.

        Raises:
            RuntimeError: If ffprobe fails.
        """
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format:stream",
            "-print_format",
            "json",
            video_path,
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise RuntimeError(
                f"ffprobe metadata extraction failed: {result.stderr.decode('utf-8')}"
            )
        return cast(Dict[str, Any], json.loads(result.stdout.decode("utf-8")))
