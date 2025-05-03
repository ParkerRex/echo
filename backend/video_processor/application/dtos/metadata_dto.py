"""
DTO (Data Transfer Object) for VideoMetadata entity.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from video_processor.domain.models.metadata import VideoMetadata


@dataclass
class MetadataDTO:
    """
    Data Transfer Object for VideoMetadata entity.

    This DTO is used to transfer video metadata between layers of the application,
    particularly for API interactions.
    """

    title: str
    description: Optional[str] = None
    keywords: Optional[str] = None
    category_id: str = "22"  # Default to "People & Blogs"
    duration_seconds: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    channel: str = "daily"  # 'daily' or 'main'
    tags: List[str] = field(default_factory=list)
    show_notes: Optional[str] = None
    thumbnail_url: Optional[str] = None
    transcript: Optional[str] = None
    chapters: List[Dict[str, str]] = field(default_factory=list)

    @classmethod
    def from_entity(cls, entity: VideoMetadata) -> "MetadataDTO":
        """
        Create DTO from domain entity.

        Args:
            entity: VideoMetadata domain entity

        Returns:
            MetadataDTO object
        """
        return cls(
            title=entity.title,
            description=entity.description,
            keywords=entity.keywords,
            category_id=entity.category_id,
            duration_seconds=entity.duration_seconds,
            width=entity.width,
            height=entity.height,
            channel=entity.channel,
            tags=entity.tags[:] if entity.tags else [],
            show_notes=entity.show_notes,
            thumbnail_url=entity.thumbnail_url,
            transcript=entity.transcript,
            chapters=entity.chapters[:] if entity.chapters else [],
        )

    def to_entity(self) -> VideoMetadata:
        """
        Convert DTO to domain entity.

        Returns:
            VideoMetadata domain entity
        """
        return VideoMetadata(
            title=self.title,
            description=self.description,
            keywords=self.keywords,
            category_id=self.category_id,
            duration_seconds=self.duration_seconds,
            width=self.width,
            height=self.height,
            channel=self.channel,
            tags=self.tags[:] if self.tags else [],
            show_notes=self.show_notes,
            thumbnail_url=self.thumbnail_url,
            transcript=self.transcript,
            chapters=self.chapters[:] if self.chapters else [],
        )

    def to_dict(self) -> Dict:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the DTO
        """
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
            # Add computed properties for convenience
            "has_transcript": bool(self.transcript),
            "has_chapters": bool(self.chapters),
            "tag_count": len(self.tags) if self.tags else 0,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "MetadataDTO":
        """
        Create from dictionary.

        Args:
            data: Dictionary with metadata

        Returns:
            MetadataDTO object
        """
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

    def to_youtube_metadata(self) -> Dict:
        """
        Convert to YouTube-specific metadata format.

        Returns:
            Dictionary with YouTube API compatible metadata
        """
        # Convert tags list to comma-separated keywords string if needed
        keywords = self.keywords
        if not keywords and self.tags:
            keywords = ",".join(self.tags)

        return {
            "snippet": {
                "title": self.title,
                "description": self.description or "",
                "tags": self.tags,
                "categoryId": self.category_id,
            },
            "status": {
                "privacyStatus": "private",  # Default to private for safety
                "selfDeclaredMadeForKids": False,
            },
        }
