"""
FFmpeg utility functions for media file operations.

This module provides wrapper functions for common FFmpeg operations used in the
video processing pipeline, such as audio extraction, frame extraction, and
metadata retrieval.
"""

import json
import logging
import os
import subprocess
from typing import Any, Dict, Optional, Tuple

from video_processor.domain.exceptions import InvalidVideoError

# Configure logger
logger = logging.getLogger(__name__)


def run_ffmpeg_command(command: list, check: bool = True) -> Tuple[str, str]:
    """
    Run an FFmpeg command and return stdout and stderr.

    Args:
        command: List of command arguments (including the ffmpeg executable)
        check: Whether to check the return code and raise an exception on failure

    Returns:
        Tuple of (stdout, stderr) as strings

    Raises:
        RuntimeError: If check=True and the command fails
    """
    logger.debug(f"Running FFmpeg command: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=check,
        )
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg command failed: {e.stderr}")
        if check:
            raise RuntimeError(f"FFmpeg command failed: {e.stderr}") from e
        return e.stdout, e.stderr


def extract_audio(video_path: str, output_path: str, format: str = "wav") -> str:
    """
    Extract audio from a video file.

    Args:
        video_path: Path to the input video file
        output_path: Path where the audio file should be saved
        format: Audio format (default: wav)

    Returns:
        Path to the extracted audio file

    Raises:
        InvalidVideoError: If the video file is invalid or FFmpeg fails
    """
    if not os.path.exists(video_path):
        raise InvalidVideoError(f"Video file not found: {video_path}")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    logger.info(f"Extracting audio from {video_path} to {output_path}")

    try:
        # Construct FFmpeg command for audio extraction
        command = [
            "ffmpeg",
            "-i",
            video_path,
            "-vn",  # Disable video
            "-acodec",
            "pcm_s16le",  # Audio codec for WAV
            "-ar",
            "44100",  # Audio sample rate
            "-ac",
            "2",  # Audio channels (stereo)
            "-y",  # Overwrite output file if it exists
            output_path,
        ]

        # Run the command
        stdout, stderr = run_ffmpeg_command(command)

        if not os.path.exists(output_path):
            raise InvalidVideoError("Failed to extract audio: Output file not created")

        logger.info(f"Audio extracted successfully to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error extracting audio: {str(e)}")
        raise InvalidVideoError(f"Failed to extract audio: {str(e)}")


def extract_frame(video_path: str, time: float, output_path: str) -> str:
    """
    Extract a single frame from a video at a specific timestamp.

    Args:
        video_path: Path to the input video file
        time: Timestamp in seconds for the frame to extract
        output_path: Path where the frame image should be saved

    Returns:
        Path to the extracted frame image

    Raises:
        InvalidVideoError: If the video file is invalid or FFmpeg fails
    """
    if not os.path.exists(video_path):
        raise InvalidVideoError(f"Video file not found: {video_path}")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    logger.info(f"Extracting frame from {video_path} at {time}s to {output_path}")

    try:
        # Format time as HH:MM:SS.mmm
        time_str = str(time)

        # Construct FFmpeg command for frame extraction
        command = [
            "ffmpeg",
            "-ss",
            time_str,  # Seek to time position
            "-i",
            video_path,
            "-vframes",
            "1",  # Extract one frame
            "-q:v",
            "2",  # Quality level (lower is better, 2-31)
            "-y",  # Overwrite output file if it exists
            output_path,
        ]

        # Run the command
        stdout, stderr = run_ffmpeg_command(command)

        if not os.path.exists(output_path):
            raise InvalidVideoError("Failed to extract frame: Output file not created")

        logger.info(f"Frame extracted successfully to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error extracting frame: {str(e)}")
        raise InvalidVideoError(f"Failed to extract frame: {str(e)}")


