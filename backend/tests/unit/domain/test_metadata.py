"""
Unit tests for the VideoMetadata domain model.
"""

from video_processor.domain.models.metadata import VideoMetadata


def test_metadata_creation():
    """Test that a VideoMetadata object can be created with minimal attributes."""
    metadata = VideoMetadata(title="Test Video")

    assert metadata.title == "Test Video"
    assert metadata.description is None
    assert metadata.category_id == "22"  # Default category
    assert metadata.channel == "daily"  # Default channel
    assert metadata.tags == []  # Default empty list
    assert metadata.chapters == []  # Default empty list


def test_metadata_creation_with_attributes():
    """Test that a VideoMetadata object can be created with all attributes."""
    metadata = VideoMetadata(
        title="Test Video",
        description="A test video description",
        keywords="test, video, unit test",
        category_id="10",  # Music
        duration_seconds=300,
        width=1920,
        height=1080,
        channel="main",
        tags=["test", "video"],
        show_notes="These are the show notes",
        thumbnail_url="https://example.com/thumbnail.jpg",
        transcript="This is the transcript",
        chapters=[{"time": "00:00", "title": "Introduction"}],
    )

    assert metadata.title == "Test Video"
    assert metadata.description == "A test video description"
    assert metadata.keywords == "test, video, unit test"
    assert metadata.category_id == "10"
    assert metadata.duration_seconds == 300
    assert metadata.width == 1920
    assert metadata.height == 1080
    assert metadata.channel == "main"
    assert metadata.tags == ["test", "video"]
    assert metadata.show_notes == "These are the show notes"
    assert metadata.thumbnail_url == "https://example.com/thumbnail.jpg"
    assert metadata.transcript == "This is the transcript"
    assert metadata.chapters == [{"time": "00:00", "title": "Introduction"}]


def test_post_init_with_null_collections():
    """Test that __post_init__ initializes collections properly."""
    metadata = VideoMetadata(title="Test Video", tags=None, chapters=None)

    assert metadata.tags == []
    assert metadata.chapters == []


def test_to_dict():
    """Test conversion to dictionary."""
    metadata = VideoMetadata(
        title="Test Video",
        description="A test video description",
        tags=["tag1", "tag2"],
        thumbnail_url="https://example.com/thumbnail.jpg",
    )

    metadata_dict = metadata.to_dict()

    assert metadata_dict["title"] == "Test Video"
    assert metadata_dict["description"] == "A test video description"
    assert metadata_dict["tags"] == ["tag1", "tag2"]
    assert metadata_dict["thumbnail_url"] == "https://example.com/thumbnail.jpg"
    assert metadata_dict["category_id"] == "22"  # Default value
    assert metadata_dict["channel"] == "daily"  # Default value


def test_from_dict():
    """Test creation from dictionary."""
    metadata_dict = {
        "title": "Test Video",
        "description": "A test video description",
        "keywords": "test, video",
        "category_id": "10",
        "duration_seconds": 300,
        "width": 1920,
        "height": 1080,
        "channel": "main",
        "tags": ["tag1", "tag2"],
        "show_notes": "Test show notes",
        "thumbnail_url": "https://example.com/thumbnail.jpg",
        "transcript": "This is the transcript",
        "chapters": [{"time": "00:00", "title": "Introduction"}],
    }

    metadata = VideoMetadata.from_dict(metadata_dict)

    assert metadata.title == "Test Video"
    assert metadata.description == "A test video description"
    assert metadata.keywords == "test, video"
    assert metadata.category_id == "10"
    assert metadata.duration_seconds == 300
    assert metadata.width == 1920
    assert metadata.height == 1080
    assert metadata.channel == "main"
    assert metadata.tags == ["tag1", "tag2"]
    assert metadata.show_notes == "Test show notes"
    assert metadata.thumbnail_url == "https://example.com/thumbnail.jpg"
    assert metadata.transcript == "This is the transcript"
    assert metadata.chapters == [{"time": "00:00", "title": "Introduction"}]


def test_from_dict_with_missing_fields():
    """Test creation from dictionary with missing fields."""
    metadata_dict = {
        "title": "Test Video"
        # All other fields missing
    }

    metadata = VideoMetadata.from_dict(metadata_dict)

    assert metadata.title == "Test Video"
    assert metadata.description is None
    assert metadata.category_id == "22"  # Default
    assert metadata.channel == "daily"  # Default
    assert metadata.tags == []  # Default empty list
    assert metadata.chapters == []  # Default empty list
