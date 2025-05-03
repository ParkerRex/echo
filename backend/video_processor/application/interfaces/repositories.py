"""
Repository interfaces for data access.

This module defines the interfaces for repositories that handle persistence
of domain entities such as VideoJob and Video.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional

from video_processor.domain.models.job import JobStatus, VideoJob
from video_processor.domain.models.video import Video


class RepositoryInterface(ABC):
    """Base repository interface with common CRUD operations."""

    @abstractmethod
    def get_by_id(self, id: str) -> Any:
        """Retrieve an entity by its ID."""
        pass

    @abstractmethod
    def save(self, entity: Any) -> str:
        """Save an entity and return its ID."""
        pass

    @abstractmethod
    def update(self, entity: Any) -> bool:
        """Update an existing entity and return success status."""
        pass

    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete an entity by its ID and return success status."""
        pass


class JobRepositoryInterface(RepositoryInterface):
    """Interface for VideoJob repository operations."""

    @abstractmethod
    def get_by_id(self, job_id: str) -> Optional[VideoJob]:
        """
        Retrieve a VideoJob by its ID.

        Args:
            job_id: ID of the job to retrieve

        Returns:
            VideoJob if found, None otherwise
        """
        pass

    @abstractmethod
    def save(self, job: VideoJob) -> str:
        """
        Save a new VideoJob.

        Args:
            job: VideoJob to save

        Returns:
            ID of the saved job
        """
        pass

    @abstractmethod
    def update(self, job: VideoJob) -> bool:
        """
        Update an existing VideoJob.

        Args:
            job: VideoJob to update

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def delete(self, job_id: str) -> bool:
        """
        Delete a VideoJob by its ID.

        Args:
            job_id: ID of the job to delete

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_jobs_by_status(self, status: JobStatus) -> List[VideoJob]:
        """
        Retrieve jobs with a specific status.

        Args:
            status: Status to filter by

        Returns:
            List of VideoJob with the specified status
        """
        pass

    @abstractmethod
    def get_pending_jobs(self) -> List[VideoJob]:
        """
        Retrieve all pending jobs.

        Returns:
            List of VideoJob with status PENDING
        """
        pass

    @abstractmethod
    def update_job_status(
        self, job_id: str, status: JobStatus, error: Optional[str] = None
    ) -> bool:
        """
        Update the status of a job.

        Args:
            job_id: ID of the job to update
            status: New status value
            error: Error message if status is FAILED

        Returns:
            True if successful, False otherwise
        """
        pass


class VideoRepositoryInterface(RepositoryInterface):
    """Interface for Video repository operations."""

    @abstractmethod
    def get_by_id(self, video_id: str) -> Optional[Video]:
        """
        Retrieve a Video by its ID.

        Args:
            video_id: ID of the video to retrieve

        Returns:
            Video if found, None otherwise
        """
        pass

    @abstractmethod
    def save(self, video: Video) -> str:
        """
        Save a new Video.

        Args:
            video: Video to save

        Returns:
            ID of the saved video
        """
        pass

    @abstractmethod
    def update(self, video: Video) -> bool:
        """
        Update an existing Video.

        Args:
            video: Video to update

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def delete(self, video_id: str) -> bool:
        """
        Delete a Video by its ID.

        Args:
            video_id: ID of the video to delete

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_videos_by_user(self, user_id: str) -> List[Video]:
        """
        Retrieve videos for a specific user.

        Args:
            user_id: ID of the user

        Returns:
            List of Video for the specified user
        """
        pass
