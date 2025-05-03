"""
Domain model for video entity.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Tuple


@dataclass
class Video:
    """
    Video entity representing a video file.

    Contains information about the video file itself, such as its location,
    format, resolution, and other technical properties.
    """

    id: str
    file_path: str
    file_name: str
    file_size: Optional[int] = None
    file_format: Optional[str] = None
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: datetime = None
    bucket_name: Optional[str] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.created_at is None:
            self.created_at = datetime.now()

    @property
    def resolution(self) -> Optional[Tuple[int, int]]:
        """Get video resolution as width x height tuple."""
        if self.width is not None and self.height is not None:
            return (self.width, self.height)
        return None

    def get_thumbnail_time(self) -> float:
        """
        Calculate an ideal time for thumbnails.

        By default, this is 20% into the video duration, which often
        captures the subject after intro but before detailed content.
        """
        if self.duration:
            return max(min(self.duration * 0.2, self.duration - 1), 0)
        return 0

    def get_file_extension(self) -> str:
        """Extract file extension from file path."""
        if "." in self.file_name:
            return self.file_name.rsplit(".", 1)[1].lower()
        return ""

    def is_valid_video(self) -> bool:
        """
        Check if this is a valid video file.

        Basic validation based on supported formats and file existence.
        """
        valid_extensions = ["mp4", "mov", "avi", "mkv", "webm"]
        return self.get_file_extension() in valid_extensions

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "file_format": self.file_format,
            "duration": self.duration,
            "width": self.width,
            "height": self.height,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "bucket_name": self.bucket_name,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Video":
        """Create from dictionary."""
        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])

        return cls(
            id=data["id"],
            file_path=data["file_path"],
            file_name=data["file_name"],
            file_size=data.get("file_size"),
            file_format=data.get("file_format"),
            duration=data.get("duration"),
            width=data.get("width"),
            height=data.get("height"),
            created_at=created_at,
            bucket_name=data.get("bucket_name"),
        )
