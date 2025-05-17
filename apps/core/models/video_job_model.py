"""
SQLAlchemy model for video processing jobs.

This module defines the VideoJobModel class, which represents a video processing job
in the database. Each job is associated with a specific video and tracks the
processing status, stages, and any error information.

Usage:
    from apps.core.models.video_job_model import VideoJobModel
    from apps.core.models.enums import ProcessingStatus

    # Create a new video processing job
    new_job = VideoJobModel(
        video_id=1,
        status=ProcessingStatus.PENDING,
        processing_stages={"transcription": False, "metadata": False}
    )

    # Add to database
    db.add(new_job)
    db.commit()

    # Update job status
    new_job.status = ProcessingStatus.PROCESSING
    new_job.processing_stages["transcription"] = True
    db.commit()
"""

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from apps.core.lib.database.connection import Base
from apps.core.models.enums import ProcessingStatus

# Remove direct import causing circular dependency
# from apps.core.models.video_metadata_model import VideoMetadataModel


class VideoJobModel(Base):
    """
    SQLAlchemy model representing a video processing job.

    This model tracks the status and progress of a video processing task, including
    which processing stages have been completed and any errors that occurred.
    It maintains relationships with both the source video and the generated metadata.

    Attributes:
        id (int): Primary key, auto-incrementing identifier.
        video_id (int): Foreign key referencing the associated video.
        status (ProcessingStatus): Current status of the job (PENDING, PROCESSING, COMPLETED, FAILED).
        processing_stages (JSON): Dictionary tracking completion of various processing steps.
        error_message (str): Error message if processing failed, otherwise None.
        created_at (datetime): Timestamp when the job was created.
        updated_at (datetime): Timestamp when the job was last updated.
        video (relationship): Many-to-one relationship with VideoModel.
        video_metadata (relationship): One-to-one relationship with VideoMetadataModel.
    """

    __tablename__ = "video_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    status = Column(
        Enum(ProcessingStatus), default=ProcessingStatus.PENDING, nullable=False
    )
    processing_stages = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Define relationships
    video = relationship("VideoModel", back_populates="jobs")
    # Use string reference instead of direct class reference
    video_metadata = relationship(
        "VideoMetadataModel",
        back_populates="job",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<VideoJob(id={self.id}, status={self.status})>"
