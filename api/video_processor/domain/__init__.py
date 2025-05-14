"""
Domain package for the video processing application.

Contains the core business logic and entities independent of any
external frameworks or infrastructure concerns.
"""

from video_processor.domain.models import (
    ProcessingStage,
    ProcessingStatus,
    Video,
    VideoJob,
    VideoMetadata,
)
from video_processor.domain.value_objects import (
    Chapter,
    Subtitle,
    SubtitleCollection,
    TimestampedText,
    VideoFormat,
    VideoResolution,
)

__all__ = [
    # Models
    "ProcessingStage",
    "ProcessingStatus",
    "Video",
    "VideoJob",
    "VideoMetadata",
    # Value objects
    "Chapter",
    "Subtitle",
    "SubtitleCollection",
    "TimestampedText",
    "VideoFormat",
    "VideoResolution",
]
