"""
Application package for the video processing pipeline.

Contains the application services and use cases that implement the business logic
of the application, independent of specific infrastructure concerns.
"""

from video_processor.application.dtos import JobDTO, MetadataDTO, VideoDTO
from video_processor.application.interfaces import (
    AIServiceInterface,
    PublishingInterface,
    StorageInterface,
)

__all__ = [
    # DTOs
    "JobDTO",
    "MetadataDTO",
    "VideoDTO",
    # Interfaces
    "AIServiceInterface",
    "PublishingInterface",
    "StorageInterface",
]
