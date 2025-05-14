"""
Unit tests for the Video domain model.
"""

from datetime import datetime

from video_processor.domain.models.video import Video


def test_video_creation():
    """Test that a Video object can be created with required attributes."""
    video = Video(
        id="test123",
        file_path="/path/to/video.mp4",
        file_name="video.mp4",
    )
    assert video.id == "test123"
    assert video.file_path == "/path/to/video.mp4"
    assert video.file_name == "video.mp4"
    assert video.created_at is not None
    assert isinstance(video.created_at, datetime)


def test_video_resolution():
    """Test the resolution property."""
    # Without dimensions
    video = Video(
        id="test123",
        file_path="/path/to/video.mp4",
        file_name="video.mp4",
    )
    assert video.resolution is None

    # With dimensions
    video = Video(
        id="test123",
        file_path="/path/to/video.mp4",
        file_name="video.mp4",
        width=1920,
        height=1080,
    )
    assert video.resolution == (1920, 1080)


def test_get_thumbnail_time():
    """Test thumbnail time calculation."""
    # Without duration
    video = Video(
        id="test123",
        file_path="/path/to/video.mp4",
        file_name="video.mp4",
    )
    assert video.get_thumbnail_time() == 0

    # With duration
    video = Video(
        id="test123",
        file_path="/path/to/video.mp4",
        file_name="video.mp4",
        duration=100.0,
    )
    assert video.get_thumbnail_time() == 20.0  # 20% of duration

    # Very short video
    video = Video(
        id="test123",
        file_path="/path/to/video.mp4",
        file_name="video.mp4",
        duration=3.0,
    )
    assert video.get_thumbnail_time() == 0.6  # 20% of 3 seconds


def test_get_file_extension():
    """Test file extension extraction."""
    video = Video(
        id="test123",
        file_path="/path/to/video.mp4",
        file_name="video.mp4",
    )
    assert video.get_file_extension() == "mp4"

    # No extension
    video = Video(
        id="test123",
        file_path="/path/to/video",
        file_name="video",
    )
    assert video.get_file_extension() == ""


def test_is_valid_video():
    """Test video validation based on extension."""
    # Valid extensions
    for ext in ["mp4", "mov", "avi", "mkv", "webm"]:
        video = Video(
            id="test123",
            file_path=f"/path/to/video.{ext}",
            file_name=f"video.{ext}",
        )
        assert video.is_valid_video() is True

    # Invalid extension
    video = Video(
        id="test123",
        file_path="/path/to/video.txt",
        file_name="video.txt",
    )
    assert video.is_valid_video() is False


def test_to_dict():
    """Test conversion to dictionary."""
    video = Video(
        id="test123",
        file_path="/path/to/video.mp4",
        file_name="video.mp4",
        file_size=1024,
        file_format="mp4",
        duration=60.0,
        width=1920,
        height=1080,
        bucket_name="my-bucket",
    )
    video_dict = video.to_dict()

    assert video_dict["id"] == "test123"
    assert video_dict["file_path"] == "/path/to/video.mp4"
    assert video_dict["file_name"] == "video.mp4"
    assert video_dict["file_size"] == 1024
    assert video_dict["file_format"] == "mp4"
    assert video_dict["duration"] == 60.0
    assert video_dict["width"] == 1920
    assert video_dict["height"] == 1080
    assert video_dict["bucket_name"] == "my-bucket"
    assert isinstance(video_dict["created_at"], str)


def test_from_dict():
    """Test creation from dictionary."""
    now = datetime.now()
    video_dict = {
        "id": "test123",
        "file_path": "/path/to/video.mp4",
        "file_name": "video.mp4",
        "file_size": 1024,
        "file_format": "mp4",
        "duration": 60.0,
        "width": 1920,
        "height": 1080,
        "created_at": now.isoformat(),
        "bucket_name": "my-bucket",
    }

    video = Video.from_dict(video_dict)

    assert video.id == "test123"
    assert video.file_path == "/path/to/video.mp4"
    assert video.file_name == "video.mp4"
    assert video.file_size == 1024
    assert video.file_format == "mp4"
    assert video.duration == 60.0
    assert video.width == 1920
    assert video.height == 1080
    assert video.bucket_name == "my-bucket"
    assert isinstance(video.created_at, datetime)
