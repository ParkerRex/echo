"""
Domain enums for video processing status and stages.
"""

from enum import Enum, auto


class ProcessingStage(Enum):
    """Stages of video processing."""

    DOWNLOAD = auto()
    EXTRACT_AUDIO = auto()
    GENERATE_TRANSCRIPT = auto()
    GENERATE_SUBTITLES = auto()
    GENERATE_SHOWNOTES = auto()
    GENERATE_CHAPTERS = auto()
    GENERATE_TITLES = auto()
    UPLOAD_OUTPUTS = auto()
    UPLOAD_TO_YOUTUBE = auto()
    COMPLETE = auto()


class ProcessingStatus(Enum):
    """Status of job processing."""

    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    PARTIAL = auto()  # Some stages completed but not all
