"""
Unit tests for the VideoMetadata domain model.
"""

import unittest

from video_processor.domain.models.metadata import VideoMetadata


class TestVideoMetadata(unittest.TestCase):
    """Test cases for the VideoMetadata domain model."""

    def setUp(self):
        """Set up test data."""
        self.metadata = VideoMetadata(
            title="Test Video Title",
            description="This is a test video description",
            keywords="test,video,metadata",
            category_id="28",  # Science & Technology
            duration_seconds=300,
            width=1920,
            height=1080,
            channel="main",
            tags=["test", "video", "metadata"],
            show_notes="These are the show notes for the test video",
            thumbnail_url="https://example.com/thumbnail.jpg",
            transcript="This is the transcript text for the test video",
            chapters=[
                {"time": "00:00", "title": "Introduction"},
                {"time": "01:30", "title": "Main Content"},
                {"time": "04:00", "title": "Conclusion"},
            ],
        )

    def test_init(self):
        """Test metadata initialization."""
        self.assertEqual(self.metadata.title, "Test Video Title")
        self.assertEqual(self.metadata.description, "This is a test video description")
        self.assertEqual(self.metadata.keywords, "test,video,metadata")
        self.assertEqual(self.metadata.category_id, "28")
        self.assertEqual(self.metadata.duration_seconds, 300)
        self.assertEqual(self.metadata.width, 1920)
        self.assertEqual(self.metadata.height, 1080)
        self.assertEqual(self.metadata.channel, "main")
        self.assertEqual(self.metadata.tags, ["test", "video", "metadata"])
        self.assertEqual(
            self.metadata.show_notes, "These are the show notes for the test video"
        )
        self.assertEqual(
            self.metadata.thumbnail_url, "https://example.com/thumbnail.jpg"
        )
        self.assertEqual(
            self.metadata.transcript, "This is the transcript text for the test video"
        )
        self.assertEqual(len(self.metadata.chapters), 3)
        self.assertEqual(self.metadata.chapters[0]["time"], "00:00")
        self.assertEqual(self.metadata.chapters[0]["title"], "Introduction")

    def test_post_init_sets_defaults(self):
        """Test __post_init__ sets defaults for collections."""
        # Test with minimal initialization
        metadata = VideoMetadata(title="Minimal Video")

        self.assertEqual(metadata.title, "Minimal Video")
        self.assertIsNone(metadata.description)
        self.assertIsNone(metadata.keywords)
        self.assertEqual(metadata.category_id, "22")  # Default category
        self.assertIsNone(metadata.duration_seconds)
        self.assertIsNone(metadata.width)
        self.assertIsNone(metadata.height)
        self.assertEqual(metadata.channel, "daily")  # Default channel
        self.assertEqual(metadata.tags, [])  # Empty list, not None
        self.assertIsNone(metadata.show_notes)
        self.assertIsNone(metadata.thumbnail_url)
        self.assertIsNone(metadata.transcript)
        self.assertEqual(metadata.chapters, [])  # Empty list, not None

    def test_to_dict(self):
        """Test conversion to dictionary."""
        metadata_dict = self.metadata.to_dict()

        self.assertEqual(metadata_dict["title"], "Test Video Title")
        self.assertEqual(
            metadata_dict["description"], "This is a test video description"
        )
        self.assertEqual(metadata_dict["keywords"], "test,video,metadata")
        self.assertEqual(metadata_dict["category_id"], "28")
        self.assertEqual(metadata_dict["duration_seconds"], 300)
        self.assertEqual(metadata_dict["width"], 1920)
        self.assertEqual(metadata_dict["height"], 1080)
        self.assertEqual(metadata_dict["channel"], "main")
        self.assertEqual(metadata_dict["tags"], ["test", "video", "metadata"])
        self.assertEqual(
            metadata_dict["show_notes"], "These are the show notes for the test video"
        )
        self.assertEqual(
            metadata_dict["thumbnail_url"], "https://example.com/thumbnail.jpg"
        )
        self.assertEqual(
            metadata_dict["transcript"],
            "This is the transcript text for the test video",
        )
        self.assertEqual(
            metadata_dict["chapters"],
            [
                {"time": "00:00", "title": "Introduction"},
                {"time": "01:30", "title": "Main Content"},
                {"time": "04:00", "title": "Conclusion"},
            ],
        )

    def test_from_dict(self):
        """Test creation from dictionary."""
        metadata_dict = {
            "title": "Test Video Title",
            "description": "This is a test video description",
            "keywords": "test,video,metadata",
            "category_id": "28",
            "duration_seconds": 300,
            "width": 1920,
            "height": 1080,
            "channel": "main",
            "tags": ["test", "video", "metadata"],
            "show_notes": "These are the show notes for the test video",
            "thumbnail_url": "https://example.com/thumbnail.jpg",
            "transcript": "This is the transcript text for the test video",
            "chapters": [
                {"time": "00:00", "title": "Introduction"},
                {"time": "01:30", "title": "Main Content"},
                {"time": "04:00", "title": "Conclusion"},
            ],
        }

        metadata = VideoMetadata.from_dict(metadata_dict)

        self.assertEqual(metadata.title, "Test Video Title")
        self.assertEqual(metadata.description, "This is a test video description")
        self.assertEqual(metadata.keywords, "test,video,metadata")
        self.assertEqual(metadata.category_id, "28")
        self.assertEqual(metadata.duration_seconds, 300)
        self.assertEqual(metadata.width, 1920)
        self.assertEqual(metadata.height, 1080)
        self.assertEqual(metadata.channel, "main")
        self.assertEqual(metadata.tags, ["test", "video", "metadata"])
        self.assertEqual(
            metadata.show_notes, "These are the show notes for the test video"
        )
        self.assertEqual(metadata.thumbnail_url, "https://example.com/thumbnail.jpg")
        self.assertEqual(
            metadata.transcript, "This is the transcript text for the test video"
        )
        self.assertEqual(len(metadata.chapters), 3)
        self.assertEqual(metadata.chapters[0]["time"], "00:00")
        self.assertEqual(metadata.chapters[0]["title"], "Introduction")

    def test_from_dict_minimal(self):
        """Test creation from minimal dictionary."""
        metadata_dict = {"title": "Minimal Video Title"}

        metadata = VideoMetadata.from_dict(metadata_dict)

        self.assertEqual(metadata.title, "Minimal Video Title")
        self.assertIsNone(metadata.description)
        self.assertIsNone(metadata.keywords)
        self.assertEqual(metadata.category_id, "22")  # Default category
        self.assertIsNone(metadata.duration_seconds)
        self.assertIsNone(metadata.width)
        self.assertIsNone(metadata.height)
        self.assertEqual(metadata.channel, "daily")  # Default channel
        self.assertEqual(metadata.tags, [])
        self.assertIsNone(metadata.show_notes)
        self.assertIsNone(metadata.thumbnail_url)
        self.assertIsNone(metadata.transcript)
        self.assertEqual(metadata.chapters, [])


if __name__ == "__main__":
    unittest.main()
