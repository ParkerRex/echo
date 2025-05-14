"""
Firestore implementation of the VideoRepositoryInterface.

This module provides a Firestore-backed implementation of the video repository
for storing and retrieving Video entities.
"""

import datetime
import logging
from typing import Any, Dict, List, Optional

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from video_processor.application.interfaces.repositories import VideoRepositoryInterface
from video_processor.domain.models.video import Video

# Configure logger
logger = logging.getLogger(__name__)


class FirestoreVideoRepository(VideoRepositoryInterface):
    """Firestore implementation of the video repository."""

    def __init__(self, project_id: str, collection_name: str = "videos"):
        """
        Initialize the Firestore video repository.

        Args:
            project_id: Google Cloud project ID
            collection_name: Firestore collection name for videos
        """
        self._db = firestore.Client(project=project_id)
        self._collection = self._db.collection(collection_name)
        logger.info(
            f"Initialized FirestoreVideoRepository with collection '{collection_name}'"
        )

    def get_by_id(self, video_id: str) -> Optional[Video]:
        """
        Retrieve a Video by its ID.

        Args:
            video_id: ID of the video to retrieve

        Returns:
            Video if found, None otherwise
        """
        doc_ref = self._collection.document(video_id)
        doc = doc_ref.get()

        if not doc.exists:
            logger.warning(f"Video with ID {video_id} not found")
            return None

        video_data = doc.to_dict()
        return self._deserialize_video(video_id, video_data)

    def save(self, video: Video) -> str:
        """
        Save a new Video.

        Args:
            video: Video to save

        Returns:
            ID of the saved video
        """
        # If video has no ID, generate one
        if not video.id:
            doc_ref = self._collection.document()
            video.id = doc_ref.id
        else:
            doc_ref = self._collection.document(video.id)

        # Serialize video to Firestore document
        video_data = self._serialize_video(video)

        # Add timestamps
        now = datetime.datetime.now()
        if not video.created_at:
            video_data["created_at"] = now
        video_data["updated_at"] = now

        # Save to Firestore
        doc_ref.set(video_data)
        logger.info(f"Saved video with ID {video.id}")

        return video.id

    def update(self, video: Video) -> bool:
        """
        Update an existing Video.

        Args:
            video: Video to update

        Returns:
            True if successful, False otherwise
        """
        if not video.id:
            logger.error("Cannot update video without ID")
            return False

        doc_ref = self._collection.document(video.id)

        # Check if document exists
        if not doc_ref.get().exists:
            logger.error(f"Video with ID {video.id} does not exist")
            return False

        # Serialize video to Firestore document
        video_data = self._serialize_video(video)

        # Update timestamp
        video_data["updated_at"] = datetime.datetime.now()

        # Update in Firestore
        doc_ref.update(video_data)
        logger.info(f"Updated video with ID {video.id}")

        return True

    def delete(self, video_id: str) -> bool:
        """
        Delete a Video by its ID.

        Args:
            video_id: ID of the video to delete

        Returns:
            True if successful, False otherwise
        """
        doc_ref = self._collection.document(video_id)

        # Check if document exists
        if not doc_ref.get().exists:
            logger.error(f"Video with ID {video_id} does not exist")
            return False

        # Delete from Firestore
        doc_ref.delete()
        logger.info(f"Deleted video with ID {video_id}")

        return True

    def get_videos_by_user(self, user_id: str) -> List[Video]:
        """
        Retrieve videos for a specific user.

        Args:
            user_id: ID of the user

        Returns:
            List of Video for the specified user
        """
        query = self._collection.where(filter=FieldFilter("user_id", "==", user_id))
        docs = query.stream()

        videos = []
        for doc in docs:
            video_id = doc.id
            video_data = doc.to_dict()
            video = self._deserialize_video(video_id, video_data)
            videos.append(video)

        logger.info(f"Retrieved {len(videos)} videos for user {user_id}")
        return videos

    def _serialize_video(self, video: Video) -> Dict[str, Any]:
        """
        Serialize a Video to a Firestore document.

        Args:
            video: Video to serialize

        Returns:
            Dictionary representation of the video
        """
        video_data = {
            "file_path": video.file_path,
            "duration": video.duration,
            "format": video.format,
            "resolution": video.resolution,
            "created_at": video.created_at or datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
            "user_id": getattr(video, "user_id", None),  # Optional user ID
        }

        return video_data

    def _deserialize_video(self, video_id: str, video_data: Dict[str, Any]) -> Video:
        """
        Deserialize a Firestore document to a Video.

        Args:
            video_id: ID of the video
            video_data: Dictionary representation of the video

        Returns:
            Deserialized Video
        """
        video = Video(
            id=video_id,
            file_path=video_data.get("file_path", ""),
            duration=video_data.get("duration", 0),
            format=video_data.get("format", "unknown"),
            resolution=video_data.get("resolution", (0, 0)),
        )

        # Set timestamps if available
        video.created_at = video_data.get("created_at")
        video.updated_at = video_data.get("updated_at")

        # Set user_id if available (not in the base model but might be used)
        if "user_id" in video_data:
            video.user_id = video_data["user_id"]

        return video
