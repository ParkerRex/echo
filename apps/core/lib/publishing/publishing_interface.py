"""
Publishing interface for modular video processing backend.

Defines the contract for publishing operations independent of any specific
platform implementation (YouTube, Vimeo, etc.).
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class PublishingInterface(ABC):
    """
    Interface for video publishing operations.

    This interface defines the contract for all publishing adapter implementations,
    ensuring they provide the necessary methods for publishing videos to platforms.
    """

    @abstractmethod
    def upload_video(self, video_file: str, metadata: Dict) -> str:
        """
        Upload a video to the publishing platform.

        Args:
            video_file: Path to the video file
            metadata: Dictionary containing video metadata:
                      {
                          "title": str,
                          "description": str,
                          "tags": List[str],
                          "category_id": str,
                          ...
                      }

        Returns:
            The video ID on the platform

        Raises:
            PublishingError: If the upload fails
        """
        pass

    @abstractmethod
    def update_metadata(self, video_id: str, metadata: Dict) -> bool:
        """
        Update metadata for a video on the publishing platform.

        Args:
            video_id: ID of the video on the platform
            metadata: Dictionary containing video metadata to update

        Returns:
            True if the update succeeded, False otherwise

        Raises:
            PublishingError: If the update fails
        """
        pass

    @abstractmethod
    def get_upload_status(self, video_id: str) -> str:
        """
        Get the status of a video upload.

        Args:
            video_id: ID of the video on the platform

        Returns:
            Status of the upload (e.g., "uploading", "processing", "ready", "failed")

        Raises:
            PublishingError: If the status check fails
        """
        pass

    @abstractmethod
    def delete_video(self, video_id: str) -> bool:
        """
        Delete a video from the publishing platform.

        Args:
            video_id: ID of the video on the platform

        Returns:
            True if the deletion succeeded, False otherwise

        Raises:
            PublishingError: If the deletion fails
        """
        pass

    @abstractmethod
    def get_video_url(self, video_id: str) -> str:
        """
        Get the public URL for a video on the publishing platform.

        Args:
            video_id: ID of the video on the platform

        Returns:
            Public URL for the video

        Raises:
            PublishingError: If the URL retrieval fails
        """
        pass

    @abstractmethod
    def upload_caption(
        self, video_id: str, caption_file: str, language: str = "en"
    ) -> bool:
        """
        Upload a caption file for a video on the publishing platform.

        Args:
            video_id: ID of the video on the platform
            caption_file: Path to the caption file (VTT, SRT, etc.)
            language: Language code for the captions

        Returns:
            True if the upload succeeded, False otherwise

        Raises:
            PublishingError: If the caption upload fails
        """
        pass

    @abstractmethod
    def set_publishing_time(
        self, video_id: str, publish_at: Optional[str] = None
    ) -> bool:
        """
        Set the publishing time for a video on the platform.

        Args:
            video_id: ID of the video on the platform
            publish_at: ISO 8601 format datetime string when the video should be published,
                        or None to publish immediately

        Returns:
            True if the publishing time was set successfully, False otherwise

        Raises:
            PublishingError: If setting the publishing time fails
        """
        pass
