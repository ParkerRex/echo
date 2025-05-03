"""
Unit tests for the Video domain model.
"""

import unittest
from datetime import datetime
from uuid import uuid4

from video_processor.domain.models.video import Video


class TestVideo(unittest.TestCase):
    """Test cases for the Video domain model."""

    def setUp(self):
        """Set up test data."""
        self.video_id = str(uuid4())
        self.video = Video(
            id=self.video_id,
            file_path="/path/to/videos/test_video.mp4",
            file_name="test_video.mp4",
            file_size=1024000,
            file_format="mp4",
            duration=120.5,
            width=1920,
            height=1080,
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            bucket_name="test-bucket",
        )

    def test_init(self):
        """Test video initialization."""
        self.assertEqual(self.video.id, self.video_id)
        self.assertEqual(self.video.file_path, "/path/to/videos/test_video.mp4")
        self.assertEqual(self.video.file_name, "test_video.mp4")
        self.assertEqual(self.video.file_size, 1024000)
        self.assertEqual(self.video.file_format, "mp4")
        self.assertEqual(self.video.duration, 120.5)
        self.assertEqual(self.video.width, 1920)
        self.assertEqual(self.video.height, 1080)
        self.assertEqual(self.video.created_at, datetime(2023, 1, 1, 12, 0, 0))
        self.assertEqual(self.video.bucket_name, "test-bucket")

    def test_post_init_sets_created_at_if_none(self):
        """Test __post_init__ sets created_at if not provided."""
        video = Video(
            id=str(uuid4()),
            file_path="/path/to/videos/test_video.mp4",
            file_name="test_video.mp4",
        )
        self.assertIsNotNone(video.created_at)
        self.assertIsInstance(video.created_at, datetime)

    def test_resolution_property(self):
        """Test resolution property returns width x height tuple."""
        self.assertEqual(self.video.resolution, (1920, 1080))

        # Test with missing dimensions
        video_no_dimensions = Video(
            id=str(uuid4()),
            file_path="/path/to/videos/test_video.mp4",
            file_name="test_video.mp4",
        )
        self.assertIsNone(video_no_dimensions.resolution)

    def test_get_thumbnail_time(self):
        """Test thumbnail time calculation."""
        # Normal case - 20% into the video
        self.assertEqual(self.video.get_thumbnail_time(), 24.1)  # 120.5 * 0.2

        # Test with no duration
        video_no_duration = Video(
            id=str(uuid4()),
            file_path="/path/to/videos/test_video.mp4",
            file_name="test_video.mp4",
        )
        self.assertEqual(video_no_duration.get_thumbnail_time(), 0)

        # Test with very short video
        video_short = Video(
            id=str(uuid4()),
            file_path="/path/to/videos/short.mp4",
            file_name="short.mp4",
            duration=3.0,
        )
        self.assertEqual(video_short.get_thumbnail_time(), 0.6)  # 3.0 * 0.2

    def test_get_file_extension(self):
        """Test file extension extraction."""
        self.assertEqual(self.video.get_file_extension(), "mp4")

        # Test with no extension
        video_no_ext = Video(
            id=str(uuid4()),
            file_path="/path/to/videos/noextension",
            file_name="noextension",
        )
        self.assertEqual(video_no_ext.get_file_extension(), "")

        # Test with upper case extension
        video_upper_ext = Video(
            id=str(uuid4()), file_path="/path/to/videos/test.MOV", file_name="test.MOV"
        )
        self.assertEqual(video_upper_ext.get_file_extension(), "mov")

    def test_is_valid_video(self):
        """Test video validation based on extension."""
        # Valid extensions
        self.assertTrue(self.video.is_valid_video())  # mp4

        video_mov = Video(
            id=str(uuid4()), file_path="/path/to/videos/test.mov", file_name="test.mov"
        )
        self.assertTrue(video_mov.is_valid_video())

        # Invalid extension
        video_invalid = Video(
            id=str(uuid4()), file_path="/path/to/videos/test.txt", file_name="test.txt"
        )
        self.assertFalse(video_invalid.is_valid_video())

        # No extension
        video_no_ext = Video(
            id=str(uuid4()),
            file_path="/path/to/videos/noextension",
            file_name="noextension",
        )
        self.assertFalse(video_no_ext.is_valid_video())

    def test_to_dict(self):
        """Test conversion to dictionary."""
        video_dict = self.video.to_dict()

        self.assertEqual(video_dict["id"], self.video_id)
        self.assertEqual(video_dict["file_path"], "/path/to/videos/test_video.mp4")
        self.assertEqual(video_dict["file_name"], "test_video.mp4")
        self.assertEqual(video_dict["file_size"], 1024000)
        self.assertEqual(video_dict["file_format"], "mp4")
        self.assertEqual(video_dict["duration"], 120.5)
        self.assertEqual(video_dict["width"], 1920)
        self.assertEqual(video_dict["height"], 1080)
        self.assertEqual(video_dict["created_at"], "2023-01-01T12:00:00")
        self.assertEqual(video_dict["bucket_name"], "test-bucket")

    def test_from_dict(self):
        """Test creation from dictionary."""
        video_dict = {
            "id": self.video_id,
            "file_path": "/path/to/videos/test_video.mp4",
            "file_name": "test_video.mp4",
            "file_size": 1024000,
            "file_format": "mp4",
            "duration": 120.5,
            "width": 1920,
            "height": 1080,
            "created_at": "2023-01-01T12:00:00",
            "bucket_name": "test-bucket",
        }

        video = Video.from_dict(video_dict)

        self.assertEqual(video.id, self.video_id)
        self.assertEqual(video.file_path, "/path/to/videos/test_video.mp4")
        self.assertEqual(video.file_name, "test_video.mp4")
        self.assertEqual(video.file_size, 1024000)
        self.assertEqual(video.file_format, "mp4")
        self.assertEqual(video.duration, 120.5)
        self.assertEqual(video.width, 1920)
        self.assertEqual(video.height, 1080)
        self.assertEqual(video.created_at.isoformat(), "2023-01-01T12:00:00")
        self.assertEqual(video.bucket_name, "test-bucket")

    def test_from_dict_minimal(self):
        """Test creation from minimal dictionary."""
        video_dict = {
            "id": self.video_id,
            "file_path": "/path/to/videos/test_video.mp4",
            "file_name": "test_video.mp4",
        }

        video = Video.from_dict(video_dict)

        self.assertEqual(video.id, self.video_id)
        self.assertEqual(video.file_path, "/path/to/videos/test_video.mp4")
        self.assertEqual(video.file_name, "test_video.mp4")
        self.assertIsNone(video.file_size)
        self.assertIsNone(video.file_format)
        self.assertIsNone(video.duration)
        self.assertIsNone(video.width)
        self.assertIsNone(video.height)
        self.assertIsNone(video.bucket_name)


if __name__ == "__main__":
    unittest.main()
