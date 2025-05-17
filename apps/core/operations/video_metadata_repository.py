"""
video_metadata_repository.py: Repository for VideoMetadataModel data access.

- Provides methods for creating/updating and retrieving VideoMetadataModel instances.
- Accepts SQLAlchemy Session as the first argument.
- No business logic; data access only.

Directory: apps/core/operations/video_metadata_repository.py
Layer: Operations
"""

from typing import Any, Optional

from sqlalchemy.orm import Session

from apps.core.models.video_metadata_model import VideoMetadataModel


class VideoMetadataRepository:
    """
    Repository for VideoMetadataModel data access.
    """

    @staticmethod
    def create_or_update(db: Session, job_id: int, **kwargs: Any) -> VideoMetadataModel:
        """
        Create or update a VideoMetadataModel for a given job_id.

        Args:
            db (Session): SQLAlchemy session.
            job_id (int): Associated job ID.
            **kwargs: Fields to update or set.

        Returns:
            VideoMetadataModel: The created or updated metadata model.
        """
        metadata = (
            db.query(VideoMetadataModel)
            .filter(VideoMetadataModel.job_id == job_id)
            .first()
        )
        if metadata is None:
            metadata = VideoMetadataModel(job_id=job_id, **kwargs)
            db.add(metadata)
        else:
            for key, value in kwargs.items():
                setattr(metadata, key, value)
        db.flush()
        return metadata

    @staticmethod
    def get_by_job_id(db: Session, job_id: int) -> Optional[VideoMetadataModel]:
        """
        Retrieve a VideoMetadataModel by its job_id.

        Args:
            db (Session): SQLAlchemy session.
            job_id (int): Job ID.

        Returns:
            Optional[VideoMetadataModel]: The metadata model, or None if not found.
        """
        return (
            db.query(VideoMetadataModel)
            .filter(VideoMetadataModel.job_id == job_id)
            .first()
        )
