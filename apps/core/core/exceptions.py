"""
Custom exception classes for the Echo Core application.

This module defines various exception types used throughout the application
to provide more specific error handling for different failure scenarios.
These exceptions help with debugging and proper error reporting to clients.

Usage:
    from apps.core.core.exceptions import VideoProcessingError, FFmpegError

    try:
        # Code that might fail with FFmpeg
        process_video_with_ffmpeg(...)
    except FFmpegError as e:
        # Handle FFmpeg-specific errors
        logger.error(f"FFmpeg processing failed: {str(e)}")
        raise VideoProcessingError("Video processing failed due to FFmpeg error") from e
"""


class PublishingError(Exception):
    """Exception raised for errors during publishing operations (e.g., YouTube upload failures)."""

    pass


class MetadataGenerationError(Exception):
    """Exception raised for errors during metadata generation operations."""

    pass


class VideoProcessingError(Exception):
    """Exception raised for errors during video processing operations."""

    pass


class FFmpegError(VideoProcessingError):
    """Exception raised for errors during FFmpeg operations."""

    pass


class AINoResponseError(VideoProcessingError):
    """Exception raised when AI services fail to provide a response."""

    pass
