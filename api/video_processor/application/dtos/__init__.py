"""
DTOs (Data Transfer Objects) package.

Contains the DTOs used for transferring data between layers of the application,
particularly for API interactions.
"""

from video_processor.application.dtos.job_dto import JobDTO
from video_processor.application.dtos.metadata_dto import MetadataDTO
from video_processor.application.dtos.video_dto import VideoDTO

__all__ = [
    "JobDTO",
    "MetadataDTO",
    "VideoDTO",
]