def get_video_metadata(video_path: str) -> Dict[str, Any]:
    """
    Extract metadata from a video file using FFprobe.

    Args:
        video_path: Path to the video file

    Returns:
        Dictionary containing video metadata (duration, resolution, format, etc.)

    Raises:
        InvalidVideoError: If the video file is invalid or FFprobe fails
    """
    if not os.path.exists(video_path):
        raise InvalidVideoError(f"Video file not found: {video_path}")

    logger.info(f"Extracting metadata from {video_path}")

    try:
        # Construct FFprobe command to get video metadata in JSON format
        command = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            video_path,
        ]

        # Run the command
        stdout, stderr = run_ffmpeg_command(command)

        if not stdout:
            raise InvalidVideoError(
                "Failed to extract metadata: No output from FFprobe"
            )

        # Parse JSON output
        probe_data = json.loads(stdout)

        # Extract relevant metadata
        metadata = {}

        # Extract format information
        if "format" in probe_data:
            format_data = probe_data["format"]
            metadata["format"] = format_data.get("format_name", "unknown")

            # Duration in seconds
            if "duration" in format_data:
                metadata["duration"] = float(format_data["duration"])

            # File size in bytes
            if "size" in format_data:
                metadata["size"] = int(format_data["size"])

        # Extract video stream information
        video_stream = None
        audio_stream = None

        if "streams" in probe_data:
            for stream in probe_data["streams"]:
                if stream.get("codec_type") == "video" and not video_stream:
                    video_stream = stream
                elif stream.get("codec_type") == "audio" and not audio_stream:
                    audio_stream = stream

        if video_stream:
            # Resolution
            width = int(video_stream.get("width", 0))
            height = int(video_stream.get("height", 0))
            metadata["resolution"] = (width, height)

            # Frame rate
            if "r_frame_rate" in video_stream:
                fps_parts = video_stream["r_frame_rate"].split("/")
                if len(fps_parts) == 2 and int(fps_parts[1]) != 0:
                    metadata["fps"] = float(int(fps_parts[0]) / int(fps_parts[1]))

            # Video codec
            metadata["video_codec"] = video_stream.get("codec_name", "unknown")

        if audio_stream:
            # Audio codec
            metadata["audio_codec"] = audio_stream.get("codec_name", "unknown")

            # Audio sample rate
            if "sample_rate" in audio_stream:
                metadata["audio_sample_rate"] = int(audio_stream["sample_rate"])

            # Audio channels
            if "channels" in audio_stream:
                metadata["audio_channels"] = int(audio_stream["channels"])

        logger.info(f"Metadata extracted successfully: {metadata}")
        return metadata

    except Exception as e:
        logger.error(f"Error extracting metadata: {str(e)}")
        raise InvalidVideoError(f"Failed to extract metadata: {str(e)}")


def compress_video(
    input_path: str, output_path: str, target_size_mb: Optional[int] = None
) -> str:
    """
    Compress a video file to a smaller size.

    Args:
        input_path: Path to the input video file
        output_path: Path where the compressed video should be saved
        target_size_mb: Target file size in MB (if None, uses default compression)

    Returns:
        Path to the compressed video

    Raises:
        InvalidVideoError: If the video file is invalid or FFmpeg fails
    """
    if not os.path.exists(input_path):
        raise InvalidVideoError(f"Video file not found: {input_path}")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    logger.info(f"Compressing video {input_path} to {output_path}")

    try:
        # Get input video metadata
        metadata = get_video_metadata(input_path)

        # Calculate bitrate if target size is specified
        bitrate_args = []
        if target_size_mb:
            # Calculate target bitrate in kbps
            # Formula: (target_size_bytes * 8) / (duration_seconds * 1000)
            duration = metadata.get("duration", 0)
            if duration > 0:
                target_size_bits = target_size_mb * 8 * 1024 * 1024
                target_bitrate = int(target_size_bits / (duration * 1000))
                bitrate_args = ["-b:v", f"{target_bitrate}k"]
                logger.info(
                    f"Targeting bitrate of {target_bitrate} kbps for {target_size_mb}MB output"
                )

        # Construct FFmpeg command for video compression
        command = [
            "ffmpeg",
            "-i",
            input_path,
            "-c:v",
            "libx264",  # H.264 codec
            "-preset",
            "medium",  # Compression preset (slower = better compression)
            "-c:a",
            "aac",  # AAC audio codec
            "-b:a",
            "128k",  # Audio bitrate
        ]

        # Add bitrate arguments if target size specified
        if bitrate_args:
            command.extend(bitrate_args)
        else:
            # Default to CRF compression (constant quality)
            command.extend(["-crf", "23"])  # 0-51, lower is better quality

        # Add output file
        command.extend(["-y", output_path])

        # Run the command
        stdout, stderr = run_ffmpeg_command(command)

        if not os.path.exists(output_path):
            raise InvalidVideoError("Failed to compress video: Output file not created")

        logger.info(f"Video compressed successfully to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error compressing video: {str(e)}")
        raise InvalidVideoError(f"Failed to compress video: {str(e)}")
