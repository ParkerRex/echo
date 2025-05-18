"""
Repository for VideoJobModel data access operations.

This module provides a repository class implementing the repository pattern for
VideoJobModel entities. It abstracts database operations for creating, retrieving,
and updating video processing jobs. The repository handles the persistence details
while keeping business logic separate, accepting a SQLAlchemy Session for all operations.

Usage:
    from sqlalchemy.orm import Session
    from apps.core.models.enums import ProcessingStatus
    from apps.core.operations.video_job_repository import VideoJobRepository

    # Create a new video processing job
    job_repo = VideoJobRepository()
    new_job = job_repo.create(
        db=db_session,
        video_id=1,
        status=ProcessingStatus.PENDING,
        processing_stages={"transcription": False}
    )

    # Update job status
    updated_job = job_repo.update_status(
        db=db_session,
        job_id=new_job.id,
        status=ProcessingStatus.PROCESSING
    )

    # Record a processing stage
    job_repo.add_processing_stage(
        db=db_session,
        job_id=new_job.id,
        stage="transcription_complete"
    )
"""

from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload

from apps.core.models.enums import ProcessingStatus
from apps.core.models.video_job_model import VideoJobModel
from apps.core.models.video_model import VideoModel


class VideoJobRepository:
    """
    Repository for VideoJobModel data access.
    """

    @staticmethod
    async def create(
        db: AsyncSession,
        video_id: int,
        status: ProcessingStatus = ProcessingStatus.PENDING,
        processing_stages: Optional[Any] = None,
        error_message: Optional[str] = None,
    ) -> VideoJobModel:
        """
        Create and persist a new VideoJobModel.

        Args:
            db (AsyncSession): SQLAlchemy async session.
            video_id (int): Associated video ID.
            status (ProcessingStatus): Initial processing status.
            processing_stages (Optional[Any]): Initial processing stages (JSON/text).
            error_message (Optional[str]): Initial error message.

        Returns:
            VideoJobModel: The created job model.
        """
        job = VideoJobModel(
            video_id=video_id,
            status=status,
            processing_stages=processing_stages,
            error_message=error_message,
        )
        db.add(job)
        await db.flush()
        return job

    @staticmethod
    async def get_by_id(db: AsyncSession, job_id: int) -> Optional[VideoJobModel]:
        """
        Retrieve a VideoJobModel by its ID.

        Args:
            db (AsyncSession): SQLAlchemy async session.
            job_id (int): Job ID.

        Returns:
            Optional[VideoJobModel]: The job model, or None if not found.
        """
        result = await db.execute(
            select(VideoJobModel).filter(VideoJobModel.id == job_id)
        )
        return result.scalars().first()

    @staticmethod
    async def update_status(
        db: AsyncSession,
        job_id: int,
        status: ProcessingStatus,
        error_message: Optional[str] = None,
    ) -> Optional[VideoJobModel]:
        """
        Update the status (and optionally error message) of a VideoJobModel.

        Args:
            db (AsyncSession): SQLAlchemy async session.
            job_id (int): Job ID.
            status (ProcessingStatus): New status.
            error_message (Optional[str]): Error message.

        Returns:
            Optional[VideoJobModel]: The updated job model, or None if not found.
        """
        result = await db.execute(
            select(VideoJobModel).filter(VideoJobModel.id == job_id)
        )
        job = result.scalars().first()
        if job is not None:
            job.status = status  # type: ignore
            if error_message is not None:
                job.error_message = error_message  # type: ignore
            await db.flush()
        return job

    @staticmethod
    async def add_processing_stage(
        db: AsyncSession, job_id: int, stage: str
    ) -> Optional[VideoJobModel]:
        """
        Add a processing stage to the job's processing_stages list (assumes JSON/text).

        Args:
            db (AsyncSession): SQLAlchemy async session.
            job_id (int): Job ID.
            stage (str): Stage to add.

        Returns:
            Optional[VideoJobModel]: The updated job model, or None if not found.
        """
        result = await db.execute(
            select(VideoJobModel).filter(VideoJobModel.id == job_id)
        )
        job = result.scalars().first()
        if job is not None:
            # Explicitly handle None to avoid potential issues with linter and SQLAlchemy attributes
            current_processing_stages = job.processing_stages
            if current_processing_stages is None:
                stages = []
            else:
                stages = current_processing_stages

            if isinstance(stages, str):
                import json

                try:
                    stages = json.loads(stages)
                except Exception:
                    stages = []
            if not isinstance(stages, list):
                stages = []
            stages.append(stage)
            job.processing_stages = stages  # type: ignore
            await db.flush()
        return job

    @staticmethod
    async def get_by_user_id_and_statuses(
        db: AsyncSession,
        user_id: str,
        statuses: Optional[List[ProcessingStatus]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[VideoJobModel]:
        """
        Retrieve VideoJobModels for a specific user, filtered by statuses, with pagination.

        Args:
            db (AsyncSession): SQLAlchemy async session.
            user_id (str): The uploader_user_id (Supabase string UUID) from VideoModel.
            statuses (Optional[List[ProcessingStatus]]): List of statuses to filter by.
                                                      If None or empty, default statuses might be applied
                                                      (e.g., PENDING, PROCESSING) or no status filter.
            limit (int): Maximum number of jobs to return.
            offset (int): Number of jobs to skip for pagination.

        Returns:
            List[VideoJobModel]: A list of job models.
        """
        stmt = (
            select(VideoJobModel)
            .join(VideoModel, VideoJobModel.video_id == VideoModel.id)
            .filter(VideoModel.uploader_user_id == user_id)
        )

        if statuses:
            stmt = stmt.filter(VideoJobModel.status.in_(statuses))

        # Eager load related video and metadata to prevent N+1 queries if accessed later
        # This is useful if the VideoJobSchema nests VideoSchema and VideoMetadataSchema
        stmt = stmt.options(
            joinedload(VideoJobModel.video), joinedload(VideoJobModel.video_metadata)
        )

        stmt = (
            stmt.order_by(VideoJobModel.created_at.desc()).offset(offset).limit(limit)
        )

        result = await db.execute(stmt)
        return list(result.scalars().all())
