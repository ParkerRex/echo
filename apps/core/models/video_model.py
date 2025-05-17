"""
SQLAlchemy model for storing video file information.

This module defines the VideoModel class, which represents uploaded video files
in the database. Each video is associated with an uploader user and can have
multiple related processing jobs.

Usage:
    from apps.core.models.video_model import VideoModel

    # Create a new video entry
    new_video = VideoModel(
        uploader_user_id="user123",
        original_filename="my_video.mp4",
        storage_path="uploads/user123/my_video.mp4",
        content_type="video/mp4",
        size_bytes=1024000
    )

    # Add to database
    db.add(new_video)
    db.commit()
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from apps.core.lib.database.connection import Base


class VideoModel(Base):
    """
    SQLAlchemy model representing an uploaded video file.

    This model stores information about the original video file, including its
    storage location, file metadata, and the user who uploaded it. It maintains
    relationships with processing jobs and tracks creation/update timestamps.

    Attributes:
        id (int): Primary key, auto-incrementing identifier.
        uploader_user_id (str): User ID of the person who uploaded the video.
        original_filename (str): Original filename of the uploaded video.
        storage_path (str): Path where the video is stored (GCS or local filesystem).
        content_type (str): MIME type of the video file (e.g., 'video/mp4').
        size_bytes (int): Size of the video file in bytes.
        created_at (datetime): Timestamp when the entry was created.
        updated_at (datetime): Timestamp when the entry was last updated.
        jobs (relationship): One-to-many relationship with VideoJobModel.
    """

    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uploader_user_id = Column(String, index=True, nullable=False)
    original_filename = Column(String, nullable=False)
    storage_path = Column(String, unique=True, nullable=False)
    content_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Define relationship to video jobs
    jobs = relationship(
        "VideoJobModel", back_populates="video", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Video(id={self.id}, filename={self.original_filename})>"
