"""
SQLAlchemy model for storing video metadata information.

This module defines the VideoMetadataModel class which stores metadata extracted from
videos during processing, such as title, description, transcript, and technical details.
It also provides a ValueObject class (VideoMetadata) for simpler in-memory representation.

Usage:
    from apps.core.models.video_metadata_model import VideoMetadataModel, VideoMetadata

    # Create new video metadata
    metadata = VideoMetadataModel(
        job_id=123,
        title="My Awesome Video",
        description="This is a video about...",
        tags=["tutorial", "programming"],
        transcript_text="Full transcript text..."
    )

    # Add to database
    db.add(metadata)
    db.commit()

    # Using the value object for in-memory operations
    metadata_vo = VideoMetadata(
        title="My Video",
        description="Description",
        tags=["tag1", "tag2"]
    )
    metadata_json = metadata_vo.to_json()
"""

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from apps.core.lib.database.connection import Base

# Remove direct import causing circular dependency
# from apps.core.models.video_job_model import VideoJobModel


class VideoMetadataModel(Base):
    """
    SQLAlchemy model representing metadata extracted from a processed video.

    This model stores all metadata extracted or generated during video processing,
    including AI-generated title and description, transcripts, subtitles, technical
    information about the video, and generated assets like thumbnails.

    Attributes:
        id (int): Primary key, auto-incrementing identifier.
        job_id (int): Foreign key referencing the processing job that created this metadata.
        title (str): AI-generated or user-provided title for the video.
        description (str): AI-generated or user-provided description.
        tags (JSON): List of keywords/tags related to the video content.
        transcript_text (str): Full text transcript of the video's audio content.
        transcript_file_url (str): URL to the stored transcript file.
        subtitle_files_urls (JSON): Dictionary mapping subtitle format to file URLs.
        thumbnail_file_url (str): URL to the generated thumbnail image.
        extracted_video_duration_seconds (float): Duration of the video in seconds.
        extracted_video_resolution (str): Resolution of the video (e.g., "1920x1080").
        extracted_video_format (str): Format/codec of the video file.
        show_notes_text (str): AI-generated or user-provided show notes/summary.
        created_at (datetime): Timestamp when the metadata was created.
        updated_at (datetime): Timestamp when the metadata was last updated.
        job (relationship): Many-to-one relationship with VideoJobModel.
    """

    __tablename__ = "video_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("video_jobs.id"), unique=True, nullable=False)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    transcript_text = Column(Text, nullable=True)
    transcript_file_url = Column(String, nullable=True)
    subtitle_files_urls = Column(JSON, nullable=True)
    thumbnail_file_url = Column(String, nullable=True)
    extracted_video_duration_seconds = Column(Float, nullable=True)
    extracted_video_resolution = Column(String, nullable=True)
    extracted_video_format = Column(String, nullable=True)
    show_notes_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Define relationship back to job - use string reference instead of direct class reference
    job = relationship("VideoJobModel", back_populates="video_metadata")

    def __repr__(self):
        return f"<VideoMetadata(id={self.id}, job_id={self.job_id})>"


@dataclass
class VideoMetadata:
    """
    Value object representing video metadata for in-memory operations.

    This dataclass provides a lightweight representation of video metadata
    without the ORM overhead, useful for business logic operations and
    serialization/deserialization.

    Attributes:
        title (str): Title of the video, defaults to "Untitled Video".
        description (str): Description of the video content.
        tags (List[str]): List of keywords/tags related to the video.
        show_notes (str): Notes or summary about the video content.
        chapters (List[Dict[str, Any]]): Chapter markers with timestamps.
    """

    title: str = "Untitled Video"
    description: str = ""
    tags: List[str] = field(default_factory=list)
    show_notes: str = ""
    chapters: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the metadata to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the metadata.
        """
        return asdict(self)

    def to_json(self) -> str:
        """
        Convert the metadata to a JSON string.

        Returns:
            str: JSON string representation of the metadata.
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
