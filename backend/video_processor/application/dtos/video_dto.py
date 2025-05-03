"""
DTO (Data Transfer Object) for Video entity.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from video_processor.domain.models.video import Video
from video_processor.domain.value_objects import VideoFormat, VideoResolution


@dataclass
class VideoDTO:
    """
    Data Transfer Object for Video entity.

    This DTO is used to transfer video data between layers of the application,
    particularly for API interactions.
    """

    id: str
    file_path: str
    file_name: str
    file_size: Optional[int] = None
    file_format: Optional[str] = None
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: Optional[str] = None
    bucket_name: Optional[str] = None

    @classmethod
    def from_entity(cls, entity: Video) -> "VideoDTO":
        """
        Create DTO from domain entity.

        Args:
            entity: Video domain entity

        Returns:
            VideoDTO object
        """
        return cls(
            id=entity.id,
            file_path=entity.file_path,
            file_name=entity.file_name,
            file_size=entity.file_size,
            file_format=entity.file_format,
            duration=entity.duration,
            width=entity.width,
            height=entity.height,
            created_at=entity.created_at.isoformat() if entity.created_at else None,
            bucket_name=entity.bucket_name,
        )

    def to_entity(self) -> Video:
        """
        Convert DTO to domain entity.

        Returns:
            Video domain entity
        """
        created_at = None
        if self.created_at:
            created_at = datetime.fromisoformat(self.created_at)

        return Video(
            id=self.id,
            file_path=self.file_path,
            file_name=self.file_name,
            file_size=self.file_size,
            file_format=self.file_format,
            duration=self.duration,
            width=self.width,
            height=self.height,
            created_at=created_at,
            bucket_name=self.bucket_name,
        )

    def to_dict(self) -> Dict:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the DTO
        """
        return {
            "id": self.id,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "file_format": self.file_format,
            "duration": self.duration,
            "width": self.width,
            "height": self.height,
            "created_at": self.created_at,
            "bucket_name": self.bucket_name,
            # Add computed properties for convenience
            "resolution": (
                f"{self.width}x{self.height}" if self.width and self.height else None
            ),
            "extension": (
                self.file_name.rsplit(".", 1)[1].lower()
                if "." in self.file_name
                else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "VideoDTO":
        """
        Create from dictionary.

        Args:
            data: Dictionary with video data

        Returns:
            VideoDTO object
        """
        return cls(
            id=data["id"],
            file_path=data["file_path"],
            file_name=data["file_name"],
            file_size=data.get("file_size"),
            file_format=data.get("file_format"),
            duration=data.get("duration"),
            width=data.get("width"),
            height=data.get("height"),
            created_at=data.get("created_at"),
            bucket_name=data.get("bucket_name"),
        )

    @property
    def resolution(self) -> Optional[VideoResolution]:
        """Get video resolution as a VideoResolution value object."""
        if self.width is not None and self.height is not None:
            return VideoResolution(width=self.width, height=self.height)
        return None

    @property
    def format(self) -> Optional[VideoFormat]:
        """Get video format as a VideoFormat value object."""
        if self.file_format:
            return VideoFormat(name=self.file_format)
        # Try to infer from file extension
        if "." in self.file_name:
            ext = self.file_name.rsplit(".", 1)[1].lower()
            return VideoFormat(name=ext)
        return None
