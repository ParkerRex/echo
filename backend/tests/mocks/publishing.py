"""
Mock publishing service adapter for testing.
"""

import time
import uuid
from typing import Dict, Optional

from video_processor.application.interfaces.publishing import PublishingInterface
from video_processor.domain.exceptions import PublishingError


class MockPublishingAdapter(PublishingInterface):
    """
    Mock implementation of PublishingInterface for testing.
    Simulates publishing operations for video platforms like YouTube.
    """

    def __init__(self):
        """Initialize the mock publishing adapter."""
        # Store videos as dictionary with video_id as key
        self.videos: Dict[str, Dict] = {}

        # Store upload statuses
        self.upload_statuses: Dict[str, str] = {}

        # Mock rate limits and errors
        self.fail_next_upload = False
        self.fail_next_update = False
        self.should_delay = False
        self.delay_seconds = 0

    def upload_video(self, video_file: str, metadata: Dict) -> str:
        """
        Simulate uploading a video to a publishing platform.

        Args:
            video_file: Path to video file
            metadata: Video metadata

        Returns:
            Platform-specific video ID

        Raises:
            PublishingError: If upload fails
        """
        if self.fail_next_upload:
            self.fail_next_upload = False
            raise PublishingError("Simulated upload failure")

        if self.should_delay:
            time.sleep(self.delay_seconds)

        # Generate a mock video ID
        video_id = f"video_{str(uuid.uuid4())[:8]}"

        # Store video metadata
        self.videos[video_id] = {
            "file": video_file,
            "metadata": metadata.copy(),
            "upload_time": time.time(),
            "status": "uploaded",
        }

        # Set initial upload status
        self.upload_statuses[video_id] = "processing"

        # Simulate async processing by setting status to complete after a short delay
        # In a real test, you would use a mock timer or manually update this
        self.upload_statuses[video_id] = "complete"

        return video_id

    def update_metadata(self, video_id: str, metadata: Dict) -> bool:
        """
        Simulate updating video metadata.

        Args:
            video_id: Platform-specific video ID
            metadata: Updated metadata

        Returns:
            True if update succeeded, False otherwise

        Raises:
            PublishingError: If update fails
        """
        if self.fail_next_update:
            self.fail_next_update = False
            raise PublishingError("Simulated metadata update failure")

        if self.should_delay:
            time.sleep(self.delay_seconds)

        if video_id not in self.videos:
            raise PublishingError(f"Video not found: {video_id}")

        # Update metadata
        self.videos[video_id]["metadata"].update(metadata)

        return True

    def get_upload_status(self, video_id: str) -> str:
        """
        Get the current upload status of a video.

        Args:
            video_id: Platform-specific video ID

        Returns:
            Status string (e.g., "processing", "complete", "failed")

        Raises:
            PublishingError: If status check fails
        """
        if video_id not in self.upload_statuses:
            raise PublishingError(f"Video not found: {video_id}")

        return self.upload_statuses[video_id]

    def delete_video(self, video_id: str) -> bool:
        """
        Simulate deleting a video from the platform.

        Args:
            video_id: Platform-specific video ID

        Returns:
            True if deletion succeeded, False otherwise

        Raises:
            PublishingError: If deletion fails
        """
        if video_id not in self.videos:
            return False

        # Delete video and status
        del self.videos[video_id]
        if video_id in self.upload_statuses:
            del self.upload_statuses[video_id]

        return True

    # Additional test helper methods

    def set_upload_status(self, video_id: str, status: str) -> None:
        """
        Set the upload status of a video for testing.

        Args:
            video_id: Platform-specific video ID
            status: Status to set
        """
        self.upload_statuses[video_id] = status

    def get_video_metadata(self, video_id: str) -> Optional[Dict]:
        """
        Get the metadata for a video.

        Args:
            video_id: Platform-specific video ID

        Returns:
            Video metadata or None if not found
        """
        if video_id in self.videos:
            return self.videos[video_id]["metadata"]
        return None

    def simulate_error(self, error_type: str) -> None:
        """
        Configure the adapter to simulate an error on the next operation.

        Args:
            error_type: Type of error to simulate ("upload", "update")
        """
        if error_type == "upload":
            self.fail_next_upload = True
        elif error_type == "update":
            self.fail_next_update = True

    def simulate_delay(self, seconds: int) -> None:
        """
        Configure the adapter to add a delay to operations.

        Args:
            seconds: Delay in seconds
        """
        self.should_delay = True
        self.delay_seconds = seconds

    def reset(self) -> None:
        """
        Reset the mock adapter to its initial state.
        """
        self.videos.clear()
        self.upload_statuses.clear()
        self.fail_next_upload = False
        self.fail_next_update = False
        self.should_delay = False
        self.delay_seconds = 0
