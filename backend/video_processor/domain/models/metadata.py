"""
Domain model for video metadata.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class VideoMetadata:
    """
    Metadata for a video.

    Contains all information about the video content and characteristics
    that can be used for publishing and organization.
    """

    title: str
    description: Optional[str] = None
    keywords: Optional[str] = None
    category_id: str = "22"  # Default to "People & Blogs"
    duration_seconds: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    channel: str = "daily"  # 'daily' or 'main'

    # Additional fields as specified in requirements
    tags: List[str] = None
    show_notes: Optional[str] = None
    thumbnail_url: Optional[str] = None
    transcript: Optional[str] = None
    chapters: List[Dict[str, str]] = None

    def __post_init__(self):
        """Initialize default values for collections."""
        if self.tags is None:
            self.tags = []
        if self.chapters is None:
            self.chapters = []

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "title": self.title,
            "description": self.description,
            "keywords": self.keywords,
            "category_id": self.category_id,
            "duration_seconds": self.duration_seconds,
            "width": self.width,
            "height": self.height,
            "channel": self.channel,
            "tags": self.tags,
            "show_notes": self.show_notes,
            "thumbnail_url": self.thumbnail_url,
            "transcript": self.transcript,
            "chapters": self.chapters,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "VideoMetadata":
        """Create from dictionary."""
        return cls(
            title=data.get("title", ""),
            description=data.get("description"),
            keywords=data.get("keywords"),
            category_id=data.get("category_id", "22"),
            duration_seconds=data.get("duration_seconds"),
            width=data.get("width"),
            height=data.get("height"),
            channel=data.get("channel", "daily"),
            tags=data.get("tags", []),
            show_notes=data.get("show_notes"),
            thumbnail_url=data.get("thumbnail_url"),
            transcript=data.get("transcript"),
            chapters=data.get("chapters", []),
        )
