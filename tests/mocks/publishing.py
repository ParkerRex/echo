"""
Mock implementation of the publishing interface for testing.
"""

from typing import Dict

from video_processor.application.interfaces.publishing import PublishingInterface


class MockPublishingAdapter(PublishingInterface):
    """
    Mock implementation of PublishingInterface for testing.

    Simulates video publishing operations without making actual API calls.
    """

    def __init__(self):
        """Initialize the mock publishing adapter."""
        self.uploaded_videos = {}  # Dictionary to track "uploaded" videos
        self.deleted_videos = set()  # Set to track "deleted" videos
        self.call_counts = {
            "upload_video": 0,
            "update_metadata": 0,
            "get_upload_status": 0,
            "delete_video": 0,
        }
        self.next_video_id = 1000  # Starting ID for mock uploads

    def upload_video(self, video_file: str, metadata: Dict) -> str:
        """
        Mock uploading a video with metadata.

        Args:
            video_file: Path to the video file
            metadata: Video metadata dictionary

        Returns:
            Platform-specific video ID
        """
        self.call_counts["upload_video"] += 1
        video_id = f"mock-video-{self.next_video_id}"
        self.next_video_id += 1

        # Store the video information
        self.uploaded_videos[video_id] = {
            "file_path": video_file,
            "metadata": metadata.copy(),
            "status": "published",
        }

        return video_id

    def update_metadata(self, video_id: str, metadata: Dict) -> bool:
        """
        Mock updating video metadata.

        Args:
            video_id: ID of the video to update
            metadata: Updated metadata dictionary

        Returns:
            Success status (boolean)
        """
        self.call_counts["update_metadata"] += 1

        if video_id in self.uploaded_videos:
            # Update the stored metadata
            self.uploaded_videos[video_id]["metadata"].update(metadata)
            return True
        return False

    def get_upload_status(self, video_id: str) -> str:
        """
        Mock checking video upload status.

        Args:
            video_id: ID of the video to check

        Returns:
            Status string (published, processing, failed, etc.)
        """
        self.call_counts["get_upload_status"] += 1

        if video_id in self.uploaded_videos:
            return self.uploaded_videos[video_id]["status"]
        return "not_found"

    def delete_video(self, video_id: str) -> bool:
        """
        Mock deleting a video.

        Args:
            video_id: ID of the video to delete

        Returns:
            Success status (boolean)
        """
        self.call_counts["delete_video"] += 1

        if video_id in self.uploaded_videos:
            # Mark as deleted but keep the record for test verification
            self.deleted_videos.add(video_id)
            self.uploaded_videos[video_id]["status"] = "deleted"
            return True
        return False

    def set_upload_status(self, video_id: str, status: str) -> None:
        """
        Set a specific upload status for a video.
        Useful for testing different scenarios.

        Args:
            video_id: ID of the video to update
            status: New status string
        """
        if video_id in self.uploaded_videos:
            self.uploaded_videos[video_id]["status"] = status

    def get_video_count(self) -> int:
        """
        Get the number of uploaded videos.

        Returns:
            Count of uploaded videos
        """
        return len(self.uploaded_videos)

    def get_deleted_count(self) -> int:
        """
        Get the number of deleted videos.

        Returns:
            Count of deleted videos
        """
        return len(self.deleted_videos)

    def reset(self) -> None:
        """Reset all mock state."""
        self.uploaded_videos.clear()
        self.deleted_videos.clear()
        for key in self.call_counts:
            self.call_counts[key] = 0
        self.next_video_id = 1000
