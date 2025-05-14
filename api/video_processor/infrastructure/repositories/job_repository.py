"""
Firestore implementation of the JobRepositoryInterface.

This module provides a Firestore-backed implementation of the job repository
for storing and retrieving VideoJob entities.
"""

import datetime
import logging
from typing import Any, Dict, List, Optional

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from video_processor.application.interfaces.repositories import JobRepositoryInterface
from video_processor.domain.models.enums import ProcessingStatus
from video_processor.domain.models.job import VideoJob
from video_processor.domain.models.metadata import VideoMetadata
from video_processor.domain.models.video import Video

# Configure logger
logger = logging.getLogger(__name__)


class FirestoreJobRepository(JobRepositoryInterface):
    """Firestore implementation of the job repository."""

    def __init__(self, project_id: str, collection_name: str = "video_jobs"):
        """
        Initialize the Firestore job repository.

        Args:
            project_id: Google Cloud project ID
            collection_name: Firestore collection name for jobs
        """
        self._db = firestore.Client(project=project_id)
        self._collection = self._db.collection(collection_name)
        logger.info(
            f"Initialized FirestoreJobRepository with collection '{collection_name}'"
        )

    def get_by_id(self, job_id: str) -> Optional[VideoJob]:
        """
        Retrieve a VideoJob by its ID.

        Args:
            job_id: ID of the job to retrieve

        Returns:
            VideoJob if found, None otherwise
        """
        doc_ref = self._collection.document(job_id)
        doc = doc_ref.get()

        if not doc.exists:
            logger.warning(f"Job with ID {job_id} not found")
            return None

        job_data = doc.to_dict()
        return self._deserialize_job(job_id, job_data)

    def save(self, job: VideoJob) -> str:
        """
        Save a new VideoJob.

        Args:
            job: VideoJob to save

        Returns:
            ID of the saved job
        """
        # If job has no ID, generate one
        if not job.id:
            doc_ref = self._collection.document()
            job.id = doc_ref.id
        else:
            doc_ref = self._collection.document(job.id)

        # Serialize job to Firestore document
        job_data = self._serialize_job(job)

        # Add timestamps
        now = datetime.datetime.now()
        job_data["created_at"] = now
        job_data["updated_at"] = now

        # Save to Firestore
        doc_ref.set(job_data)
        logger.info(f"Saved job with ID {job.id}")

        return job.id

    def update(self, job: VideoJob) -> bool:
        """
        Update an existing VideoJob.

        Args:
            job: VideoJob to update

        Returns:
            True if successful, False otherwise
        """
        if not job.id:
            logger.error("Cannot update job without ID")
            return False

        doc_ref = self._collection.document(job.id)

        # Check if document exists
        if not doc_ref.get().exists:
            logger.error(f"Job with ID {job.id} does not exist")
            return False

        # Serialize job to Firestore document
        job_data = self._serialize_job(job)

        # Update timestamp
        job_data["updated_at"] = datetime.datetime.now()

        # Update in Firestore
        doc_ref.update(job_data)
        logger.info(f"Updated job with ID {job.id}")

        return True

    def delete(self, job_id: str) -> bool:
        """
        Delete a VideoJob by its ID.

        Args:
            job_id: ID of the job to delete

        Returns:
            True if successful, False otherwise
        """
        doc_ref = self._collection.document(job_id)

        # Check if document exists
        if not doc_ref.get().exists:
            logger.error(f"Job with ID {job_id} does not exist")
            return False

        # Delete from Firestore
        doc_ref.delete()
        logger.info(f"Deleted job with ID {job_id}")

        return True

    def get_jobs_by_status(self, status: ProcessingStatus) -> List[VideoJob]:
        """
        Retrieve jobs with a specific status.

        Args:
            status: Status to filter by

        Returns:
            List of VideoJob with the specified status
        """
        query = self._collection.where(filter=FieldFilter("status", "==", status.value))
        docs = query.stream()

        jobs = []
        for doc in docs:
            job_id = doc.id
            job_data = doc.to_dict()
            job = self._deserialize_job(job_id, job_data)
            jobs.append(job)

        logger.info(f"Retrieved {len(jobs)} jobs with status {status}")
        return jobs

    def get_pending_jobs(self) -> List[VideoJob]:
        """
        Retrieve all pending jobs.

        Returns:
            List of VideoJob with status PENDING
        """
        return self.get_jobs_by_status(ProcessingStatus.PENDING)

    def update_job_status(
        self, job_id: str, status: ProcessingStatus, error: Optional[str] = None
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
        doc_ref = self._collection.document(job_id)

        # Check if document exists
        if not doc_ref.get().exists:
            logger.error(f"Job with ID {job_id} does not exist")
            return False

        # Prepare update data
        update_data = {"status": status.value, "updated_at": datetime.datetime.now()}

        # Add error message if provided
        if error and status == ProcessingStatus.FAILED:
            update_data["error"] = error

        # Update in Firestore
        doc_ref.update(update_data)
        logger.info(f"Updated status of job {job_id} to {status}")

        return True

    def _serialize_job(self, job: VideoJob) -> Dict[str, Any]:
        """
        Serialize a VideoJob to a Firestore document.

        Args:
            job: VideoJob to serialize

        Returns:
            Dictionary representation of the job
        """
        video_data = {
            "id": job.video.id,
            "file_path": job.video.file_path,
            "duration": job.video.duration,
            "format": job.video.format,
            "resolution": job.video.resolution,
        }

        metadata_data = {
            "title": job.metadata.title,
            "description": job.metadata.description,
            "tags": job.metadata.tags,
            "show_notes": job.metadata.show_notes,
            "thumbnail_url": job.metadata.thumbnail_url,
            "transcript": job.metadata.transcript,
            "transcript_url": job.metadata.transcript_url,
            "subtitle_urls": job.metadata.subtitle_urls,
        }

        job_data = {
            "status": job.status.value,
            "error": job.error,
            "video": video_data,
            "metadata": metadata_data,
            "processing_stages": job.processing_stages,
            "created_at": job.created_at or datetime.datetime.now(),
            "updated_at": job.updated_at or datetime.datetime.now(),
        }

        return job_data

    def _deserialize_job(self, job_id: str, job_data: Dict[str, Any]) -> VideoJob:
        """
        Deserialize a Firestore document to a VideoJob.

        Args:
            job_id: ID of the job
            job_data: Dictionary representation of the job

        Returns:
            Deserialized VideoJob
        """
        # Create Video object
        video_data = job_data.get("video", {})
        video = Video(
            id=video_data.get("id", ""),
            file_path=video_data.get("file_path", ""),
            duration=video_data.get("duration", 0),
            format=video_data.get("format", "unknown"),
            resolution=video_data.get("resolution", (0, 0)),
        )

        # Create VideoMetadata object
        metadata_data = job_data.get("metadata", {})
        metadata = VideoMetadata(
            title=metadata_data.get("title", ""),
            description=metadata_data.get("description", ""),
            tags=metadata_data.get("tags", []),
            show_notes=metadata_data.get("show_notes", ""),
            thumbnail_url=metadata_data.get("thumbnail_url", ""),
            transcript=metadata_data.get("transcript", ""),
            transcript_url=metadata_data.get("transcript_url", ""),
            subtitle_urls=metadata_data.get("subtitle_urls", {}),
        )

        # Create VideoJob object
        job = VideoJob(
            id=job_id,
            video=video,
            metadata=metadata,
            status=ProcessingStatus(
                job_data.get("status", ProcessingStatus.PENDING.value)
            ),
            error=job_data.get("error", ""),
            processing_stages=job_data.get("processing_stages", {}),
            created_at=job_data.get("created_at"),
            updated_at=job_data.get("updated_at"),
        )

        return job
