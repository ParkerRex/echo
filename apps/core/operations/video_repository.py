"""
Repository for VideoModel data access operations.

This module provides a repository class implementing the repository pattern for
VideoModel entities. It abstracts database access operations, providing methods
for creating and retrieving video records. The repository focuses solely on data
access with no business logic, accepting a SQLAlchemy Session for each operation.

Usage:
    from sqlalchemy.orm import Session
    from apps.core.operations.video_repository import VideoRepository

    # Create a new video
    video_repo = VideoRepository()
    new_video = video_repo.create(
        db=db_session,
        uploader_user_id="user123",
        original_filename="video.mp4",
        storage_path="uploads/video.mp4",
        content_type="video/mp4",
        size_bytes=1024000
    )

    # Get a video by ID
    video = video_repo.get_by_id(db=db_session, video_id=1)
"""

from typing import Optional

from sqlalchemy.orm import Session

from apps.core.models.video_model import VideoModel


class VideoRepository:
    """
    Repository for VideoModel data access.
    """

    @staticmethod
    def create(
        db: Session,
        uploader_user_id: str,
        original_filename: str,
        storage_path: str,
        content_type: str,
        size_bytes: int,
    ) -> VideoModel:
        """
        Create and persist a new VideoModel.

        Args:
            db (Session): SQLAlchemy session.
            uploader_user_id (str): Supabase Auth user ID.
            original_filename (str): Original filename.
            storage_path (str): Path in storage backend.
            content_type (str): MIME type.
            size_bytes (int): File size in bytes.

        Returns:
            VideoModel: The created video model.
        """
        video = VideoModel(
            uploader_user_id=uploader_user_id,
            original_filename=original_filename,
            storage_path=storage_path,
            content_type=content_type,
            size_bytes=size_bytes,
        )
        db.add(video)
        db.flush()  # Assigns ID
        return video

    @staticmethod
    def get_by_id(db: Session, video_id: int) -> Optional[VideoModel]:
        """
        Retrieve a VideoModel by its ID.

        Args:
            db (Session): SQLAlchemy session.
            video_id (int): Video ID.

        Returns:
            Optional[VideoModel]: The video model, or None if not found.
        """
        return db.query(VideoModel).filter(VideoModel.id == video_id).first()
