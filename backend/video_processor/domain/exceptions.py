"""
Domain-specific exceptions for the video processing application.
"""


class VideoProcessingError(Exception):
    """Base exception for all domain-related errors in the video processor."""

    pass


class InvalidVideoError(VideoProcessingError):
    """Raised when a video file is invalid or corrupted."""

    pass


class MetadataGenerationError(VideoProcessingError):
    """Raised when metadata generation fails."""

    pass


class PublishingError(VideoProcessingError):
    """Raised when video publishing to platforms like YouTube fails."""

    pass


class StorageError(VideoProcessingError):
    """Raised when file storage operations fail."""

    pass


class TranscriptionError(VideoProcessingError):
    """Raised when transcript generation fails."""

    pass


class JobNotFoundError(VideoProcessingError):
    """Raised when a job with the specified ID cannot be found."""

    pass


class MessagingError(VideoProcessingError):
    """Raised when messaging operations fail."""

    pass
