"""
Application interfaces package exports.
"""

from video_processor.application.interfaces.ai import AIServiceInterface
from video_processor.application.interfaces.publishing import PublishingInterface
from video_processor.application.interfaces.storage import StorageInterface

__all__ = [
    "AIServiceInterface",
    "PublishingInterface",
    "StorageInterface",
]
